"""Handler for complaint filing -- collects complaint text or voice, detects duplicates, and runs AI analysis."""

import asyncio
import logging
import time
from typing import Optional

import httpx

from config import supabase
from config import WHATSAPP_TOKEN
from services.ai import analyze_audio_complaint, analyze_complaint
from services.whatsapp import send_message

logger = logging.getLogger(__name__)


def _ticket_display(complaint_id) -> str:
    """Format a complaint UUID into a short human-readable ticket ID."""
    return str(complaint_id)[:8].upper()


def _format_confirmation(draft: dict) -> str:
    """Format the AI-analyzed complaint draft into a confirmation message."""
    return (
        "Your complaint has been recorded. Please verify the details below:\n\n"
        f"Category : {draft['category']}\n"
        f"Urgency  : {draft['urgency']}\n"
        f"Location : {draft['location']}\n"
        f"Ward     : {draft.get('ward', 'Unknown')}\n"
        f"Summary  : {draft['summary']}\n\n"
        "Reply YES to submit, NO to cancel, or send a photo as evidence."
    )


def _format_voice_confirmation(draft: dict) -> str:
    """Format the voice-note confirmation message including transcription."""
    return (
        "Voice note received. Here is what I understood:\n\n"
        f"Transcription: {draft.get('transcription', '')}\n\n"
        f"Category : {draft['category']}\n"
        f"Urgency  : {draft['urgency']}\n"
        f"Location : {draft['location']}\n"
        f"Ward     : {draft.get('ward', 'Unknown')}\n"
        f"Summary  : {draft['summary']}\n\n"
        "Reply YES to submit, NO to cancel, or send a photo as evidence."
    )


def _format_duplicate(existing: dict, ticket_id: str) -> str:
    """Format the duplicate complaint notification message."""
    return (
        "A similar complaint has already been filed.\n\n"
        f"Ticket   : {ticket_id}\n"
        f"Category : {existing.get('category', 'N/A')}\n"
        f"Location : {existing.get('location', 'N/A')}\n"
        f"Status   : {existing.get('status', 'open')}\n\n"
        "Your complaint is already being tracked. "
        "Send NEW to file a different complaint or STATUS to check updates."
    )


async def handle_filing(
    whatsapp_number: str,
    message_text: str,
    *,
    message_type: str = "text",
    media_id: Optional[str] = None,
) -> None:
    """Process the user's complaint description, check for duplicates, and generate an AI-analyzed draft."""
    is_voice = False
    text = (message_text or "").strip()

    if message_type == "audio":
        if not media_id or not WHATSAPP_TOKEN:
            await send_message(
                whatsapp_number,
                "Sorry, I could not process your voice note. Please type your complaint instead.",
            )
            return

        max_retries = 3
        retry_delay = 1
        for attempt in range(max_retries):
            try:
                audio_bytes, mime_type = await _download_whatsapp_audio(media_id)
                mime_type = mime_type or "audio/ogg"
                analysis = await analyze_audio_complaint(audio_bytes, mime_type)
                transcription = (analysis.get("transcription") or "").strip()
                if not transcription:
                    raise ValueError("Empty transcription")
                text = transcription
                is_voice = True
                break
            except httpx.RequestError as exc:
                logger.error("Network error downloading audio for %s: %s", whatsapp_number, exc)
                await send_message(
                    whatsapp_number,
                    "Sorry, I could not download your voice note. Please try again or type your complaint.",
                )
                retry_delay *= 2
                await asyncio.sleep(retry_delay)
            except httpx.HTTPStatusError as exc:
                logger.error("HTTP error downloading audio for %s: %s", whatsapp_number, exc)
                await send_message(
                    whatsapp_number,
                    "Sorry, I could not download your voice note. Please try again or type your complaint.",
                )
                retry_delay *= 2
                await asyncio.sleep(retry_delay)
            except ValueError as exc:
                logger.error("Invalid audio data for %s: %s", whatsapp_number, exc)
                await send_message(
                    whatsapp_number,
                    "Sorry, your voice note format is not supported. Please type your complaint.",
                )
                break
            except asyncio.TimeoutError as exc:
                logger.error("Timeout error downloading audio for %s: %s", whatsapp_number, exc)
                await send_message(
                    whatsapp_number,
                    "Sorry, I could not download your voice note. Please try again or type your complaint.",
                )
                retry_delay *= 2
                await asyncio.sleep(retry_delay)
            except Exception as exc:
                logger.exception("Unexpected error processing audio for %s", whatsapp_number)
                await send_message(
                    whatsapp_number,
                    "Sorry, I could not process your voice note. Please type your complaint instead.",
                )
                break
        else:
            logger.error("Failed to download audio after %d retries", max_retries)
            await send_message(
                whatsapp_number,
                "Sorry, I could not download your voice note. Please try again or type your complaint.",
            )
            return

    elif message_type == "text":
        # Check for empty message or command keywords
        command_keywords = ["new", "status", "help", "menu", "hello", "hi", "start", "yes", "no"]
        text_lower = text.lower().strip()
        
        if not text or text_lower in command_keywords or len(text) < 10:
            await send_message(
                whatsapp_number, 
                "Please describe your complaint. Include your location for faster resolution."
            )
            return
        logger.info("Analyzing complaint from %s", whatsapp_number)
        analysis = await analyze_complaint(text)
    else:
        await send_message(
            whatsapp_number,
            "Please describe your issue in a text message or send a voice note.",
        )
        return

    category = analysis.get("category", "Other")
    location = analysis.get("location", "Location not specified")

    # Check for duplicate complaints
    dup_res = (
        supabase.table("raw_complaints")
        .select("*")
        .eq("whatsapp_number", whatsapp_number)
        .eq("category", category)
        .eq("location", location)
        .neq("status", "resolved")
        .limit(1)
        .execute()
    )
    if dup_res.data:
        existing = dup_res.data[0]
        ticket_id = _ticket_display(existing["id"])
        logger.info(
            "Duplicate complaint detected for %s: ticket=%s, category=%s, location=%s",
            whatsapp_number, ticket_id, category, location,
        )
        await send_message(whatsapp_number, _format_duplicate(existing, ticket_id))
        supabase.table("users").update(
            {"state": "idle", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
        return

    draft = {
        "category": category,
        "categories": analysis.get("categories", [category]),
        "urgency": analysis.get("urgency", "Medium"),
        "location": location,
        "ward": analysis.get("ward", "Unknown"),
        "summary": analysis.get("summary", ""),
        "sentiment": analysis.get("sentiment", "Neutral"),
        "raw_message": text,
        "photo_url": None,
    }
    if is_voice:
        draft["transcription"] = (analysis.get("transcription") or "").strip()
    
    # Store draft persistently in database
    draft_record = {
        "whatsapp_number": whatsapp_number,
        "draft_data": draft,
        "status": "draft"
    }
    
    # Remove any existing draft for this user
    supabase.table("complaint_drafts").delete().eq("whatsapp_number", whatsapp_number).execute()
    
    # Insert new draft
    draft_result = supabase.table("complaint_drafts").insert(draft_record).execute()
    
    if draft_result.data:
        draft_id = draft_result.data[0]["id"]
        # Update user state with draft ID reference
        supabase.table("users").update(
            {
                "state": "confirming",
                "state_data": {"draft_id": draft_id},
            }
        ).eq("whatsapp_number", whatsapp_number).execute()
    else:
        # Fallback to in-memory if database insert fails
        supabase.table("users").update(
            {
                "state": "confirming",
                "state_data": {"draft": draft},
            }
        ).eq("whatsapp_number", whatsapp_number).execute()
    await send_message(
        whatsapp_number,
        _format_voice_confirmation(draft) if is_voice else _format_confirmation(draft),
    )
    logger.info(
        "Draft created for %s: category=%s, categories=%s, urgency=%s, ward=%s",
        whatsapp_number,
        draft["category"],
        draft["categories"],
        draft["urgency"],
        draft["ward"],
    )


async def _download_whatsapp_audio(media_id: str) -> tuple[bytes, Optional[str]]:
    """Download an audio media attachment from WhatsApp Cloud API by media_id."""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    graph_base = "https://graph.facebook.com/v18.0"
    async with httpx.AsyncClient(timeout=60.0) as client:
        meta = await client.get(f"{graph_base}/{media_id}", headers=headers)
        meta.raise_for_status()
        media = meta.json()
        download_url = media.get("url")
        mime = media.get("mime_type")
        if not download_url:
            raise ValueError("Missing media download URL")
        audio_res = await client.get(download_url, headers=headers)
        audio_res.raise_for_status()
        return audio_res.content, mime
