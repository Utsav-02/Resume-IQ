import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, get_db
from resume_parser import parse_resume_bytes
from ai_analyser import extract_skills, analyse_gap, improve_resume_bullet
from crud import (
    get_or_create_user, save_resume, save_skills, get_resume,
    get_skills, get_jobs, get_job, add_job, save_match,
    get_matches_for_resume, seed_sample_jobs, delete_job
)

# ── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Resume Analyser & Job Matcher",
    description="Upload your resume, extract skills, and match with jobs using Claude AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    # Seed sample jobs using a direct session
    from database import SessionLocal
    db = SessionLocal()
    try:
        seed_sample_jobs(db)
    finally:
        db.close()


# ── Pydantic Models ───────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: Optional[list] = []
    source_url: Optional[str] = ""


class ImproveRequest(BaseModel):
    bullet_point: str
    job_description: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI Resume Analyser API is running!", "docs": "/docs"}


@app.post("/upload-resume/")
async def upload_resume(
    file: UploadFile = File(...),
    user_name: str = Form(default="Demo User"),
    user_email: str = Form(default="demo@example.com"),
    db: Session = Depends(get_db)
):
    """Upload a resume PDF/DOCX, extract skills using Claude AI, and store in DB."""

    if not file.filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Parse resume text
    raw_text = parse_resume_bytes(file_bytes, file.filename)
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from the file.")

    # Get or create user
    user = get_or_create_user(db, user_name, user_email)

    # Save resume to DB
    resume = save_resume(db, user.id, raw_text, file.filename)

    # Extract skills using Claude AI
    try:
        skills_data = extract_skills(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")

    # Save skills to DB
    save_skills(db, resume.id, skills_data)

    return {
        "resume_id": resume.id,
        "user_id": user.id,
        "file_name": file.filename,
        "skills": skills_data
    }


@app.post("/match-jobs/{resume_id}")
def match_jobs(resume_id: int, db: Session = Depends(get_db)):
    """Match a resume against all jobs in the DB and return ranked results."""

    resume = get_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    skills = get_skills(db, resume_id)
    skill_names = [s.skill_name for s in skills]

    if not skill_names:
        raise HTTPException(status_code=422, detail="No skills found for this resume. Please upload again.")

    jobs = get_jobs(db)
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found in the database.")

    results = []
    for job in jobs:
        try:
            gap = analyse_gap(skill_names, job.title, job.description)
            save_match(db, resume_id, job.id, gap)
            results.append({
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "source_url": job.source_url,
                "match_score": gap.get("match_score", 0),
                "apply_chance": gap.get("apply_chance", "Unknown"),
                "matching_skills": gap.get("matching_skills", []),
                "missing_skills": gap.get("missing_skills", []),
                "keywords_to_add": gap.get("keywords_to_add", []),
                "recommendation": gap.get("recommendation", "")
            })
        except Exception as e:
            results.append({
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "source_url": job.source_url,
                "error": str(e)
            })

    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {"resume_id": resume_id, "total_jobs": len(results), "matches": results}


@app.get("/resume/{resume_id}")
def get_resume_details(resume_id: int, db: Session = Depends(get_db)):
    """Get resume details and extracted skills."""
    resume = get_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    skills = get_skills(db, resume_id)
    return {
        "resume_id": resume.id,
        "file_name": resume.file_name,
        "uploaded_at": resume.uploaded_at,
        "technical_skills": [s.skill_name for s in skills if s.category == "technical"],
        "soft_skills": [s.skill_name for s in skills if s.category == "soft"],
    }


@app.get("/jobs/")
def list_jobs(db: Session = Depends(get_db)):
    """List all jobs in the database."""
    jobs = get_jobs(db)
    return [
        {
            "job_id": j.id,
            "title": j.title,
            "company": j.company,
            "source_url": j.source_url,
            "required_skills": json.loads(j.required_skills) if j.required_skills else []
        }
        for j in jobs
    ]


@app.post("/jobs/")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Add a new job to match resumes against."""
    new_job = add_job(db, job.title, job.company, job.description, job.required_skills, job.source_url)
    return {"job_id": new_job.id, "message": "Job added successfully."}


@app.delete("/jobs/{job_id}")
def remove_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job from the database."""
    job = delete_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"message": f"Job '{job.title}' deleted."}


@app.post("/improve-bullet/")
def improve_bullet(request: ImproveRequest):
    """Use Claude to rewrite a resume bullet point to better match a job."""
    try:
        improved = improve_resume_bullet(request.bullet_point, request.job_description)
        return {"original": request.bullet_point, "improved": improved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/matches/{resume_id}")
def get_saved_matches(resume_id: int, db: Session = Depends(get_db)):
    """Get previously saved match results for a resume."""
    matches = get_matches_for_resume(db, resume_id)
    return [
        {
            "job_id": m.job_id,
            "match_score": m.match_score,
            "missing_skills": json.loads(m.missing_skills) if m.missing_skills else [],
            "keywords_to_add": json.loads(m.keywords_to_add) if m.keywords_to_add else [],
            "recommendation": m.recommendation,
            "matched_at": m.matched_at
        }
        for m in matches
    ]
