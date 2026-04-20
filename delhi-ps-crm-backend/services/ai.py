"""Gemini AI service for complaint classification, ward detection, and multi-category analysis."""

import json
import logging

from google import genai
from google.genai import types

from config import GEMINI_API_KEY
from constants import CATEGORIES, WARD_MAPPINGS

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

PROMPT_TEMPLATE = """You are a civic complaint classifier for Delhi PS-CRM system.
Analyze the citizen's complaint message and extract the following information.
Return ONLY a valid JSON object with no newlines, no markdown, no backticks, no extra text whatsoever.

Classify category as EXACTLY one of these values (case sensitive):
- Waste Management
- Water Supply
- Sewage & Drainage
- Roads
- Electricity
- Other

Classify urgency as EXACTLY one of these values:
- Low
- Medium
- High
- Critical

Classify sentiment as EXACTLY one of these values:
- Neutral
- Frustrated
- Angry
- Urgent

Extract location as a specific area, sector, colony or landmark in Delhi. If no location mentioned, use "Location not specified".
Extract summary as a single sentence under 15 words describing the core issue.
Extract ward as the Delhi ward or zone inferred from the location. If not determinable, use "Unknown".
Extract categories as an array of ALL relevant categories if multiple departments involved. Always include at least one.

The citizen message may be in Hindi, English, Urdu, Punjabi, Haryanvi, Bhojpuri, Hinglish, or any mix. Understand and process all of them.

Return this exact structure:
{{"category":"...","categories":["..."],"urgency":"...","location":"...","ward":"...","summary":"...","sentiment":"..."}}

Complaint message: "{message}"
"""

VALID_SENTIMENTS = ["Neutral", "Frustrated", "Angry", "Urgent"]


def _detect_ward(location: str) -> str:
    """Detect ward from location using comprehensive mappings."""
    if not location or location == "Location not specified":
        return "Unknown"
    
    location_lower = location.lower().strip()
    
    # Direct mapping lookup
    if location_lower in WARD_MAPPINGS:
        return WARD_MAPPINGS[location_lower]
    
    # Partial matching for locations that contain ward names
    for key, ward in WARD_MAPPINGS.items():
        if key in location_lower or location_lower in key:
            return ward
    
    # Check for common Delhi area patterns
    if "sector" in location_lower:
        # Extract sector number and try to match
        for key, ward in WARD_MAPPINGS.items():
            if "sector" in key and key.split()[-1] in location_lower:
                return ward
    
    return "Unknown"


def _enhanced_prompt_with_ward_context(message: str) -> str:
    """Enhance prompt with ward mapping context for better detection."""
    ward_context = "\nDelhi Ward Mappings for reference:\n"
    # Include key ward mappings in the prompt
    sample_wards = list(WARD_MAPPINGS.items())[:20]  # First 20 mappings to keep prompt reasonable
    for location, ward in sample_wards:
        ward_context += f"- {location.title()} -> {ward}\n"
    ward_context += "...and many more locations.\n\n"
    
    base_prompt = """You are a civic complaint classifier for Delhi PS-CRM system.
Analyze the citizen's complaint message and extract the following information.
Return ONLY a valid JSON object with no newlines, no markdown, no backticks, no extra text whatsoever.

Classify category as EXACTLY one of these values (case sensitive):
- Waste Management
- Water Supply
- Sewage & Drainage
- Roads
- Electricity
- Other

Classify urgency as EXACTLY one of these values:
- Low
- Medium
- High
- Critical

Classify sentiment as EXACTLY one of these values:
- Neutral
- Frustrated
- Angry
- Urgent

Extract location as a specific area, sector, colony or landmark in Delhi. If no location mentioned, use "Location not specified".
Extract summary as a single sentence under 15 words describing the core issue.
Extract ward as the Delhi ward or zone inferred from the location. Use the ward mappings above for accurate detection. If not determinable, use "Unknown".
Extract categories as an array of ALL relevant categories if multiple departments involved. Always include at least one.

The citizen message may be in Hindi, English, Urdu, Punjabi, Haryanvi, Bhojpuri, Hinglish, or any mix. Understand and process all of them.

Return this exact structure:
{{"category":"...","categories":["..."],"urgency":"...","location":"...","ward":"...","summary":"...","sentiment":"..."}}

Complaint message: "{message}"
"""
    
    return ward_context + base_prompt


async def analyze_complaint(message: str) -> dict:
    """Classify a complaint using Gemini AI and return structured analysis."""
    prompt = _enhanced_prompt_with_ward_context(message)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", contents=prompt
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

        # Validate sentiment
        if result.get("sentiment") not in VALID_SENTIMENTS:
            result["sentiment"] = "Neutral"

        # Enhanced ward detection using mappings
        location = result.get("location", "Location not specified")
        detected_ward = _detect_ward(location)
        if detected_ward != "Unknown":
            result["ward"] = detected_ward
        elif not result.get("ward"):
            result["ward"] = "Unknown"

        # Ensure location field exists
        if not result.get("location"):
            result["location"] = "Location not specified"

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
            "location": "Location not specified",
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
            "location": "Location not specified",
            "ward": "Unknown",
            "summary": "",
            "sentiment": "Neutral",
        }


AUDIO_PROMPT = """You are a civic complaint classifier for Delhi PS-CRM system.
The attached audio is a citizen complaint. It may be in Hindi, English, Urdu, Punjabi, Haryanvi, Bhojpuri, Hinglish, or any mix.
First transcribe the audio, then analyze the complaint.
Return ONLY a valid JSON object with no newlines, no markdown, no backticks, no extra text whatsoever.

Classify category as EXACTLY one of: Waste Management, Water Supply, Sewage & Drainage, Roads, Electricity, Other
Classify urgency as EXACTLY one of: Low, Medium, High, Critical
Classify sentiment as EXACTLY one of: Neutral, Frustrated, Angry, Urgent
Extract location as a specific area, sector, colony or landmark in Delhi. If no location mentioned, use "Location not specified".
Extract summary as a single sentence under 15 words describing the core issue.
Extract ward as the Delhi ward or zone inferred from the location. If not determinable, use "Unknown".
Extract categories as an array of ALL relevant categories if multiple departments involved.

Return this exact structure:
{"transcription":"...","category":"...","categories":["..."],"urgency":"...","location":"...","ward":"...","summary":"...","sentiment":"..."}
"""


async def analyze_audio_complaint(audio_bytes: bytes, mime_type: str) -> dict:
    """Transcribe and analyze an audio complaint using Gemini and return structured JSON."""
    try:
        parts = [
            types.Part.from_text(AUDIO_PROMPT),
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
        ]
        response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=parts)
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

        # Validate sentiment
        if result.get("sentiment") not in VALID_SENTIMENTS:
            result["sentiment"] = "Neutral"

        # Enhanced ward detection using mappings
        location = result.get("location", "Location not specified")
        detected_ward = _detect_ward(location)
        if detected_ward != "Unknown":
            result["ward"] = detected_ward
        elif not result.get("ward"):
            result["ward"] = "Unknown"

        # Ensure location field exists
        if not result.get("location"):
            result["location"] = "Location not specified"

        # Ensure transcription exists
        if not result.get("transcription"):
            result["transcription"] = ""

        return result
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Gemini audio response as JSON: %s", exc)
        return {
            "transcription": "",
            "category": "Other",
            "categories": ["Other"],
            "urgency": "Medium",
            "location": "Location not specified",
            "ward": "Unknown",
            "summary": "",
            "sentiment": "Neutral",
        }
    except Exception as exc:
        logger.exception("Gemini audio analysis failed: %s", exc)
        return {
            "transcription": "",
            "category": "Other",
            "categories": ["Other"],
            "urgency": "Medium",
            "location": "Location not specified",
            "ward": "Unknown",
            "summary": "",
            "sentiment": "Neutral",
        }