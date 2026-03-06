from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_analyser.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resumes = relationship("Resume", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    raw_text = Column(Text)
    file_name = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="resumes")
    skills = relationship("Skill", back_populates="resume")
    matches = relationship("JobMatch", back_populates="resume")


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    skill_name = Column(String, nullable=False)
    category = Column(String)
    resume = relationship("Resume", back_populates="skills")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String)
    description = Column(Text)
    required_skills = Column(Text)
    source_url = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
    matches = relationship("JobMatch", back_populates="job")


class JobMatch(Base):
    __tablename__ = "job_matches"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_score = Column(Float)
    missing_skills = Column(Text)
    keywords_to_add = Column(Text)
    recommendation = Column(Text)
    matched_at = Column(DateTime, default=datetime.utcnow)
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
