"""Application configuration -- loads and validates environment variables."""

import logging
import os
import re
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, validator, HttpUrl
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Required WhatsApp configuration
    whatsapp_token: str = Field(..., description="WhatsApp Business API token")
    whatsapp_phone_number_id: str = Field(..., description="WhatsApp phone number ID")
    whatsapp_verify_token: str = Field(..., description="WhatsApp webhook verification token")
    
    # Required AI configuration
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    
    # Required database configuration
    supabase_url: HttpUrl = Field(..., description="Supabase project URL")
    supabase_service_key: Optional[str] = Field(None, description="Supabase service role key")
    
    # Required notification configuration
    hod_whatsapp_number: Optional[str] = Field(None, description="HoD WhatsApp number")
    
    # Optional configuration
    gmail_address: Optional[str] = Field(None, description="Gmail address for notifications")
    gmail_app_password: Optional[str] = Field(None, description="Gmail app-specific password")
    
    # Application configuration
    app_name: str = "Delhi PS-CRM"
    app_version: str = "1.0.0"
    log_level: str = Field("INFO", description="Application log level")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra environment variables
    
    @validator('whatsapp_phone_number_id')
    def validate_phone_number_id(cls, v):
        """Validate WhatsApp phone number ID format."""
        if not re.match(r'^\d+$', v):
            raise ValueError('WhatsApp phone number ID must be numeric')
        return v
    
    @validator('hod_whatsapp_number')
    def validate_whatsapp_number(cls, v):
        """Validate WhatsApp number format."""
        if v is None or v == "":
            return None
        # Remove any non-digit characters and validate format
        clean_number = re.sub(r'[^\d]', '', v)
        if not re.match(r'^\d{10,15}$', clean_number):
            raise ValueError('WhatsApp number must be 10-15 digits')
        return clean_number
    
    @validator('gemini_api_key')
    def validate_gemini_key(cls, v):
        """Validate Gemini API key format."""
        if not v.startswith('AIza'):
            raise ValueError('Invalid Gemini API key format')
        return v
    
    @validator('supabase_service_key')
    def validate_supabase_key(cls, v):
        """Validate Supabase service key format."""
        if v is None:
            return v
        if not v.startswith('eyJ'):
            raise ValueError('Invalid Supabase service key')
        return v
    
    @validator('gmail_address')
    def validate_gmail_address(cls, v):
        """Validate Gmail address format."""
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', v):
            raise ValueError('Must be a valid Gmail address')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()


# Initialize settings with validation
settings = Settings()

# Export variables for backward compatibility
WHATSAPP_TOKEN = settings.whatsapp_token
WHATSAPP_PHONE_NUMBER_ID = settings.whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN = settings.whatsapp_verify_token
GEMINI_API_KEY = settings.gemini_api_key
SUPABASE_URL = str(settings.supabase_url)
SUPABASE_KEY = settings.supabase_service_key or os.getenv('SUPABASE_KEY', '')  # Fallback to anon key
HOD_WHATSAPP_NUMBER = settings.hod_whatsapp_number
GMAIL_ADDRESS = settings.gmail_address
GMAIL_APP_PASSWORD = settings.gmail_app_password

# -- Supabase client ---------------------------------------------------------

from supabase import create_client, Client  # noqa: E402

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)