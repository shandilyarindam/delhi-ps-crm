"""WhatsApp webhook router -- handles Meta verification and incoming messages."""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Request, Response, Query

from config import WHATSAPP_VERIFY_TOKEN
from handlers.state_machine import route_message

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_MESSAGE_AGE_SECONDS = 30


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> Response:
    """Verify the WhatsApp webhook subscription with Meta's challenge-response."""
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning("Webhook verification failed: invalid token")
    return Response(content="Forbidden", status_code=403)


def _extract_incoming_messages(
    body: Dict[str, Any],
) -> List[Tuple[str, str, str, Optional[str], int]]:
    """Parse WhatsApp payload into (whatsapp_number, message_text, message_type, media_id, timestamp)."""
    out: List[Tuple[str, str, str, Optional[str], int]] = []
    for entry in body.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            for msg in value.get("messages") or []:
                from_id = msg.get("from")
                if not from_id:
                    continue
                typ = msg.get("type") or "unknown"
                text = ""
                if typ == "text":
                    text = (msg.get("text") or {}).get("body") or ""
                media_id = None
                if typ == "image":
                    media_id = (msg.get("image") or {}).get("id")
                if typ == "audio":
                    media_id = (msg.get("audio") or {}).get("id")
                ts = int(msg.get("timestamp") or 0)
                out.append((str(from_id), text, typ, media_id, ts))
    return out


@router.post("/webhook")
async def receive_message(request: Request) -> dict[str, str]:
    """Receive and process incoming WhatsApp messages from the Meta webhook."""
    try:
        body = await request.json()
        messages = _extract_incoming_messages(body)
        logger.info("Received %d message(s) from webhook", len(messages))
        now = int(time.time())
        for whatsapp_number, message_text, message_type, media_id, msg_ts in messages:
            # Deduplication: ignore messages older than 30 seconds
            if msg_ts > 0 and (now - msg_ts) > MAX_MESSAGE_AGE_SECONDS:
                logger.info(
                    "Dropping stale message from %s (age=%ds)",
                    whatsapp_number,
                    now - msg_ts,
                )
                continue
            await route_message(
                whatsapp_number,
                message_text,
                message_type=message_type,
                media_id=media_id,
            )
    except ValueError as exc:
        logger.error("Invalid JSON in webhook POST: %s", exc)
    except Exception:
        logger.exception("Webhook POST handling failed")
    return {"status": "ok"}
