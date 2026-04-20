"""Handler for complaint confirmation -- accepts photos, confirms, submits to Supabase, and sends email notifications."""

import logging
from typing import Optional

from config import supabase
from handlers.awaiting_photo import store_whatsapp_image
from services.email_service import send_complaint_registered_email
from services.whatsapp import send_message

logger = logging.getLogger(__name__)


def _ticket_id_from_uuid(uid) -> str:
    """Convert a complaint UUID into a short display ticket ID."""
    s = str(uid)
    return s[:8].upper()


def _format_registered(ticket_id: str, draft: dict) -> str:
    """Format the successful registration message with ticket details."""
    return (
        "Your complaint has been registered with the Delhi Civic Grievance System.\n\n"
        f"Ticket ID : {ticket_id}\n"
        f"Category  : {draft['category']}\n"
        f"Urgency   : {draft['urgency']}\n\n"
        "The concerned department has been notified. "
        "An officer will be assigned shortly."
    )


async def handle_confirming(
    whatsapp_number: str,
    message_text: str,
    *,
    message_type: str = "text",
    media_id: Optional[str] = None,
) -> None:
    """Handle confirmation state -- process photo uploads or YES/NO commands."""
    res = (
        supabase.table("users")
        .select("*")
        .eq("whatsapp_number", whatsapp_number)
        .limit(1)
        .execute()
    )
    user = res.data[0] if res.data else None
    if not user:
        return

    state_data = user.get("state_data") or {}
    draft = {}
    
    # Try to get draft from database first (persistent storage)
    draft_id = state_data.get("draft_id")
    if draft_id:
        draft_res = (
            supabase.table("complaint_drafts")
            .select("*")
            .eq("id", draft_id)
            .eq("whatsapp_number", whatsapp_number)
            .eq("status", "draft")
            .limit(1)
            .execute()
        )
        if draft_res.data:
            draft = draft_res.data[0].get("draft_data") or {}
    
    # Fallback to in-memory state_data if database draft not found
    if not draft:
        draft = state_data.get("draft") or {}

    if message_type == "image" and media_id:
        url = await store_whatsapp_image(media_id, whatsapp_number)
        if not url:
            await send_message(
                whatsapp_number,
                "Could not save your photo. Please try again or reply YES to submit without a photo.",
            )
            return
        draft["photo_url"] = url
        
        # Update draft in database if we have a draft_id
        draft_id = state_data.get("draft_id")
        if draft_id:
            supabase.table("complaint_drafts").update({
                "draft_data": draft
            }).eq("id", draft_id).eq("whatsapp_number", whatsapp_number).execute()
        else:
            # Fallback to in-memory state_data
            state_data["draft"] = draft
            supabase.table("users").update({"state_data": state_data}).eq(
                "whatsapp_number", whatsapp_number
            ).execute()
        await send_message(
            whatsapp_number,
            "Photo evidence received. Reply YES to submit your complaint or NO to cancel.",
        )
        logger.info("Photo stored for %s", whatsapp_number)
        return

    cmd = (message_text or "").strip().lower()
    if cmd == "yes":
        if not draft.get("category"):
            await send_message(
                whatsapp_number,
                "Nothing to submit. Send NEW to start a complaint.",
            )
            return

        row = {
            "whatsapp_number": whatsapp_number,
            "category": draft["category"],
            "categories": draft.get("categories", [draft["category"]]),
            "urgency": draft["urgency"],
            "location": draft["location"],
            "ward": draft.get("ward", "Unknown"),
            "sentiment": draft.get("sentiment", "Neutral"),
            "summary": draft["summary"],
            "status": "open",
            "photo_url": draft.get("photo_url"),
            "raw_message": draft.get("raw_message", ""),
        }

        ins = supabase.table("raw_complaints").insert(row).execute()
        if not ins.data:
            logger.error("raw_complaints insert returned no data for %s", whatsapp_number)
            await send_message(
                whatsapp_number,
                "Could not register your complaint. Please try again later.",
            )
            return

        complaint = ins.data[0]
        cid = complaint["id"]
        ticket = _ticket_id_from_uuid(cid)
        await send_message(whatsapp_number, _format_registered(ticket, draft))

        # Send email notifications to relevant department(s)
        try:
            await send_complaint_registered_email(complaint, user)
        except Exception as exc:
            logger.error("Email notification failed for ticket %s: %s", ticket, exc)

        # Clean up draft from database
        draft_id = state_data.get("draft_id")
        if draft_id:
            supabase.table("complaint_drafts").delete().eq("id", draft_id).eq("whatsapp_number", whatsapp_number).execute()
        
        supabase.table("users").update(
            {"state": "idle", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
        logger.info("Complaint %s submitted by %s", ticket, whatsapp_number)
        return

    if cmd == "no":
        # Clean up draft from database
        draft_id = state_data.get("draft_id")
        if draft_id:
            supabase.table("complaint_drafts").delete().eq("id", draft_id).eq("whatsapp_number", whatsapp_number).execute()
        
        supabase.table("users").update(
            {"state": "idle", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
        await send_message(
            whatsapp_number,
            "Your complaint has been cancelled. "
            "Send NEW to file a fresh complaint or STATUS to view existing ones.",
        )
        logger.info("Complaint cancelled by %s during confirmation", whatsapp_number)
        return

    # Fallback for anything that is not YES/NO and not a photo
    await send_message(
        whatsapp_number,
        "Please reply YES to submit, NO to cancel, or send a photo as evidence.",
    )
