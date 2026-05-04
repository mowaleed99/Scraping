import json
import structlog
from groq import Groq
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

settings = get_settings()
# Initialize groq client only if key is present
client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

def safe_parse(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        logger.warning("json_parse_failed", raw_text=text)
        return {
            "type": "irrelevant",
            "item": None,
            "location": None,
            "contact": None
        }

def analyze_post(text: str) -> dict:
    """
    Analyzes a raw Facebook post and extracts structured data using Groq.
    
    Returns a dictionary with:
    - type: "lost" | "found" | "irrelevant"
    - item: string or null
    - location: string or null
    - contact: string or null
    """
    if not client:
        logger.error("groq_client_not_initialized")
        return {"type": "irrelevant", "item": None, "location": None, "contact": None}
        
    prompt = f"""
Return ONLY valid JSON. No explanation. No extra text.

Post:
{text}

Output format:
{{
  "type": "lost" | "found" | "irrelevant",
  "item": "string or null",
  "location": "string or null",
  "contact": "string or null"
}}
"""
    try:
        completion = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=settings.llm_temperature,
            response_format={"type": "json_object"},
            timeout=25.0
        )
        result = completion.choices[0].message.content
        return safe_parse(result)
    except Exception as e:
        logger.error("groq_analysis_failed", error=str(e))
        return {"type": "irrelevant", "item": None, "location": None, "contact": None}
