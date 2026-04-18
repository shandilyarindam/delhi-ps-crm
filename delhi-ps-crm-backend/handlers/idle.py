"""Handler for idle-state users: status checks, new complaints, and cancellation."""

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
        "Cancelled. Send 'new' to file another complaint.",
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


async def handle_idle(whatsapp_number: str, message_text: str) -> None:
    """Handle messages from users in idle state -- dispatches to status or new complaint flow."""
    t = (message_text or "").strip().lower()
    if t == "status":
        await _send_complaint_status(whatsapp_number)
        return
    if t == "new":
        supabase.table("users").update(
            {"state": "filing", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
        await send_message(whatsapp_number, "Describe your issue")
        logger.info("User %s started new complaint flow", whatsapp_number)
        return

    # Fallback for unrecognized input
    await send_message(
        whatsapp_number,
        "I did not understand that.\n\nSend NEW to file a complaint or STATUS to check your existing complaints.",
    )
