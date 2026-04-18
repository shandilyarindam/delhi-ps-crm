"""Handler for complaint filing -- collects complaint text, detects duplicates, and runs AI analysis."""

import logging

from config import supabase
from services.ai import analyze_complaint
from services.whatsapp import send_message

logger = logging.getLogger(__name__)


def _ticket_display(complaint_id) -> str:
    """Format a complaint UUID into a short human-readable ticket ID."""
    return str(complaint_id)[:8].upper()


def _format_confirmation(draft: dict) -> str:
    """Format the AI-analyzed complaint draft into a confirmation message with ward."""
    return (
        "Thanks -- I've noted your complaint.\n"
        f"Category    : {draft['category']}\n"
        f"Urgency     : {draft['urgency']}\n"
        f"Location    : {draft['location']}\n"
        f"Ward        : {draft.get('ward', 'Unknown')}\n"
        f"Summary     : {draft['summary']}\n"
        "\nReply YES to submit, NO to cancel, or send a photo as evidence."
    )


def _format_duplicate(existing: dict, ticket_id: str) -> str:
    """Format the duplicate complaint notification message."""
    return (
        "A similar complaint has already been filed.\n"
        "\n"
        f"Ticket   : {ticket_id}\n"
        f"Category : {existing.get('category', 'N/A')}\n"
        f"Location : {existing.get('location', 'N/A')}\n"
        f"Status   : {existing.get('status', 'open')}\n"
        "\n"
        "Your complaint is already being tracked. "
        "Send NEW to file a different complaint or STATUS to check updates."
    )


async def handle_filing(
    whatsapp_number: str, message_text: str, *, message_type: str = "text"
) -> None:
    """Process the user's complaint description, check for duplicates, and generate an AI-analyzed draft."""
    if message_type != "text":
        await send_message(
            whatsapp_number,
            "Please describe your issue in a text message.",
        )
        return

    text = (message_text or "").strip()
    if not text:
        await send_message(whatsapp_number, "Please describe your issue.")
        return

    logger.info("Analyzing complaint from %s", whatsapp_number)
    analysis = await analyze_complaint(text)

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
        "complaint_text": text,
        "photo_url": None,
    }
    supabase.table("users").update(
        {
            "state": "confirming",
            "state_data": {"draft": draft},
        }
    ).eq("whatsapp_number", whatsapp_number).execute()
    await send_message(whatsapp_number, _format_confirmation(draft))
    logger.info(
        "Draft created for %s: category=%s, categories=%s, urgency=%s, ward=%s",
        whatsapp_number,
        draft["category"],
        draft["categories"],
        draft["urgency"],
        draft["ward"],
    )
