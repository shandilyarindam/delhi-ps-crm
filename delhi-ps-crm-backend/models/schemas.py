"""Pydantic schemas for request/response validation.

These reflect the data structures used by the WhatsApp flow and webhook inputs.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    """Payload used when creating a complaint record."""

    whatsapp_number: str
    category: str
    categories: list[str] = Field(default_factory=list)
    urgency: str = "Medium"
    location: str = "Location not specified"
    ward: str = "Unknown"
    sentiment: str = "Neutral"
    summary: str = ""
    status: str = "open"
    photo_url: Optional[str] = None
    raw_message: str = ""
    rating: Optional[int] = None


class UserCreate(BaseModel):
    """Payload used when creating/updating a user record."""

    whatsapp_number: str
    name: Optional[str] = None
    state: str = "registering"
    state_data: dict[str, Any] = Field(default_factory=dict)


class WebhookPayload(BaseModel):
    """Supabase webhook payload used by `/notifications/assignment`."""

    record: dict[str, Any] = Field(default_factory=dict)
