from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class JobProfileCreate(BaseModel):
    name: str
    title: str
    department: str
    location: str
    experience_min_years: int
    experience_max_years: Optional[int] = None
    salary_range: Optional[str] = None
    jd_text: str
    skills_required: List[str] = []

class JobProfileOut(JobProfileCreate):
    id: int
    created_at: str

class ResumeUploadResponse(BaseModel):
    resume_id: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    total_experience_years: Optional[float] = None
    match_score: float
    recommendation: str

class AnalysisResultOut(BaseModel):
    id: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    total_experience_years: Optional[float] = None
    match_score: float
    recommendation: str
    strengths: List[str]
    gaps: List[str]
    suggestions: List[str]
    analyzed_at: str