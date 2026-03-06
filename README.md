# 🤖 AI Resume Analyser & Job Matcher

Upload your resume → Extract skills with Claude AI → Match against jobs → See what's missing → Apply smarter.

---

## 🚀 Quick Start (Local)

### 1. Clone & Setup
```bash
git clone <your-repo>
cd ai_resume_analyser

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Set API Key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```
Get your API key from: https://console.anthropic.com

### 3. Run Backend (Terminal 1)
```bash
cd ai_resume_analyser
uvicorn backend.main:app --reload
# API runs at: http://localhost:8000
# Docs at:     http://localhost:8000/docs
```

### 4. Run Frontend (Terminal 2)
```bash
streamlit run frontend/app.py
# Opens at: http://localhost:8501
```

---

## 🐳 Docker (One Command)

```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

---

## 📁 Project Structure

```
ai_resume_analyser/
├── backend/
│   ├── main.py           # FastAPI routes
│   ├── database.py       # SQLAlchemy models + SQLite
│   ├── crud.py           # DB operations
│   ├── resume_parser.py  # PDF/DOCX text extraction
│   └── ai_analyser.py    # Claude AI integration
├── frontend/
│   └── app.py            # Streamlit UI
├── requirements.txt
├── .env.example
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
└── README.md
```

---

## ✨ Features

- Upload PDF or DOCX resume
- Claude AI extracts technical skills, soft skills, experience, education
- Match resume against job descriptions
- See match score (0–100%)
- View missing skills and ATS keywords to add
- Get AI recommendation for each job
- Add custom job listings
- Improve resume bullet points with AI
- SQLite database (swap to PostgreSQL for production)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-resume/` | Upload resume, extract skills |
| POST | `/match-jobs/{resume_id}` | Match resume against all jobs |
| GET | `/resume/{resume_id}` | Get resume details |
| GET | `/jobs/` | List all jobs |
| POST | `/jobs/` | Add a new job |
| DELETE | `/jobs/{job_id}` | Delete a job |
| POST | `/improve-bullet/` | Improve a resume bullet point |

Interactive docs: http://localhost:8000/docs

---

## 🔧 Switch to PostgreSQL

1. Install PostgreSQL
2. Update `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/resume_db
```
3. That's it — SQLAlchemy handles the rest.
