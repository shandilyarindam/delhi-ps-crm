"""Handler for idle-state users: status checks, new complaints, ratings, and cancellation."""

import logging

from config import supabase
from services.whatsapp import send_message

logger = logging.getLogger(__name__)


def _ticket_display(complaint_id) -> str:
    """Format a complaint UUID into a short human-readable ticket ID."""
    return str(complaint_id)[:8].upper()


async def cancel_complaint_flow(whatsapp_number: str) -> None:
    """Cancel any in-progress complaint and reset user state to idle."""
    supabase.table("users").update(
        {"state": "idle", "state_data": {}}
    ).eq("whatsapp_number", whatsapp_number).execute()
    await send_message(
        whatsapp_number,
        "Your complaint has been cancelled. "
        "Send NEW to file a fresh complaint or STATUS to view existing ones.",
    )
    logger.info("Complaint flow cancelled for %s", whatsapp_number)


async def _send_complaint_status(whatsapp_number: str) -> None:
    """Fetch and send all complaints for a user as a formatted list."""
    res = (
        supabase.table("raw_complaints")
        .select("*")
        .eq("whatsapp_number", whatsapp_number)
        .order("timestamp", desc=True)
        .execute()
    )
    rows = res.data or []
    if not rows:
        await send_message(whatsapp_number, "You have no complaints filed yet.")
        return

    lines = ["Your complaints:", ""]
    for i, c in enumerate(rows, start=1):
        tid = _ticket_display(c["id"])
        cat = c.get("category") or "--"
        urg = c.get("urgency") or "--"
        st = c.get("status") or "open"
        summ = c.get("summary") or "--"
        lines.append(f"{i}. Ticket: {tid}")
        lines.append(f"   Category: {cat}")
        lines.append(f"   Urgency: {urg}")
        lines.append(f"   Status: {st}")
        lines.append(f"   Summary: {summ}")
        lines.append("")
    body = "\n".join(lines).rstrip()
    await send_message(whatsapp_number, body)


async def _handle_rating(whatsapp_number: str, rating: int) -> None:
    """Record a citizen rating for the most recently resolved complaint."""
    res = (
        supabase.table("raw_complaints")
        .select("id")
        .eq("whatsapp_number", whatsapp_number)
        .eq("status", "resolved")
        .order("timestamp", desc=True)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    if not rows:
        await send_message(
            whatsapp_number,
            "No resolved complaint found to rate. "
            "Send NEW to report a civic issue or STATUS to track your existing complaints.",
        )
        return

    cid = rows[0]["id"]
    supabase.table("raw_complaints").update(
        {"rating": rating}
    ).eq("id", cid).execute()
    await send_message(
        whatsapp_number,
        f"Thank you for your feedback. Your rating of {rating}/5 has been recorded.",
    )
    logger.info("User %s rated complaint %s: %d/5", whatsapp_number, cid, rating)


NEW_COMPLAINT_TEXT = (
    "Please describe the civic issue you want to report. "
    "Include your location or area name for faster resolution.\n\n"
    "You can:\n"
    "- Type your complaint in Hindi, English, Urdu, Punjabi, or any regional language\n"
    "- Send a voice note describing the issue\n\n"
    "Our system will automatically understand and process your complaint."
)


async def handle_idle(whatsapp_number: str, message_text: str) -> None:
    """Handle messages from users in idle state -- dispatches to status, new complaint, or rating."""
    t = (message_text or "").strip().lower()

    if t == "status":
        await _send_complaint_status(whatsapp_number)
        return

    if t == "new":
        supabase.table("users").update(
            {"state": "filing", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
        await send_message(whatsapp_number, NEW_COMPLAINT_TEXT)
        logger.info("User %s started new complaint flow", whatsapp_number)
        return

    # Check for rating (1-5)
    if t in ("1", "2", "3", "4", "5"):
        await _handle_rating(whatsapp_number, int(t))
        return

    # Fallback for unrecognized input
    await send_message(
        whatsapp_number,
        "Send NEW to file a complaint or STATUS to check existing ones.",
    )
