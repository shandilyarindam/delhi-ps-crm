"""WhatsApp Business API client for sending text messages."""

import logging

import httpx

from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = (
    f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
)


async def send_message(phone: str, text: str) -> dict:
    """Send a text message to a WhatsApp user via the Cloud API."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                WHATSAPP_API_URL, json=payload, headers=headers
            )
            response.raise_for_status()
            logger.info("Message sent to %s", phone)
            return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error("WhatsApp API HTTP error for %s: %s", phone, exc)
        raise
    except httpx.RequestError as exc:
        logger.error("Network error sending message to %s: %s", phone, exc)
        raise
