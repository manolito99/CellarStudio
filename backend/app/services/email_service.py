"""Email service for sending appointment confirmations and reminders."""

import asyncio
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email_async(to_email: str, subject: str, html_body: str) -> bool:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured, skipping email send")
        return False

    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_appointment_confirmation(
    client_name: str,
    client_email: str,
    barber_name: str,
    service_name: str,
    date_str: str,
    time_str: str,
) -> None:
    if not client_email:
        return

    subject = "Confirmación de tu cita - Cellar Studio"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #F2F0E9; color: #2B2E2E; padding: 30px; border-radius: 10px;">
        <h1 style="color: #A66B4C; text-align: center;">Cellar Studio</h1>
        <h2 style="text-align: center;">¡Cita confirmada!</h2>
        <p>Hola <strong>{client_name}</strong>,</p>
        <p>Tu cita ha sido registrada con éxito:</p>
        <div style="background: #ffffff; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #d1d1d1;">
            <p><strong>Servicio:</strong> {service_name}</p>
            <p><strong>Barbero:</strong> {barber_name}</p>
            <p><strong>Fecha:</strong> {date_str}</p>
            <p><strong>Hora:</strong> {time_str}</p>
        </div>
        <p>Si necesitas cancelar o modificar tu cita, contáctanos por WhatsApp.</p>
        <p style="color: #595959; font-size: 12px; text-align: center; margin-top: 30px;">
            Cellar Studio Barbería
        </p>
    </div>
    """

    try:
        asyncio.get_event_loop().create_task(send_email_async(client_email, subject, html))
    except RuntimeError:
        pass
