"""Scheduled escalation cron job -- checks open complaints and auto-escalates using the ML model."""

import logging
from collections import Counter

from config import HOD_WHATSAPP_NUMBER, supabase
from services.escalation import predict_escalation
from services.email_service import send_escalation_email
from services.whatsapp import send_message

logger = logging.getLogger(__name__)


def _ticket_display(complaint_id) -> str:
    """Format a complaint UUID into a short human-readable ticket ID."""
    return str(complaint_id)[:8].upper()


async def run_escalation_check() -> None:
    """Run the periodic escalation check across all unresolved complaints."""
    logger.info("Starting escalation check")
    try:
        all_rows = (
            supabase.table("raw_complaints")
            .select("category, location")
            .execute()
            .data
            or []
        )
        cluster_keys = [
            ((r.get("category") or ""), (r.get("location") or "")) for r in all_rows
        ]
        cluster_counts = Counter(cluster_keys)

        pending = (
            supabase.table("raw_complaints")
            .select("*")
            .neq("status", "resolved")
            .execute()
            .data
            or []
        )

        escalated_count = 0
        for row in pending:
            st = (row.get("status") or "").strip().lower()
            if st == "escalated":
                continue

            category = row.get("category") or ""
            location = row.get("location") or ""
            urgency = row.get("urgency") or "Medium"
            status_for_model = row.get("status") or "open"
            cid = row["id"]

            key = (category, location)
            cluster_count = cluster_counts.get(key, 0)

            if predict_escalation(status_for_model, urgency, cluster_count) != 1:
                continue

            supabase.table("raw_complaints").update({"status": "escalated"}).eq(
                "id", cid
            ).execute()

            tid = _ticket_display(cid)

            # Send WhatsApp notification to citizen
            wn = row.get("whatsapp_number")
            if wn:
                msg = (
                    f"Your complaint {tid} regarding {category} in {location} "
                    f"has been escalated due to high priority."
                )
                await send_message(wn, msg)

            # Send WhatsApp notification to HoD (if configured)
            if HOD_WHATSAPP_NUMBER:
                hod_msg = (
                    "ESCALATION ALERT\n\n"
                    f"Ticket   : {tid}\n"
                    f"Category : {category}\n"
                    f"Location : {location}\n"
                    f"Ward     : {row.get('ward', 'Unknown')}\n"
                    f"Urgency  : {urgency}\n"
                    f"Similar complaints in area : {cluster_count}\n\n"
                    "This complaint has been auto-escalated by the ML model and requires immediate attention."
                )
                await send_message(HOD_WHATSAPP_NUMBER, hod_msg)

            # Send escalation email to all relevant departments
            try:
                await send_escalation_email(row, cluster_count)
            except Exception as exc:
                logger.error("Escalation email failed for complaint %s: %s", cid, exc)

            escalated_count += 1

        logger.info("Escalation check complete: %d complaints escalated", escalated_count)
    except Exception:
        logger.exception("run_escalation_check failed")
