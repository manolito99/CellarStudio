"""WhatsApp service for sending appointment notifications via Meta Cloud API."""

import logging
import re
import threading

import requests

from app.config import settings

logger = logging.getLogger(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v21.0/{phone_number_id}/messages"


def format_phone_for_whatsapp(phone: str) -> str:
    """Normalize a Spanish phone number to international format (34XXXXXXXXX)."""
    digits = re.sub(r"\D", "", phone)

    # Already has country code 34 (e.g. 34612345678)
    if digits.startswith("34") and len(digits) == 11:
        return digits

    # 9-digit local number (e.g. 612345678)
    if len(digits) == 9:
        return f"34{digits}"

    return digits


def _send_whatsapp(to_phone: str, message: str) -> bool:
    """Send a WhatsApp text message via Meta Cloud API. Returns True on success."""
    if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_ACCESS_TOKEN:
        logger.warning("WhatsApp not configured, skipping send")
        return False

    url = GRAPH_API_URL.format(phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID)
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": format_phone_for_whatsapp(to_phone),
        "type": "text",
        "text": {"body": message},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        data = resp.json()

        if resp.ok:
            msg_id = data.get("messages", [{}])[0].get("id", "unknown")
            logger.info(f"WhatsApp sent to {to_phone} (ID: {msg_id})")
            return True
        else:
            error = data.get("error", {}).get("message", resp.text)
            logger.error(f"Failed to send WhatsApp to {to_phone}: {error}")
            return False
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {to_phone}: {e}")
        return False


def _send_in_background(to_phone: str, message: str) -> None:
    """Fire-and-forget: run _send_whatsapp in a daemon thread."""
    thread = threading.Thread(target=_send_whatsapp, args=(to_phone, message), daemon=True)
    thread.start()


def send_appointment_whatsapp(
    client_phone: str,
    client_name: str,
    barber_name: str,
    service_name: str,
    date_str: str,
    time_str: str,
) -> None:
    """Fire-and-forget WhatsApp confirmation for a new appointment."""
    if not client_phone:
        return

    message = (
        f"Hola {client_name}! Tu cita en Cellar Barber Studio ha sido registrada:\n\n"
        f"Servicio: {service_name}\n"
        f"Barbero: {barber_name}\n"
        f"Fecha: {date_str}\n"
        f"Hora: {time_str}\n\n"
        f"Si necesitas cancelar o modificar, contáctanos por WhatsApp."
    )

    _send_in_background(client_phone, message)


def send_status_change_whatsapp(
    client_phone: str,
    client_name: str,
    status: str,
    date_str: str,
    time_str: str,
) -> None:
    """Fire-and-forget WhatsApp notification for appointment status change."""
    if not client_phone:
        return

    status_messages = {
        "confirmed": f"Hola {client_name}! Tu cita del {date_str} a las {time_str} ha sido *confirmada*. ¡Te esperamos en Cellar Barber Studio!",
        "cancelled": f"Hola {client_name}, tu cita del {date_str} a las {time_str} ha sido *cancelada*. Si quieres reprogramar, reserva desde nuestra web.",
        "noshow": f"Hola {client_name}, registramos que no pudiste asistir a tu cita del {date_str} a las {time_str}. Reserva una nueva cita cuando quieras.",
        "completed": f"Hola {client_name}! Gracias por visitarnos hoy en Cellar Barber Studio. ¡Hasta la próxima!",
    }

    message = status_messages.get(status)
    if not message:
        return

    _send_in_background(client_phone, message)


def send_reminder_whatsapp(
    client_phone: str,
    client_name: str,
    barber_name: str,
    service_name: str,
    date_str: str,
    time_str: str,
) -> None:
    """Fire-and-forget WhatsApp reminder before appointment."""
    if not client_phone:
        return

    message = (
        f"Hola {client_name}! Te recordamos tu cita de hoy en Cellar Barber Studio:\n\n"
        f"Servicio: {service_name}\n"
        f"Barbero: {barber_name}\n"
        f"Hora: {time_str}\n\n"
        f"¡Te esperamos!"
    )

    _send_in_background(client_phone, message)
