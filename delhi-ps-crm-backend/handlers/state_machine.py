"""State machine that routes incoming WhatsApp messages to the appropriate handler."""

import logging
from typing import Optional

from config import supabase
from handlers.awaiting_rating import handle_awaiting_rating
from handlers.confirming import handle_confirming
from handlers.filing import handle_filing
from handlers.idle import handle_idle
from handlers.registration import handle_registration

logger = logging.getLogger(__name__)


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

    # New user -- not in DB at all
    if user is None:
        await handle_registration(whatsapp_number, message_text)
        return

    # User exists but still registering
    if state == "registering":
        await handle_registration(whatsapp_number, message_text)
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
    elif state in ("confirming", "awaiting_photo"):
        await handle_confirming(
            whatsapp_number,
            message_text,
            message_type=message_type,
            media_id=media_id,
        )
    elif state == "awaiting_rating":
        await handle_awaiting_rating(whatsapp_number, message_text)
    else:
        logger.warning(
            "Unknown user state %r for %s; resetting to idle", state, whatsapp_number
        )
        supabase.table("users").update(
            {"state": "idle", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
