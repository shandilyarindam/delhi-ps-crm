"""Handler for user registration -- new user creation and name collection."""

import logging

from config import supabase
from services.whatsapp import send_message

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "Namaskar! Welcome to the Delhi Civic Grievance Portal. "
    "I am here to help you report civic issues in your area.\n\n"
    "To get started, please share your full name."
)


async def handle_registration(whatsapp_number: str, message_text: str) -> None:
    """Register new users or collect name when state is registering."""
    res = (
        supabase.table("users")
        .select("*")
        .eq("whatsapp_number", whatsapp_number)
        .limit(1)
        .execute()
    )
    user = res.data[0] if res.data else None

    if user is None:
        supabase.table("users").insert(
            {
                "whatsapp_number": whatsapp_number,
                "state": "registering",
                "state_data": {},
            }
        ).execute()
        await send_message(whatsapp_number, WELCOME_TEXT)
        logger.info("New user initiated registration: %s", whatsapp_number)
        return

    if user.get("state") == "registering":
        name = (message_text or "").strip()
        if len(name) >= 2:
            supabase.table("users").update(
                {"name": name, "state": "idle"}
            ).eq("whatsapp_number", whatsapp_number).execute()
            await send_message(
                whatsapp_number,
                f"Thank you, {name}. Your account has been created.\n\n"
                "Send NEW to report a civic issue or STATUS to track your existing complaints.",
            )
            logger.info("User %s registered with name: %s", whatsapp_number, name)
        else:
            await send_message(
                whatsapp_number,
                "Please send your full name (at least 2 characters).",
            )
        return
