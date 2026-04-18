"""Supabase Storage helpers used by handlers/services.

These helpers keep storage usage consistent across the codebase and provide
small, typed wrappers around the Supabase client.
"""

from __future__ import annotations

from typing import Any, Optional

from config import supabase


def get_public_url(bucket: str, path: str) -> str:
    """Return a public URL for an object already stored in Supabase Storage."""
    return supabase.storage.from_(bucket).get_public_url(path)


def upload_bytes(
    bucket: str,
    path: str,
    data: bytes,
    *,
    content_type: Optional[str] = None,
    file_options: Optional[dict[str, Any]] = None,
) -> Any:
    """Upload raw bytes to Supabase Storage and return the SDK response."""
    opts: dict[str, Any] = dict(file_options or {})
    if content_type:
        opts.setdefault("content-type", content_type)
    if opts:
        return supabase.storage.from_(bucket).upload(path, data, file_options=opts)
    return supabase.storage.from_(bucket).upload(path, data)
