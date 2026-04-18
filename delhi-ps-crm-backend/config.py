"""Application configuration -- loads and validates environment variables."""

import os
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# -- Required environment variables ------------------------------------------

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HOD_WHATSAPP_NUMBER = os.getenv("HOD_WHATSAPP_NUMBER")

# -- Optional environment variables ------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# -- Startup validation ------------------------------------------------------

_REQUIRED = {
    "WHATSAPP_TOKEN": WHATSAPP_TOKEN,
    "WHATSAPP_PHONE_NUMBER_ID": WHATSAPP_PHONE_NUMBER_ID,
    "WHATSAPP_VERIFY_TOKEN": WHATSAPP_VERIFY_TOKEN,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_KEY": SUPABASE_KEY,
}

_missing = [name for name, value in _REQUIRED.items() if not value]
if _missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        "Check your .env file or deployment config."
    )

# -- Supabase client ---------------------------------------------------------

from supabase import create_client, Client  # noqa: E402

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)