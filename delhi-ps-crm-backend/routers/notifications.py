"""Notification endpoints for officer assignment and complaint resolution alerts."""

import logging

from fastapi import APIRouter, Request

from config import supabase
from services.whatsapp import send_message

logger = logging.getLogger(__name__)

router = APIRouter()


def _ticket_display(complaint_id) -> str:
    """Format a complaint UUID into a short human-readable ticket ID."""
    return str(complaint_id)[:8].upper()


@router.post("/notifications/assignment")
async def notify_assignment(request: Request) -> dict[str, str]:
    """Handle Supabase webhook for complaint updates -- officer assignment and resolution."""
    try:
        body = await request.json()
        logger.info("Notification received: %s", body)

        record = body.get("record") or {}
        whatsapp_number = record.get("whatsapp_number")
        status = (record.get("status") or "").strip().lower()
        category = record.get("category") or "N/A"
        cid = record.get("id")

        if not whatsapp_number or not cid:
            logger.warning("Notification missing whatsapp_number or id, skipping")
            return {"status": "ok"}

        ticket_id = _ticket_display(cid)

        if status == "assigned" and record.get("assigned_to"):
            officer_name = record.get("assigned_to", "an officer")
            msg = (
                f"Your complaint {ticket_id} regarding {category} "
                f"has been assigned to Officer {officer_name}. "
                f"They will be in touch shortly."
            )
            await send_message(whatsapp_number, msg)
            logger.info("Assignment notification sent for ticket %s to %s", ticket_id, whatsapp_number)

        elif status == "resolved":
            msg = (
                f"Your complaint {ticket_id} regarding {category} "
                f"has been resolved. Thank you for using Delhi PS-CRM."
            )
            await send_message(whatsapp_number, msg)
            logger.info("Resolution notification sent for ticket %s to %s", ticket_id, whatsapp_number)

    except Exception as exc:
        logger.exception("Notification handling failed: %s", exc)

    return {"status": "ok"}
