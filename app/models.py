from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_hr: bool = Field(default=True)

    profiles: List["JobProfile"] = Relationship(back_populates="hr")

class JobProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    title: str
    department: str
    location: str
    experience_min_years: int
    experience_max_years: Optional[int] = None
    salary_range: Optional[str] = None
    jd_text: str
    skills_required: str = Field(default="[]")  # JSON list
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    hr_id: int = Field(foreign_key="user.id")

    hr: User = Relationship(back_populates="profiles")
    candidates: List["CandidateResume"] = Relationship(back_populates="profile")

class CandidateResume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    resume_text: str
    profile_id: int = Field(foreign_key="jobprofile.id")
    uploaded_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # ==== NEW FIELDS ====
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    total_experience_years: Optional[float] = None   # e.g. 5.5
    # =====================

    profile: JobProfile = Relationship(back_populates="candidates")
    result: Optional["AnalysisResult"] = Relationship(back_populates="resume")
    
class AnalysisResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    resume_id: int = Field(foreign_key="candidateresume.id")
    match_score: float
    recommendation: str
    strengths: str = Field(default="[]")
    gaps: str = Field(default="[]")
    suggestions: str = Field(default="[]")
    analyzed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    resume: CandidateResume = Relationship(back_populates="result")