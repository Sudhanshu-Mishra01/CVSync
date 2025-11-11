# utils.py
import json
import logging
import re
import PyPDF2
from fastapi import UploadFile, HTTPException
from messages import PDF_PARSE_ERROR
from llm import client  # Use the same Groq client

logger = logging.getLogger("utils")

# --- PDF TEXT EXTRACTION ---
def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        reader = PyPDF2.PdfReader(file.file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        logger.info(f"PDF parsed: {file.filename}")
        return text.strip()
    except Exception as e:
        logger.error(f"PDF parse error: {e}")
        raise HTTPException(status_code=400, detail=PDF_PARSE_ERROR)


# --- CANDIDATE INFO EXTRACTION (NEW) ---
EXTRACT_PROMPT = """
You are a resume parser. Extract ONLY:
{
  "candidate_name": str (full name),
  "candidate_email": str (email),
  "total_experience_years": float (total years, e.g. 5.5, 0 if none)
}
If not found, use null.

RESUME:
{resume}
"""

def extract_candidate_info(resume_text: str) -> dict:
    try:
        prompt = EXTRACT_PROMPT.format(resume=resume_text)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=256,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        logger.info("Candidate info extracted via LLM")
        return {
            "candidate_name": data.get("candidate_name"),
            "candidate_email": data.get("candidate_email"),
            "total_experience_years": data.get("total_experience_years")
        }
    except Exception as e:
        logger.warning(f"LLM extraction failed, using regex: {e}")
        # Fallback: regex
        name_match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})", resume_text[:1000])
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
        return {
            "candidate_name": name_match.group(0).strip() if name_match else None,
            "candidate_email": email_match.group(0) if email_match else None,
            "total_experience_years": None
        }


# --- JSON HELPERS ---
def json_list_to_str(data: list) -> str:
    return json.dumps(data or [])

def str_to_json_list(data: str) -> list:
    try:
        return json.loads(data) if data else []
    except:
        return []