"""Handler for awaiting rating state - processes citizen ratings for resolved complaints."""

import logging

from config import supabase
from services.whatsapp import send_message

logger = logging.getLogger(__name__)


def _ticket_display(complaint_id) -> str:
    """Format a complaint UUID into a short human-readable ticket ID."""
    return str(complaint_id)[:8].upper()


async def handle_awaiting_rating(whatsapp_number: str, message_text: str) -> None:
    """Handle messages from users in awaiting_rating state -- process ratings or re-prompt."""
    # Get user state to find which complaint to rate
    user_res = (
        supabase.table("users")
        .select("*")
        .eq("whatsapp_number", whatsapp_number)
        .limit(1)
        .execute()
    )
    user = user_res.data[0] if user_res.data else None
    if not user:
        return
    
    state_data = user.get("state_data") or {}
    complaint_id = state_data.get("complaint_id")
    
    if not complaint_id:
        # No complaint ID in state, reset to idle
        supabase.table("users").update(
            {"state": "idle", "state_data": {}}
        ).eq("whatsapp_number", whatsapp_number).execute()
        await send_message(
            whatsapp_number,
            "No complaint found to rate. Send NEW to report a civic issue or STATUS to check your complaint history."
        )
        return
    
    # Check if the message is a valid rating (1-5)
    message = (message_text or "").strip().lower()
    if message in ("1", "2", "3", "4", "5"):
        rating = int(message)
        
        # Update the complaint with the rating
        update_res = supabase.table("raw_complaints").update(
            {"rating": rating}
        ).eq("id", complaint_id).eq("whatsapp_number", whatsapp_number).execute()
        
        if update_res.data:
            complaint = update_res.data[0]
            ticket_id = _ticket_display(complaint_id)
            
            # Also update the officer's record if officer is assigned
            officer_id = complaint.get("assigned_officer_id")
            if officer_id:
                # This would update officer performance metrics in a real system
                logger.info("Officer %s received rating %d for complaint %s", officer_id, rating, ticket_id)
            
            # Reset user state to idle
            supabase.table("users").update(
                {"state": "idle", "state_data": {}}
            ).eq("whatsapp_number", whatsapp_number).execute()
            
            await send_message(
                whatsapp_number,
                f"Thank you for your feedback. Your rating of {rating}/5 has been recorded."
            )
            logger.info("User %s rated complaint %s: %d/5", whatsapp_number, ticket_id, rating)
        else:
            logger.error("Failed to update rating for complaint %s", complaint_id)
            await send_message(
                whatsapp_number,
                "Sorry, I could not record your rating. Please try again."
            )
    else:
        # Invalid response, re-prompt
        await send_message(
            whatsapp_number,
            "Please reply with a number between 1 and 5 to rate your experience."
        )
        logger.info("Invalid rating response from %s: %s", whatsapp_number, message_text)
