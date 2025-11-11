# llm.py
import json
import logging
from groq import Groq
from config import get_settings
from messages import LLM_ERROR

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)  # Export this
logger = logging.getLogger("llm")

PROMPT_TEMPLATE = """
You are an expert HR recruiter. Compare the JOB DESCRIPTION and CANDIDATE RESUME.

Return ONLY valid JSON with:
{
  "match_score": float (0-100),
  "recommendation": str ("Strong Hire" | "Good Fit" | "Needs Review" | "Not Suitable"),
  "strengths": [str],
  "gaps": [str],
  "suggestions": [str]
}

RULES:
- Normalize skills (python3 → Python)
- Be critical but fair
- Use bullet-style strings
- JD and Resume separated by ---

JD:
{jd}

---

RESUME:
{resume}
"""

def analyze_resume(jd: str, resume: str, model: str = "llama3-70b-8192") -> dict:
    try:
        prompt = PROMPT_TEMPLATE.format(jd=jd, resume=resume)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        logger.info("LLM analysis successful")
        return result
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        raise RuntimeError(LLM_ERROR)