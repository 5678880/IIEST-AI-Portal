# IIEST Student-Teacher AI Portal

A prototype academic intelligence portal for students and teachers. It connects exams, subject enrollment, class capture, AI tutoring, grading support, analytics, papers, learning resources, and weak-topic revision in one Streamlit + FastAPI based system.

## Project Goal

The project uses AI as academic support, not as a teacher replacement. Teachers stay in control of final academic decisions, while AI helps with repetitive work such as question support, study help, submission organization, grading suggestions, and weak-topic analysis.

## What We Built

### Student Features

- Login and signup.
- Student dashboard with subject enrollment, roll number, semester, section, and academic year.
- Live exam page for teacher-created timed exams.
- BerriBot AI study assistant for typed and voice-based academic help.
- Uploaded-material based tutoring through PDFs, notes, DOCX, TXT, CSV, and images.
- Papers page for question papers and study material.
- Weak subjects / revision page for focused improvement.
- Learning resources page for links, articles, notes, PDFs, and reference material.

### Teacher Features

- Teacher command center.
- Exam builder with subject, subject code, topics, difficulty, question type, duration, deadline, and number of sets.
- Auto exam-set assignment for students.
- Class capture for taught topics, notes, and quick tests.
- Subject roster and enrollment tracking.
- AI grading center for typed assignments, uploaded papers, OCR-assisted extraction, and teacher-reviewed marks.
- Attendance intelligence.
- Analytics dashboard for scores, submissions, weak topics, pass/fail status, and teacher action notes.

### AI Features

- BerriBot tutor for students.
- AI-assisted question generation.
- Question-bank based exam creation.
- Typed assignment grading suggestions.
- Weak-topic feedback and revision suggestions.
- Class capture to concept-check workflow.
- Uploaded-material support.
- Teacher review for important academic decisions.

## Tech Stack

### Frontend

- Streamlit
- Python
- Plotly / Matplotlib
- Browser speech recognition and speech synthesis

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Database

- SQLite for the prototype
- Database file: `assesment_backend/assessment.db`

### File and OCR Support

- PDF extraction with `pypdf` / PyMuPDF
- DOCX extraction with `python-docx`
- OCR support through `pytesseract`

### AI Layer

- Ollama / Llama-style local AI support when available
- Structured fallback responses when the local model is unavailable

## Project Structure

```text
AI_Assessment_Platform/
├── assesment_backend/
│   ├── assessment.db
│   └── app/
│       ├── main.py
│       ├── models.py
│       ├── database.py
│       ├── security.py
│       ├── routes/
│       └── services/
├── assessment_frontend/
│   ├── app.py
│   ├── components/
│   ├── pages/
│   └── services/
├── deploy/
│   └── start.sh
├── requirements.txt
├── runtime.txt
├── render.yaml
└── README.md
```

## How To Run Locally

Open two terminals.

### 1. Start Backend

```bash
cd /Users/shreyakar/Downloads/AI_Assessment_Platform/assesment_backend
/Users/shreyakar/Downloads/AI_Assessment_Platform/.venv-mac/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Backend local URL:

```text
http://127.0.0.1:8001
```

### 2. Start Frontend

```bash
cd /Users/shreyakar/Downloads/AI_Assessment_Platform/assessment_frontend
/Users/shreyakar/Downloads/AI_Assessment_Platform/.venv-mac/bin/python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

Frontend local URL:

```text
http://127.0.0.1:8501
```

For another device on the same Wi-Fi, use the laptop LAN IP:

```bash
ipconfig getifaddr en0
```

Then open:

```text
http://YOUR_LAN_IP:8501
```

Important: `127.0.0.1` only works on the same laptop. For another computer, use the LAN IP.

## How To Make A Public Professor Link

A local link works only while the laptop is on. A link that works anytime on the professor's computer must be deployed to a cloud hosting service.

This project now includes deployment files for a one-service cloud deployment:

```text
requirements.txt
runtime.txt
render.yaml
deploy/start.sh
```

The cloud service starts both parts together:

- FastAPI backend runs internally on `127.0.0.1:8001`.
- Streamlit frontend runs publicly on the cloud service port.
- The professor only receives one public Streamlit link.

### Recommended Deployment: Render

1. Upload this project to GitHub.
2. Go to Render.
3. Create a new Web Service from the GitHub repository.
4. Use these settings:

```text
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: bash deploy/start.sh
```

5. Render will generate a public URL like:

```text
https://iiest-student-teacher-ai-portal.onrender.com
```

That is the link to send to the professor.

Note: Render free services may sleep after inactivity. The first load can take time, but the link does not depend on the laptop being on.

## How The System Works

1. User opens the Streamlit frontend.
2. User logs in or signs up as teacher/student.
3. The frontend sends API-style requests.
4. FastAPI handles authentication, exams, grading, enrollments, analytics, and AI requests.
5. Data is saved in SQLite.
6. AI features use subject, question, uploaded material, or exam context.
7. Results return to the frontend.

## Important Panel Explanation

If asked how this differs from ChatGPT:

> ChatGPT is a general-purpose assistant. This portal is role-aware and course-aware. It connects teachers, students, subjects, exams, submissions, uploaded papers, grading, analytics, and weak-topic revision in one academic workflow.

If asked where login data is stored:

> In this prototype, user details are saved in a local SQLite database. In production, this should move to a secure server database with password hashing and stronger authentication.

If asked why AI is used:

> AI reduces repetitive academic work, generates practice, summarizes material, supports grading, and identifies weak areas. Teachers still control final academic decisions.

## Current Prototype Limitations

- SQLite is local and best for prototype/demo use.
- OCR depends on file quality and may fail on unclear handwriting.
- AI output must be teacher-reviewed.
- Browser voice support depends on browser permissions.
- Free cloud hosting may sleep after inactivity.
- For production, authentication, hosting, database security, and file storage should be upgraded.

## Future Prospects

- Deploy on a cloud server.
- Replace SQLite with PostgreSQL or MySQL.
- Add stronger password hashing and user management.
- Add full coding test execution.
- Add plagiarism checks.
- Improve OCR and scanned-paper workflows.
- Add notification system for deadlines and reminders.
- Add role-based admin panel for college-level deployment.

