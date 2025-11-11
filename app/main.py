# main.py
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from fastapi import Depends
from database import get_session, init_db
from models import JobProfile, CandidateResume, AnalysisResult
from schemas import (
    JobProfileCreate, JobProfileOut, JobProfileOut, 
    ResumeUploadResponse, AnalysisResultOut
)
from utils import extract_text_from_pdf, extract_candidate_info, json_list_to_str, str_to_json_list
from llm import analyze_resume
from messages import *

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("api")

# === FASTAPI APP ===
app = FastAPI(
    title="CVSync - AI Resume Screener",
    description="No Auth | Job Profiles | Resume Upload | LLM Grading | Candidate Dashboard",
    version="3.0.0"
)

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("CVSync started. No authentication required.")

# === JOB PROFILES ===
@app.post("/profiles", response_model=JobProfileOut)
def create_job_profile(profile: JobProfileCreate, session: Session = Depends(get_session)):
    if session.exec(select(JobProfile).where(JobProfile.name == profile.name)).first():
        raise HTTPException(status_code=400, detail=PROFILE_EXISTS)

    db_profile = JobProfile(
        **profile.dict(),
        skills_required=json_list_to_str(profile.skills_required)
    )
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    logger.info(f"Profile created: {profile.name}")
    return db_profile


@app.get("/profiles", response_model=List[JobProfileOut])
def list_job_profiles(session: Session = Depends(get_session)):
    return session.exec(select(JobProfile)).all()


@app.get("/profiles/{profile_id}", response_model=JobProfileOut)
def get_job_profile(profile_id: int, session: Session = Depends(get_session)):
    profile = session.get(JobProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)
    return profile


# === RESUME UPLOAD & ANALYSIS ===
@app.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    profile_name: str = Form(...),
    model: str = Form("llama3-70b-8192"),
    session: Session = Depends(get_session)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes allowed")

    # Find profile
    profile = session.exec(
        select(JobProfile).where(JobProfile.name == profile_name)
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)

    # 1. Extract text
    resume_text = extract_text_from_pdf(file)

    # 2. Extract candidate info
    meta = extract_candidate_info(resume_text)

    # 3. Save resume
    candidate = CandidateResume(
        filename=file.filename,
        resume_text=resume_text,
        profile_id=profile.id,
        candidate_name=meta.get("candidate_name"),
        candidate_email=meta.get("candidate_email"),
        total_experience_years=meta.get("total_experience_years")
    )
    session.add(candidate)
    session.commit()
    session.refresh(candidate)

    # 4. Build JD
    skills = ", ".join(str_to_json_list(profile.skills_required))
    jd = f"""
Title: {profile.title}
Experience: {profile.experience_min_years}+ years
Skills: {skills}
Location: {profile.location}

Full JD:
{profile.jd_text}
    """.strip()

    # 5. LLM Analysis
    try:
        result = analyze_resume(jd, resume_text, model)
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        raise HTTPException(status_code=500, detail=LLM_ERROR)

    # 6. Save result
    analysis = AnalysisResult(
        resume_id=candidate.id,
        match_score=result["match_score"],
        recommendation=result["recommendation"],
        strengths=json_list_to_str(result["strengths"]),
        gaps=json_list_to_str(result["gaps"]),
        suggestions=json_list_to_str(result["suggestions"])
    )
    session.add(analysis)
    session.commit()

    logger.info(f"Analyzed: {candidate.candidate_name or file.filename} → {result['match_score']}%")

    return ResumeUploadResponse(
        resume_id=candidate.id,
        candidate_name=candidate.candidate_name,
        candidate_email=candidate.candidate_email,
        total_experience_years=candidate.total_experience_years,
        match_score=result["match_score"],
        recommendation=result["recommendation"]
    )


# === CANDIDATES BY PROFILE ===
@app.get("/profiles/{profile_id}/candidates", response_model=List[AnalysisResultOut])
def get_candidates(
    profile_id: int,
    threshold: Optional[float] = None,
    session: Session = Depends(get_session)
):
    profile = session.get(JobProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)

    query = (
        select(AnalysisResult, CandidateResume)
        .join(CandidateResume)
        .where(CandidateResume.profile_id == profile_id)
    )
    if threshold is not None:
        query = query.where(AnalysisResult.match_score >= threshold)

    results = session.exec(query).all()

    return [
        AnalysisResultOut(
            id=analysis.id,
            candidate_name=resume.candidate_name,
            candidate_email=resume.candidate_email,
            total_experience_years=resume.total_experience_years,
            match_score=analysis.match_score,
            recommendation=analysis.recommendation,
            strengths=str_to_json_list(analysis.strengths),
            gaps=str_to_json_list(analysis.gaps),
            suggestions=str_to_json_list(analysis.suggestions),
            analyzed_at=analysis.analyzed_at
        )
        for analysis, resume in results
    ]


# === HEALTH ===
@app.get("/health")
def health():
    return {"status": "running", "time": datetime.utcnow().isoformat() + "Z"}