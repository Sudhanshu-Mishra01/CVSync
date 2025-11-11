# schemas.py
from pydantic import BaseModel
from typing import List, Optional
from utils import str_to_json_list  # Import helper

# === JOB PROFILE ===
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


class JobProfileOut(BaseModel):
    id: int
    name: str
    title: str
    department: str
    location: str
    experience_min_years: int
    experience_max_years: Optional[int]
    salary_range: Optional[str]
    jd_text: str
    created_at: str

    # FIX: Convert JSON string → list
    skills_required: List[str]

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if isinstance(self.skills_required, str):
            self.skills_required = str_to_json_list(self.skills_required)


# === RESUME UPLOAD ===
class ResumeUploadResponse(BaseModel):
    resume_id: int
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    total_experience_years: Optional[float] = None
    match_score: float
    recommendation: str


# === ANALYSIS RESULT ===
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

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        self.strengths = str_to_json_list(self.strengths)
        self.gaps = str_to_json_list(self.gaps)
        self.suggestions = str_to_json_list(self.suggestions)