import json
from sqlalchemy.orm import Session
from database import User, Resume, Skill, Job, JobMatch


# ── User ──────────────────────────────────────────────────────────────────────

def get_or_create_user(db: Session, name: str, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(name=name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()


# ── Resume ────────────────────────────────────────────────────────────────────

def save_resume(db: Session, user_id: int, raw_text: str, file_name: str) -> Resume:
    resume = Resume(user_id=user_id, raw_text=raw_text, file_name=file_name)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get_resume(db: Session, resume_id: int) -> Resume:
    return db.query(Resume).filter(Resume.id == resume_id).first()


def get_user_resumes(db: Session, user_id: int):
    return db.query(Resume).filter(Resume.user_id == user_id).all()


# ── Skills ────────────────────────────────────────────────────────────────────

def save_skills(db: Session, resume_id: int, skills_data: dict):
    # Delete existing skills for this resume
    db.query(Skill).filter(Skill.resume_id == resume_id).delete()

    for skill in skills_data.get("technical_skills", []):
        db.add(Skill(resume_id=resume_id, skill_name=skill, category="technical"))
    for skill in skills_data.get("soft_skills", []):
        db.add(Skill(resume_id=resume_id, skill_name=skill, category="soft"))

    db.commit()


def get_skills(db: Session, resume_id: int):
    return db.query(Skill).filter(Skill.resume_id == resume_id).all()


# ── Jobs ──────────────────────────────────────────────────────────────────────

def add_job(db: Session, title: str, company: str, description: str,
            required_skills: list = None, source_url: str = "") -> Job:
    job = Job(
        title=title,
        company=company,
        description=description,
        required_skills=json.dumps(required_skills or []),
        source_url=source_url
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_jobs(db: Session):
    return db.query(Job).all()


def get_job(db: Session, job_id: int) -> Job:
    return db.query(Job).filter(Job.id == job_id).first()


def delete_job(db: Session, job_id: int):
    job = get_job(db, job_id)
    if job:
        db.delete(job)
        db.commit()
    return job


# ── Job Matches ───────────────────────────────────────────────────────────────

def save_match(db: Session, resume_id: int, job_id: int, gap_data: dict) -> JobMatch:
    # Remove old match for same resume+job
    db.query(JobMatch).filter(
        JobMatch.resume_id == resume_id,
        JobMatch.job_id == job_id
    ).delete()

    match = JobMatch(
        resume_id=resume_id,
        job_id=job_id,
        match_score=gap_data.get("match_score", 0.0),
        missing_skills=json.dumps(gap_data.get("missing_skills", [])),
        keywords_to_add=json.dumps(gap_data.get("keywords_to_add", [])),
        recommendation=gap_data.get("recommendation", "")
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def get_matches_for_resume(db: Session, resume_id: int):
    return db.query(JobMatch).filter(JobMatch.resume_id == resume_id).all()


def seed_sample_jobs(db: Session):
    """Add sample jobs if the jobs table is empty."""
    if db.query(Job).count() > 0:
        return

    sample_jobs = [
        {
            "title": "Python Backend Developer",
            "company": "TechCorp",
            "description": """We are looking for a skilled Python Backend Developer to join our team.
Requirements:
- 3+ years of Python development experience
- Strong knowledge of FastAPI or Django REST Framework
- Experience with PostgreSQL and Redis
- Familiarity with Docker and Kubernetes
- Understanding of REST APIs and microservices
- Experience with AWS or GCP cloud platforms
- Knowledge of CI/CD pipelines
- Git version control
- Unit testing with pytest
- Good communication and teamwork skills""",
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Redis", "pytest"],
            "source_url": "https://example.com/jobs/python-backend"
        },
        {
            "title": "Data Scientist",
            "company": "DataViz Inc",
            "description": """Seeking a Data Scientist to develop machine learning models and drive insights.
Requirements:
- 2+ years of data science experience
- Proficiency in Python and R
- Experience with scikit-learn, TensorFlow or PyTorch
- Strong SQL skills for data extraction
- Data visualization with Tableau or Power BI
- Statistical analysis and hypothesis testing
- Experience with Pandas, NumPy
- Knowledge of NLP techniques
- Jupyter notebooks
- Excellent problem-solving skills""",
            "required_skills": ["Python", "Machine Learning", "SQL", "TensorFlow", "Pandas", "NLP"],
            "source_url": "https://example.com/jobs/data-scientist"
        },
        {
            "title": "Full Stack Developer",
            "company": "StartupXYZ",
            "description": """Join our fast-growing startup as a Full Stack Developer.
Requirements:
- React.js or Vue.js frontend experience
- Node.js or Python backend
- RESTful API design
- MongoDB or PostgreSQL
- HTML5, CSS3, JavaScript ES6+
- Git and GitHub
- Agile/Scrum methodology
- Basic DevOps knowledge
- Strong attention to detail
- Ability to work in a fast-paced environment""",
            "required_skills": ["React", "Node.js", "JavaScript", "PostgreSQL", "REST API", "Git"],
            "source_url": "https://example.com/jobs/fullstack"
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudSystems Ltd",
            "description": """We need a DevOps Engineer to manage our cloud infrastructure.
Requirements:
- Strong experience with AWS, Azure, or GCP
- Kubernetes and Docker container orchestration
- Terraform for infrastructure as code
- CI/CD pipeline setup (Jenkins, GitHub Actions)
- Linux system administration
- Monitoring with Prometheus and Grafana
- Scripting in Python or Bash
- Security best practices
- Networking fundamentals
- On-call support experience""",
            "required_skills": ["AWS", "Kubernetes", "Docker", "Terraform", "Linux", "CI/CD", "Python"],
            "source_url": "https://example.com/jobs/devops"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations",
            "description": """Looking for an ML Engineer to build and deploy production ML systems.
Requirements:
- Strong Python skills
- Experience with PyTorch or TensorFlow
- MLOps experience (MLflow, Kubeflow)
- Data pipeline development
- Model deployment and serving (FastAPI, Flask)
- Cloud platforms (AWS SageMaker or GCP Vertex AI)
- Distributed computing (Spark)
- SQL and NoSQL databases
- Version control with Git
- Research background is a plus""",
            "required_skills": ["Python", "PyTorch", "MLOps", "FastAPI", "AWS", "Spark", "SQL"],
            "source_url": "https://example.com/jobs/ml-engineer"
        }
    ]

    for job_data in sample_jobs:
        add_job(
            db,
            title=job_data["title"],
            company=job_data["company"],
            description=job_data["description"],
            required_skills=job_data["required_skills"],
            source_url=job_data["source_url"]
        )
