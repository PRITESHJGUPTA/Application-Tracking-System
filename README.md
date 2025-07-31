# 🎯 Application Tracking System 

A full-featured, clean, and lightweight web-based ATS (Applicant Tracking System) designed for HR teams to manage candidate applications, filter by skills and status, and collect resumes through a controlled submission form.

🔗 **Live Site**: [https://application-tracking-system-y8yo.onrender.com](https://application-tracking-system-y8yo.onrender.com)

---

## 📌 Features

- 🔐 **HR Dashboard with Login Protection**
- 🧾 **Candidate Resume Upload** (PDF parsing via NLP)
- ✅ **Form Submission Toggle** (Enable/disable from HR panel)
- 📂 **Auto Resume Parsing**: Name, Email, Phone, Skills, Experience
- 📧 **Automatic Email Confirmation** on resume submission
- 🎛 **Advanced Filters**: Skill, Qualification, Experience, Round Status
- 📊 **CSV Upload** for aptitude test results
- 📥 **Candidate Status Tracking**: Aptitude, Interview 1 & 2, Final Selection

---



## ⚙️ Tech Stack

| Layer            | Tech Used                         |
|------------------|-----------------------------------|
| Backend          | FastAPI + SQLAlchemy              |
| Database         | PostgreSQL (Render-hosted)        |
| Resume Parsing   | pdfminer.six + spaCy NLP          |
| Frontend         | HTML + CSS + JavaScript           |
| Email Service    | Gmail SMTP via `smtplib`          |
| Deployment       | Render (Free Tier)                |

---

## 🚀 Getting Started Locally

### 1. Clone this repo

```bash
git clone https://github.com/your-username/Application-Tracking-System.git
cd Application-Tracking-System
