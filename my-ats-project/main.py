from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, not_
from typing import List, Optional
import shutil
import os
from pydantic import BaseModel
from db_setup import SessionLocal, Candidate
from parse_resume import (
    extract_text_from_pdf,
    extract_skills,
    extract_experience
)
from skill_list import skill_keywords
from db_setup import Base, engine
app = FastAPI()

#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# ------------------- Pydantic Model -------------------

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    skills: List[str]
    experience: List[str]
    qualification: str
    gender: str
    location_state: str
    location_city: str
    kanaka_employee: bool
    aptitude_status: Optional[str]
    interview_round_1: Optional[str]
    interview_round_2: Optional[str]
    is_selected: bool
    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    aptitude_status: Optional[str] = None
    interview_round_1: Optional[str] = None
    interview_round_2: Optional[str] = None
    is_selected: Optional[bool] = None

# ------------------- Upload Resume Endpoint -------------------

@app.post("/upload_resume", response_model=CandidateResponse)
def upload_resume(
    file: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    qualification: str = Form(...),
    gender: str = Form(...),
    location_state: str = Form(...),
    location_city: str = Form(...),
    kanaka_employee: bool = Form(False)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_text_from_pdf(temp_file_path)
        skills = extract_skills(text, skill_keywords)
        experience = extract_experience(text)

        session = SessionLocal()
        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            skills=skills,
            experience=experience,
            qualification=qualification,
            gender=gender,
            location_state=location_state,
            location_city=location_city,
            kanaka_employee=kanaka_employee,
            aptitude_status="Not Started",
            interview_round_1="Not Started",
            interview_round_2="Not Started"
        )
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        session.close()
        return candidate
    finally:
        os.remove(temp_file_path)

# ------------------- Get Candidates with Filters -------------------

@app.get("/candidates", response_model=List[CandidateResponse])
def get_candidates(
    skill: Optional[str] = Query(None),
    min_experience: Optional[int] = Query(None),
    qualification: Optional[str] = Query(None),
    aptitude_status: Optional[str] = Query(None),
    interview_round_1: Optional[str] = Query(None),
    interview_round_2: Optional[str] = Query(None)
):
    session = SessionLocal()
    query = session.query(Candidate)

    if skill:
        skill = skill.lower()
        query = query.filter(
            func.array_to_string(Candidate.skills, ',').ilike(f'%{skill}%')
        )

    if min_experience:
        query = query.filter(Candidate.experience != None)
        query = query.filter(not_(Candidate.experience.contains(["Not Found"])))
        query = query.filter(func.array_length(Candidate.experience, 1) >= min_experience)

    if qualification:
        query = query.filter(func.lower(Candidate.qualification) == qualification.lower())

    if aptitude_status:
        query = query.filter(Candidate.aptitude_status == aptitude_status)

    if interview_round_1:
        query = query.filter(Candidate.interview_round_1 == interview_round_1)

    if interview_round_2:
        query = query.filter(Candidate.interview_round_2 == interview_round_2)

    results = query.all()
    session.close()
    return results

# ------------------- Update Candidate Status -------------------

@app.put("/candidates/{candidate_id}", response_model=CandidateResponse)
def update_candidate_status(candidate_id: int = Path(...), update: StatusUpdate = None):
    session = SessionLocal()
    candidate = session.get(Candidate, candidate_id)

    if not candidate:
        session.close()
        raise HTTPException(status_code=404, detail="Candidate not found")

    if update.aptitude_status is not None:
        candidate.aptitude_status = update.aptitude_status
    if update.interview_round_1 is not None:
        candidate.interview_round_1 = update.interview_round_1
    if update.interview_round_2 is not None:
        candidate.interview_round_2 = update.interview_round_2
    if update.is_selected is not None:
        candidate.is_selected = update.is_selected
    

    session.commit()
    session.refresh(candidate)
    session.close()
    return candidate

# ------------------- Serve Frontend -------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
def serve_homepage():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/hr", response_class=FileResponse)
def serve_hr_dashboard():
    return FileResponse(os.path.join("static", "hr.html"))
import csv
from fastapi import UploadFile
from io import TextIOWrapper

@app.post("/upload-aptitude-results")
def upload_aptitude_results(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    updated = 0
    session = SessionLocal()

    try:
        contents = file.file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(contents)

        for row in reader:
            email = row.get("email", "").strip().lower()
            result = row.get("result", "").strip()

            candidate = session.query(Candidate).filter(func.lower(Candidate.email) == email).first()
            if candidate:
                candidate.aptitude_status = result
                updated += 1

        session.commit()
        return {"message": "Upload successful", "updated": updated}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"CSV processing failed: {str(e)}")

    finally:
        session.close()
