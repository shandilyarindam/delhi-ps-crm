"""Pydantic schemas for request/response validation.

These reflect the data structures used by the WhatsApp flow and webhook inputs.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator
from typing_extensions import TypedDict


class ComplaintCreate(BaseModel):
    """Schema for creating a new complaint."""
    summary: str = Field(..., min_length=1, max_length=500, description="Brief summary of the complaint")
    category: str = Field(..., min_length=1, max_length=50, description="Complaint category")
    urgency: str = Field(..., min_length=1, max_length=20, description="Complaint urgency level")
    location: str = Field(..., max_length=200, description="Complaint location")
    ward: Optional[str] = Field(None, max_length=50, description="Delhi ward")
    whatsapp_number: str = Field(..., min_length=10, max_length=15, description="WhatsApp phone number")
    raw_message: str = Field(..., min_length=1, max_length=2000, description="Original message content")
    status: str = "open"
    photo_url: Optional[str] = None
    rating: Optional[int] = None

    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            "Waste Management", "Water Supply", "Sewage & Drainage", 
            "Roads", "Electricity", "Other"
        ]
        if v not in valid_categories:
            raise ValueError(f'Invalid category. Must be one of: {valid_categories}')
        return v

    @validator('urgency')
    def validate_urgency(cls, v):
        valid_urgencies = ["Low", "Medium", "High", "Critical"]
        if v not in valid_urgencies:
            raise ValueError(f'Invalid urgency. Must be one of: {valid_urgencies}')
        return v

    @validator('whatsapp_number')
    def validate_whatsapp_number(cls, v):
        if not v.isdigit() or len(v) < 10 or len(v) > 15:
            raise ValueError('WhatsApp number must be 10-15 digits')
        return v


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    whatsapp_number: str = Field(..., min_length=10, max_length=15, description="WhatsApp phone number")
    name: Optional[str] = None
    state: str = Field("registering", max_length=20, description="User state")
    state_data: Dict[str, Any] = Field(default_factory=dict)

    @validator('whatsapp_number')
    def validate_whatsapp_number(cls, v):
        if not v.isdigit() or len(v) < 10 or len(v) > 15:
            raise ValueError('WhatsApp number must be 10-15 digits')
        return v

    @validator('state')
    def validate_state(cls, v):
        valid_states = ["registering", "idle", "filing", "confirming", "registered"]
        if v not in valid_states:
            raise ValueError(f'Invalid state. Must be one of: {valid_states}')
        return v


class WebhookPayload(BaseModel):
    """Schema for Meta webhook payload validation."""
    record: Dict[str, Any] = Field(default_factory=dict)
