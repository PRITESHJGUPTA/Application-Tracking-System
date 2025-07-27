from pdfminer.high_level import extract_text
import re
import spacy
import sqlalchemy
import psycopg2

from skill_list import skill_keywords

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(file_path):
    return extract_text(file_path)

def extract_email(text):
    # Improved regex for email
    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    match = re.search(pattern, text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    # Improved regex for phone numbers (handles various formats)
    pattern = r'(\+?\d{1,3}[\s\-]?)?(\(?\d{3,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}'
    match = re.search(pattern, text)
    return match.group(0) if match else "Not Found"

def extract_name(text):
    doc = nlp(text)
    possible_names = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Allow spaces in names
            if len(ent.text.split()) >= 2 and ent.text.replace(" ", "").isalpha():
                possible_names.append(ent.text)
    if possible_names:
        return possible_names[0]
    # Fallback: first non-contact, non-empty line with at least 2 words
    lines = text.strip().split("\n")
    contact_keywords = ['email', 'contact', 'phone', 'github', 'linkedin', 'resume', '@']
    for line in lines:
        lower_line = line.strip().lower()
        if line.strip() and len(line.split()) >= 2:
            if not any(keyword in lower_line for keyword in contact_keywords):
                return line.strip()
    return "Not Found"

def extract_skills(text, skill_list):
    text = text.lower()
    found_skills = []
    for skill in skill_list:
        skill_lower = skill.lower()
        # Use word boundaries to avoid substring false positives
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text):
            found_skills.append(skill)
    return list(set(found_skills))

def extract_experience(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    experience_entries = []
    in_experience_section = False
    section_titles = ["experience", "internship", "work experience", "professional experience"]

    month_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*'
    date_range_pattern = re.compile(
        rf'{month_pattern}\s+\d{{4}}\s*[-–to]+\s*{month_pattern}\s+\d{{4}}',
        re.IGNORECASE
    )

    pattern1 = re.compile(r'(.+?),\s*(.+?),\s*(' + date_range_pattern.pattern + ')', re.IGNORECASE)
    pattern2 = re.compile(r'(.+?)\s+at\s+(.+?)\s+from\s+(' + date_range_pattern.pattern + ')', re.IGNORECASE)

    for i, line in enumerate(lines):
        lower = line.lower()
        # Detect if entering experience section
        if any(title in lower for title in section_titles):
            in_experience_section = True
            continue
        # Stop reading after too many lines without a match
        if in_experience_section and len(experience_entries) == 0 and line.lower() in section_titles:
            continue
        if in_experience_section and len(line.split()) <= 2:
            in_experience_section = False
            continue
        if in_experience_section:
            # One-liner matches
            match1 = pattern1.match(line)
            match2 = pattern2.match(line)
            if match1:
                title, company, duration = match1.groups()
                experience_entries.append(f"{title.strip()}, {company.strip()}, {duration.strip()}")
            elif match2:
                title, company, duration = match2.groups()
                experience_entries.append(f"{title.strip()}, {company.strip()}, {duration.strip()}")
            # Check for 3-line block
            elif i + 2 < len(lines):
                if date_range_pattern.search(lines[i + 2]):
                    experience_entries.append(f"{line}, {lines[i + 1]}, {lines[i + 2]}")
                    # skip next 2 lines
                    continue
    return experience_entries if experience_entries else ["Not Found"]

if __name__ == '__main__':
    file_path = "sample_resume_02.pdf"
    resume_text = extract_text_from_pdf(file_path)

    name = extract_name(resume_text)
    print("Name :", name)

    phone_number = extract_phone(resume_text)
    print("Phone Number :", phone_number)

    email = extract_email(resume_text)
    print("Email :", email)

    skills = extract_skills(resume_text, skill_keywords)
    print("Skills :", skills)

    experience = extract_experience(resume_text)
    print("Experience :", experience)
