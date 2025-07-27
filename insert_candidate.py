from db_setup import SessionLocal, Candidate
from parse_resume import (
    extract_text_from_pdf,
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    extract_experience
)
from skill_list import skill_keywords

# Path to your resume PDF
file_path = "sample_resume_03.pdf"

# Step 1: Extract text from PDF
text = extract_text_from_pdf(file_path)

# Step 2: Parse the text
name = extract_name(text)
email = extract_email(text)
phone = extract_phone(text)
skills = extract_skills(text, skill_keywords)
experience = extract_experience(text)

# Step 3: Create a DB session
session = SessionLocal()

# Step 4: Create a Candidate object
candidate = Candidate(
    name=name,
    email=email,
    phone=phone,
    skills=skills,
    experience=experience
)

# Step 5: Insert into DB
session.add(candidate)
session.commit()
session.close()

print("✅ Candidate inserted successfully.")
