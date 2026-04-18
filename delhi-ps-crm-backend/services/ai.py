"""Gemini AI service for complaint classification, ward detection, and multi-category analysis."""

import json
import logging

from google import genai
from google.genai import types

from config import GEMINI_API_KEY
from constants import CATEGORIES

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

PROMPT_TEMPLATE = """You are an AI assistant for Delhi PS-CRM, a civic complaint system for Delhi, India.
Analyze this complaint: "{message}"
Respond ONLY with valid JSON, no markdown:
{{
  "category": "<primary category: Waste Management|Water Supply|Sewage & Drainage|Roads|Electricity|Other>",
  "categories": ["<list of ALL relevant categories from: Waste Management, Water Supply, Sewage & Drainage, Roads, Electricity, Other>"],
  "urgency": "<Low|Medium|High|Critical>",
  "location": "<location mentioned or Not specified>",
  "ward": "<Delhi ward name/number derived from the location, e.g. Rohini Sector 7 -> Rohini West Ward. If ward cannot be determined, return Unknown>",
  "summary": "<one sentence summary>",
  "sentiment": "<Neutral|Frustrated|Angry|Distressed|Polite>"
}}
Rules:
- "category" must be the single most relevant category.
- "categories" must include ALL relevant categories (at least one). For example, a pothole with water leaking -> ["Roads", "Water Supply"].
- "ward" should be the Delhi municipal ward name or number. Use your knowledge of Delhi geography. If unsure, return "Unknown".
"""


async def analyze_complaint(message: str) -> dict:
    """Classify a complaint using Gemini AI and return structured analysis with ward and multi-category support."""
    prompt = PROMPT_TEMPLATE.format(message=message)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        result = json.loads(raw)

        # Validate primary category
        if result.get("category") not in CATEGORIES:
            result["category"] = "Other"

        # Validate categories list
        categories = result.get("categories")
        if not isinstance(categories, list) or not categories:
            result["categories"] = [result["category"]]
        else:
            result["categories"] = [c for c in categories if c in CATEGORIES] or [result["category"]]

        # Ensure ward field exists
        if not result.get("ward"):
            result["ward"] = "Unknown"

        logger.info(
            "AI analysis complete: category=%s, categories=%s, urgency=%s, ward=%s",
            result.get("category"),
            result.get("categories"),
            result.get("urgency"),
            result.get("ward"),
        )
        return result
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Gemini response as JSON: %s", exc)
        return {
            "category": "Other",
            "categories": ["Other"],
            "urgency": "Medium",
            "location": "Not specified",
            "ward": "Unknown",
            "summary": "",
            "sentiment": "Neutral",
        }
    except Exception as exc:
        logger.exception("Gemini AI analysis failed: %s", exc)
        return {
            "category": "Other",
            "categories": ["Other"],
            "urgency": "Medium",
            "location": "Not specified",
            "ward": "Unknown",
            "summary": "",
            "sentiment": "Neutral",
        }


AUDIO_PROMPT = """You are an AI assistant for Delhi PS-CRM.
The attached audio is a citizen complaint in Hindi or English.
First transcribe the audio, then analyze the complaint and respond ONLY with valid JSON:
{
  "transcription": "<full transcription of the audio>",
  "category": "<Waste Management|Water Supply|Sewage & Drainage|Roads|Electricity|Other>",
  "categories": ["<list of all relevant categories>"],
  "urgency": "<Low|Medium|High|Critical>",
  "location": "<location mentioned or Not specified>",
  "ward": "<Delhi ward name or Unknown>",
  "summary": "<one sentence summary in English>",
  "sentiment": "<Neutral|Frustrated|Angry|Distressed|Polite>"
}
"""


async def analyze_audio_complaint(audio_bytes: bytes, mime_type: str) -> dict:
    """Transcribe and analyze an audio complaint using Gemini and return structured JSON."""
    try:
        parts = [
            types.Part.from_text(AUDIO_PROMPT),
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
        ]
        response = client.models.generate_content(model="gemini-2.0-flash", contents=parts)
        raw = (response.text or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        result = json.loads(raw)

        # Validate primary category
        if result.get("category") not in CATEGORIES:
            result["category"] = "Other"

        # Validate categories list
        categories = result.get("categories")
        if not isinstance(categories, list) or not categories:
            result["categories"] = [result["category"]]
        else:
            result["categories"] = [c for c in categories if c in CATEGORIES] or [result["category"]]

        # Ensure ward field exists
        if not result.get("ward"):
            result["ward"] = "Unknown"

        # Ensure transcription exists
        if not result.get("transcription"):
            result["transcription"] = ""

        return result
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Gemini audio response as JSON: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Gemini audio analysis failed: %s", exc)
        raise