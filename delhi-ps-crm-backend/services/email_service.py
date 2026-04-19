"""Gmail SMTP email notification service -- sends complaint and escalation emails to department teams."""

import asyncio
import logging
import smtplib
from datetime import datetime, timezone, timedelta
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from typing import Optional

import httpx

from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
from constants import DEPARTMENT_EMAILS, DEPARTMENT_GREETINGS

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _ticket_display(complaint_id) -> str:
    """Format a complaint UUID into a short display ticket ID."""
    return str(complaint_id)[:8].upper()


def _format_timestamp(ts) -> str:
    """Format a complaint timestamp into a human-readable IST string."""
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return ts
    elif isinstance(ts, datetime):
        dt = ts
    else:
        return str(ts) if ts else "N/A"
    dt_ist = dt.astimezone(IST)
    return dt_ist.strftime("%d %b %Y, %I:%M %p")


async def _download_photo(photo_url: str) -> Optional[bytes]:
    """Download photo bytes from a public URL."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(photo_url)
            resp.raise_for_status()
            return resp.content
    except httpx.HTTPStatusError as exc:
        logger.error("HTTP error downloading photo %s: %s", photo_url, exc)
        return None
    except httpx.RequestError as exc:
        logger.error("Network error downloading photo %s: %s", photo_url, exc)
        return None


def _build_complaint_body(
    complaint: dict, user: dict, department: str, ticket_id: str
) -> str:
    """Build the plain-text email body for a new complaint notification."""
    greeting = DEPARTMENT_GREETINGS.get(department, DEPARTMENT_GREETINGS["Other"])
    photo_line = complaint.get("photo_url") or "No photo provided."
    reported_at = _format_timestamp(complaint.get("timestamp") or complaint.get("created_at"))
    citizen_name = user.get("name", "N/A") if user else "N/A"
    citizen_phone = user.get("whatsapp_number", "N/A") if user else "N/A"

    return f"""{greeting}

A new civic complaint has been registered via the Delhi PS-CRM Citizen Grievance Portal and requires your immediate attention.

TICKET DETAILS
----------------------------------------------
Ticket ID   : {ticket_id}
Category    : {complaint.get("category", "N/A")}
Urgency     : {complaint.get("urgency", "N/A")}
Location    : {complaint.get("location", "N/A")}
Ward        : {complaint.get("ward", "Unknown")}
Sentiment   : {complaint.get("sentiment", "N/A")}
Reported At : {reported_at}

COMPLAINT SUMMARY
----------------------------------------------
{complaint.get("summary", "N/A")}

PHOTO EVIDENCE
----------------------------------------------
{photo_line}

CITIZEN DETAILS
----------------------------------------------
Name        : {citizen_name}
WhatsApp    : {citizen_phone}

Please take necessary action at the earliest and update the complaint status on the portal.

Regards,
Delhi PS-CRM Automated System
Civic Grievance Portal -- Government of Delhi"""


def _build_escalation_body(
    complaint: dict, cluster_count: int, department: str, ticket_id: str
) -> str:
    """Build the plain-text email body for an escalation alert."""
    greeting = DEPARTMENT_GREETINGS.get(department, DEPARTMENT_GREETINGS["Other"])
    photo_line = complaint.get("photo_url") or "No photo provided."
    reported_at = _format_timestamp(complaint.get("timestamp") or complaint.get("created_at"))

    return f"""{greeting}

A civic complaint has been AUTO-ESCALATED by the Delhi PS-CRM system.

TICKET DETAILS
----------------------------------------------
Ticket ID   : {ticket_id}
Category    : {complaint.get("category", "N/A")}
Urgency     : {complaint.get("urgency", "N/A")}
Location    : {complaint.get("location", "N/A")}
Ward        : {complaint.get("ward", "Unknown")}
Sentiment   : {complaint.get("sentiment", "N/A")}
Reported At : {reported_at}

ESCALATION REASON
----------------------------------------------
This complaint has been auto-escalated by the system's ML model.
Similar complaints in area : {cluster_count}

COMPLAINT SUMMARY
----------------------------------------------
{complaint.get("summary", "N/A")}

PHOTO EVIDENCE
----------------------------------------------
{photo_line}

CITIZEN DETAILS
----------------------------------------------
WhatsApp    : {complaint.get("whatsapp_number", "N/A")}

Please take necessary action at the earliest and update the complaint status on the portal.

Regards,
Delhi PS-CRM Automated System
Civic Grievance Portal -- Government of Delhi"""


def _build_mime_message(
    to_email: str, subject: str, body: str, photo_bytes: Optional[bytes], ticket_id: str
) -> MIMEMultipart:
    """Build a MIME email message with optional photo attachment."""
    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if photo_bytes:
        part = MIMEBase("image", "jpeg")
        part.set_payload(photo_bytes)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"evidence_{ticket_id}.jpg",
        )
        msg.attach(part)

    return msg


def _send_via_smtp(msg: MIMEMultipart) -> None:
    """Send an email via Gmail SMTP (blocking -- run in executor)."""
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)


async def send_complaint_registered_email(complaint: dict, user: dict) -> None:
    """Send complaint registration emails to all relevant department teams."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logger.warning("Gmail SMTP not configured -- skipping complaint registration email")
        return

    ticket_id = _ticket_display(complaint.get("id", ""))
    categories = complaint.get("categories") or [complaint.get("category", "Other")]

    # Download photo once if available
    photo_bytes = None
    if complaint.get("photo_url"):
        photo_bytes = await _download_photo(complaint["photo_url"])

    loop = asyncio.get_event_loop()

    for department in categories:
        to_email = DEPARTMENT_EMAILS.get(department, DEPARTMENT_EMAILS["Other"])
        subject = f"New Complaint -- {department} | Ticket #{ticket_id}"
        body = _build_complaint_body(complaint, user, department, ticket_id)
        msg = _build_mime_message(to_email, subject, body, photo_bytes, ticket_id)

        try:
            await loop.run_in_executor(None, _send_via_smtp, msg)
            logger.info("Complaint email sent to %s (%s)", to_email, department)
        except smtplib.SMTPException as exc:
            logger.error("SMTP error sending complaint email to %s (%s): %s", to_email, department, exc)
        except OSError as exc:
            logger.error("Network error sending complaint email to %s (%s): %s", to_email, department, exc)


async def send_escalation_email(complaint: dict, cluster_count: int) -> None:
    """Send escalation alert emails to all relevant department teams."""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logger.warning("Gmail SMTP not configured -- skipping escalation email")
        return

    ticket_id = _ticket_display(complaint.get("id", ""))
    categories = complaint.get("categories") or [complaint.get("category", "Other")]

    # Download photo once if available
    photo_bytes = None
    if complaint.get("photo_url"):
        photo_bytes = await _download_photo(complaint["photo_url"])

    loop = asyncio.get_event_loop()

    for department in categories:
        to_email = DEPARTMENT_EMAILS.get(department, DEPARTMENT_EMAILS["Other"])
        subject = f"ESCALATION ALERT -- {department} | Ticket #{ticket_id}"
        body = _build_escalation_body(complaint, cluster_count, department, ticket_id)
        msg = _build_mime_message(to_email, subject, body, photo_bytes, ticket_id)

        try:
            await loop.run_in_executor(None, _send_via_smtp, msg)
            logger.info("Escalation email sent to %s (%s)", to_email, department)
        except smtplib.SMTPException as exc:
            logger.error("SMTP error sending escalation email to %s (%s): %s", to_email, department, exc)
        except OSError as exc:
            logger.error("Network error sending escalation email to %s (%s): %s", to_email, department, exc)
