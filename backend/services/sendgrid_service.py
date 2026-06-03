import asyncio
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import settings

logger = logging.getLogger(__name__)


def _send_sync(patient_id: str, triggering_message: str, to_email: str) -> None:
    recipient = to_email.strip() or settings.alert_recipient_email
    message = Mail(
        from_email=settings.sendgrid_from_email,
        to_emails=recipient,
        subject=f"EMERGENCY ALERT — Patient {patient_id}",
        html_content=(
            f"<h2>Emergency Triage Alert</h2>"
            f"<p><strong>Patient ID:</strong> {patient_id}</p>"
            f"<p><strong>Triggering message:</strong></p>"
            f"<blockquote>{triggering_message}</blockquote>"
            f"<p>This patient has been classified as <strong>Level 3 — Emergency</strong>. "
            f"Immediate action is required.</p>"
        ),
    )
    sg = SendGridAPIClient(settings.sendgrid_api_key.strip())
    response = sg.send(message)
    logger.info(
        "SendGrid response: status=%s body=%s",
        response.status_code,
        response.body,
    )
    if response.status_code not in (200, 202):
        raise RuntimeError(
            f"SendGrid rejected email: status {response.status_code} — {response.body}"
        )


async def send_emergency_alert(patient_id: str, triggering_message: str, to_email: str = "") -> None:
    await asyncio.to_thread(_send_sync, patient_id, triggering_message, to_email)
