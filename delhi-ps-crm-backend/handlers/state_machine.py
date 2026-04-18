"""State machine that routes incoming WhatsApp messages to the appropriate handler."""

import logging
from typing import Optional

from config import supabase
from handlers.confirming import handle_confirming
from handlers.filing import handle_filing
from handlers.idle import cancel_complaint_flow, handle_idle
from handlers.registration import handle_registration

logger = logging.getLogger(__name__)


def _is_no(text: str) -> bool:
    """Check if the user's message is a cancellation command."""
    return (text or "").strip().lower() == "no"


async def route_message(
    whatsapp_number: str,
    message_text: str,
    *,
    message_type: str = "text",
    media_id: Optional[str] = None,
) -> None:
    """Route an incoming message based on the user's current conversation state."""
    res = (
        supabase.table("users")
        .select("*")
        .eq("whatsapp_number", whatsapp_number)
        .limit(1)
        .execute()
    )
    user = res.data[0] if res.data else None
    state = user.get("state") if user else None

    logger.info("Routing message from %s (state=%s, type=%s)", whatsapp_number, state, message_type)

    if state is None or state == "registering":
        await handle_registration(whatsapp_number, message_text)
        return

    if user and _is_no(message_text) and message_type == "text":
        await cancel_complaint_flow(whatsapp_number)
        return

    if state == "idle":
        await handle_idle(whatsapp_number, message_text)
    elif state == "filing":
        await handle_filing(
            whatsapp_number,
            message_text,
            message_type=message_type,
            media_id=media_id,
        )
    elif state == "awaiting_photo":
        await handle_confirming(
            whatsapp_number,
            message_text,
            message_type=message_type,
            media_id=media_id,
        )
    elif state == "confirming":
        await handle_confirming(
            whatsapp_number,
            message_text,
            message_type=message_type,
            media_id=media_id,
        )
    else:
        logger.warning(
            "Unknown user state %r for %s; resetting to idle", state, whatsapp_number
        )
        supabase.table("users").update(
            {"state": "idle", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
