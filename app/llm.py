# llm.py
import json
import logging
from groq import Groq
from config import get_settings
from messages import LLM_ERROR

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)
logger = logging.getLogger("llm")

PROMPT_TEMPLATE = """
You are an expert HR. Compare JD and RESUME.

Return ONLY JSON:
{
  "match_score": float (0-100),
  "recommendation": str ("Strong Hire" | "Good Fit" | "Needs Review" | "Not Suitable"),
  "strengths": [str],
  "gaps": [str],
  "suggestions": [str]
}

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