"""WhatsApp webhook router -- handles Meta verification and incoming messages."""

import hashlib
import hmac
import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException, Request, Response, Query

from config import WHATSAPP_VERIFY_TOKEN
from handlers.state_machine import route_message

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_MESSAGE_AGE_SECONDS = 30
MAX_REQUESTS_PER_MINUTE = 100
RATE_LIMIT_WINDOW = 60  # seconds

# In-memory rate limiting store (for production, use Redis)
_rate_limit_store: Dict[str, List[float]] = defaultdict(list)


def _is_rate_limited(phone_number: str) -> bool:
    """Check if phone number has exceeded rate limit."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old entries
    _rate_limit_store[phone_number] = [
        timestamp for timestamp in _rate_limit_store[phone_number]
        if timestamp > window_start
    ]
    
    # Check if under limit
    if len(_rate_limit_store[phone_number]) >= MAX_REQUESTS_PER_MINUTE:
        return True
    
    # Add current request
    _rate_limit_store[phone_number].append(now)
    return False


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


def _verify_signature(body: bytes, signature: str) -> bool:
    """Verify HMAC-SHA256 signature from Meta webhook."""
    if not signature or not signature.startswith("sha256="):
        return False
    
    signature_hash = signature[7:]  # Remove 'sha256=' prefix
    expected_hash = hmac.new(
        WHATSAPP_VERIFY_TOKEN.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature_hash, expected_hash)


@router.post("/webhook")
async def receive_message(request: Request) -> dict[str, str]:
    """Receive and process incoming WhatsApp messages from the Meta webhook."""
    # Verify signature
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        logger.warning("Webhook request missing signature header")
        raise HTTPException(status_code=403, detail="Missing signature")
    
    body = await request.body()
    if not _verify_signature(body, signature):
        logger.warning("Webhook signature verification failed")
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse body for rate limiting
    try:
        body_json = await request.json()
    except Exception as exc:
        logger.error("Failed to parse webhook JSON for rate limiting: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Extract phone numbers for rate limiting
    messages = _extract_incoming_messages(body_json)
    for whatsapp_number, _, _, _, _ in messages:
        if _is_rate_limited(whatsapp_number):
            logger.warning("Rate limit exceeded for %s", whatsapp_number)
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later."
            )
    
    # Process the already parsed body_json
    try:
        messages = _extract_incoming_messages(body_json)
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
        logger.error("Value error processing webhook messages: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid message format")
    except KeyError as exc:
        logger.error("Missing required field in webhook messages: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid message structure")
    except Exception as exc:
        logger.exception("Unexpected error processing webhook messages: %s", exc)
        raise HTTPException(status_code=500, detail="Internal processing error")
    
    return {"status": "ok"}
