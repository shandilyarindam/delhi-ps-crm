"""Handler for photo evidence -- downloads from WhatsApp and uploads to Supabase Storage."""

import logging
from typing import Optional
from uuid import uuid4

import httpx

from config import WHATSAPP_TOKEN, supabase

logger = logging.getLogger(__name__)

STORAGE_BUCKET = "complaint-evidence"


async def store_whatsapp_image(media_id: str, whatsapp_number: str) -> Optional[str]:
    """Download an image from WhatsApp Cloud API and upload to Supabase Storage."""
    if not media_id or not WHATSAPP_TOKEN:
        return None

    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    graph_base = "https://graph.facebook.com/v18.0"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            meta = await client.get(f"{graph_base}/{media_id}", headers=headers)
            meta.raise_for_status()
            media = meta.json()
            download_url = media.get("url")
            mime = media.get("mime_type") or "image/jpeg"
            if not download_url:
                logger.warning("No download URL in media metadata for media_id=%s", media_id)
                return None
            file_res = await client.get(download_url, headers=headers)
            file_res.raise_for_status()
            content = file_res.content

        ext = ".jpg"
        if "png" in mime:
            ext = ".png"
        elif "webp" in mime:
            ext = ".webp"

        path = f"{whatsapp_number}/{uuid4()}{ext}"
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path,
            content,
            file_options={"content-type": mime},
        )
        public = supabase.storage.from_(STORAGE_BUCKET).get_public_url(path)
        logger.info("Image uploaded to %s for %s", path, whatsapp_number)
        return public
    except httpx.HTTPStatusError as exc:
        logger.error("HTTP error downloading media %s: %s", media_id, exc)
        return None
    except (httpx.RequestError, OSError) as exc:
        logger.error("Network error during image upload for %s: %s", whatsapp_number, exc)
        return None
    except Exception as exc:
        logger.exception("Unexpected error in store_whatsapp_image: %s", exc)
        return None
