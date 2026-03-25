"""Email service for sending appointment confirmations and reminders.

Generates professional HTML emails with an ICS calendar attachment (RFC 5545)
so clients can add their appointment directly to Google/Apple Calendar.
"""

import asyncio
import datetime
import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ICS calendar attachment builder (no external deps — pure RFC 5545)
# ---------------------------------------------------------------------------

# Full VTIMEZONE block for Europe/Madrid with CET (winter) and CEST (summer)
# Required for Outlook and older iOS clients that don't trust TZID alone.
_VTIMEZONE_MADRID = """\
BEGIN:VTIMEZONE\r
TZID:Europe/Madrid\r
BEGIN:STANDARD\r
TZOFFSETFROM:+0200\r
TZOFFSETTO:+0100\r
TZNAME:CET\r
DTSTART:19701025T030000\r
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10\r
END:STANDARD\r
BEGIN:DAYLIGHT\r
TZOFFSETFROM:+0100\r
TZOFFSETTO:+0200\r
TZNAME:CEST\r
DTSTART:19700329T020000\r
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3\r
END:DAYLIGHT\r
END:VTIMEZONE\r
"""


def _fmt_ics_dt(d: datetime.date, t: datetime.time) -> str:
    """Format a date+time as ICS local datetime string: YYYYMMDDTHHMMSS."""
    return f"{d.strftime('%Y%m%d')}T{t.strftime('%H%M%S')}"


def _build_ics_content(
    appointment_id: str,
    client_name: str,
    barber_name: str,
    service_name: str,
    date_obj: datetime.date,
    start_time_obj: datetime.time,
    end_time_obj: datetime.time,
    duration_minutes: int,
) -> str:
    """Build a minimal but standards-compliant ICS calendar event string."""
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = f"{appointment_id}@cellarstudio.com"
    dtstart = _fmt_ics_dt(date_obj, start_time_obj)
    dtend = _fmt_ics_dt(date_obj, end_time_obj)
    summary = f"Cita en Cellar Barber Studio \u2013 {service_name}"
    description = (
        f"Barbero: {barber_name}\\nServicio: {service_name}\\nCliente: {client_name}"
    )
    organizer_email = settings.SMTP_USER or "noreply@cellarstudio.com"

    lines = [
        "BEGIN:VCALENDAR\r\n",
        "VERSION:2.0\r\n",
        "PRODID:-//Cellar Barber Studio//Appointments//ES\r\n",
        "METHOD:REQUEST\r\n",
        _VTIMEZONE_MADRID,
        "BEGIN:VEVENT\r\n",
        f"UID:{uid}\r\n",
        f"DTSTAMP:{now_utc}\r\n",
        f"DTSTART;TZID=Europe/Madrid:{dtstart}\r\n",
        f"DTEND;TZID=Europe/Madrid:{dtend}\r\n",
        f"SUMMARY:{summary}\r\n",
        f"DESCRIPTION:{description}\r\n",
        "LOCATION:Cellar Barber Studio\r\n",
        "STATUS:CONFIRMED\r\n",
        f"ORGANIZER;CN=Cellar Barber Studio:mailto:{organizer_email}\r\n",
        "END:VEVENT\r\n",
        "END:VCALENDAR\r\n",
    ]
    return "".join(lines)


# ---------------------------------------------------------------------------
# HTML email template builder
# ---------------------------------------------------------------------------

# Logo URL hosted on the production server (referenced in email — no base64 needed)
_LOGO_URL = "https://cellarbarberstudio.com/icons/CellarStudio_Logo.png"


def _build_appointment_email_html(
    client_name: str,
    barber_name: str,
    service_name: str,
    date_str: str,
    time_str: str,
    duration_minutes: int,
    is_reminder: bool = False,
) -> str:
    """
    Build a professional, email-client-safe HTML body.

    Uses only inline CSS and <table> layout for maximum compatibility with
    Gmail, Outlook, Apple Mail and mobile clients.
    """
    if is_reminder:
        banner_text = "RECORDATORIO DE TU CITA"
        intro = (
            f"Hola <strong>{client_name}</strong>, te recordamos que tienes una cita mañana:"
        )
        reminder_banner = """\
<tr>
  <td style="padding:0 32px 24px 32px;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td bgcolor="#FEF3C7" style="background-color:#FEF3C7;border-left:4px solid #A66B4C;padding:14px 18px;border-radius:4px;">
          <span style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#92400E;">
            &#9200; Tu cita es ma&#241;ana. &#161;Te esperamos!
          </span>
        </td>
      </tr>
    </table>
  </td>
</tr>"""
        ics_note = ""
    else:
        banner_text = "&#161;CITA CONFIRMADA!"
        intro = f"Hola <strong>{client_name}</strong>, tu cita ha sido registrada con &#233;xito:"
        reminder_banner = ""
        ics_note = """\
<tr>
  <td style="padding:0 32px 24px 32px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#595959;">
    &#128197; Hemos adjuntado un archivo <strong>.ics</strong> para que puedas a&#241;adir esta cita directamente a Google Calendar, Apple Calendar u Outlook.
  </td>
</tr>"""

    duration_label = (
        f"{duration_minutes} min"
        if duration_minutes % 60 != 0 or duration_minutes == 0
        else f"{duration_minutes // 60}h"
    )
    if duration_minutes == 0:
        duration_label = "Consultar duración"

    html = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Cellar Barber Studio</title>
</head>
<body style="margin:0;padding:0;background-color:#e8e6df;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#e8e6df;">
  <tr>
    <td align="center" style="padding:32px 16px;">

      <!-- Email card -->
      <table width="600" cellpadding="0" cellspacing="0" border="0"
             style="max-width:600px;width:100%;border-radius:8px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.12);">

        <!-- HEADER — dark background with circular logo -->
        <tr>
          <td bgcolor="#0d0d0d" style="background-color:#0d0d0d;padding:32px 40px;text-align:center;">
            <!--[if mso]>
            <table cellpadding="0" cellspacing="0" border="0" align="center"><tr><td style="border-radius:50%;background:#ffffff;padding:4px;">
            <![endif]-->
            <img src="{_LOGO_URL}"
                 width="110" height="110"
                 alt="Cellar Barber Studio"
                 style="display:block;margin:0 auto;
                        width:110px;height:110px;
                        border-radius:50%;
                        border:3px solid #A66B4C;
                        object-fit:cover;">
            <!--[if mso]></td></tr></table><![endif]-->
          </td>
        </tr>

        <!-- SUB-HEADER — accent color with status label -->
        <tr>
          <td bgcolor="#A66B4C" style="background-color:#A66B4C;padding:12px 40px;text-align:center;">
            <span style="font-family:Arial,Helvetica,sans-serif;font-size:12px;font-weight:bold;
                         letter-spacing:3px;text-transform:uppercase;color:#ffffff;">
              {banner_text}
            </span>
          </td>
        </tr>

        <!-- BODY — light background -->
        <tr>
          <td bgcolor="#F2F0E9" style="background-color:#F2F0E9;padding:32px 40px 8px 40px;">
            <p style="margin:0 0 20px 0;font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#2B2E2E;line-height:1.6;">
              {intro}
            </p>
          </td>
        </tr>

        <!-- DETAILS TABLE -->
        <tr>
          <td bgcolor="#F2F0E9" style="background-color:#F2F0E9;padding:0 32px 24px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="border-radius:6px;overflow:hidden;border:1px solid #e0ddd6;">
              <!-- Servicio -->
              <tr>
                <td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 18px;width:120px;
                    font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:bold;
                    letter-spacing:1px;text-transform:uppercase;color:#595959;border-bottom:1px solid #f0ede6;">
                  Servicio
                </td>
                <td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#2B2E2E;
                    border-bottom:1px solid #f0ede6;">
                  {service_name}
                </td>
              </tr>
              <!-- Barbero -->
              <tr>
                <td bgcolor="#fafaf8" style="background-color:#fafaf8;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:bold;
                    letter-spacing:1px;text-transform:uppercase;color:#595959;border-bottom:1px solid #f0ede6;">
                  Barbero
                </td>
                <td bgcolor="#fafaf8" style="background-color:#fafaf8;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#2B2E2E;
                    border-bottom:1px solid #f0ede6;">
                  {barber_name}
                </td>
              </tr>
              <!-- Fecha -->
              <tr>
                <td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:bold;
                    letter-spacing:1px;text-transform:uppercase;color:#595959;border-bottom:1px solid #f0ede6;">
                  Fecha
                </td>
                <td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#2B2E2E;
                    border-bottom:1px solid #f0ede6;">
                  {date_str}
                </td>
              </tr>
              <!-- Hora -->
              <tr>
                <td bgcolor="#fafaf8" style="background-color:#fafaf8;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:bold;
                    letter-spacing:1px;text-transform:uppercase;color:#595959;border-bottom:1px solid #f0ede6;">
                  Hora
                </td>
                <td bgcolor="#fafaf8" style="background-color:#fafaf8;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#2B2E2E;
                    border-bottom:1px solid #f0ede6;">
                  {time_str}
                </td>
              </tr>
              <!-- Duración -->
              <tr>
                <td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:bold;
                    letter-spacing:1px;text-transform:uppercase;color:#595959;">
                  Duraci&#243;n
                </td>
                <td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 18px;
                    font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#2B2E2E;">
                  {duration_label}
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- REMINDER BANNER (only for reminders) -->
        {reminder_banner}

        <!-- ICS NOTE (only for confirmations) -->
        {ics_note}

        <!-- CANCEL NOTE -->
        <tr>
          <td bgcolor="#F2F0E9" style="background-color:#F2F0E9;padding:0 32px 32px 32px;
              font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#595959;line-height:1.6;">
            Para cancelar o modificar tu cita, cont&#225;ctanos por WhatsApp.
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td bgcolor="#0d0d0d" style="background-color:#0d0d0d;padding:20px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#888888;">
                  Cellar Barber Studio
                </td>
                <td align="right" style="font-family:Arial,Helvetica,sans-serif;font-size:12px;">
                  <a href="https://cellarbarberstudio.com"
                     style="color:#A66B4C;text-decoration:none;">
                    cellarbarberstudio.com
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

      </table>
      <!-- /Email card -->

    </td>
  </tr>
</table>
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# Core send helper — supports optional ICS attachment
# ---------------------------------------------------------------------------


async def send_email_async(
    to_email: str,
    subject: str,
    html_body: str,
    ics_content: str | None = None,
    ics_filename: str = "cita.ics",
) -> bool:
    """
    Send an HTML email, optionally with an ICS calendar attachment.

    Returns True on success, False on failure (never raises).
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured, skipping email send")
        return False

    # Build MIME tree
    outer = MIMEMultipart("mixed")
    outer["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
    outer["To"] = to_email
    outer["Subject"] = subject

    # Inner alternative part (HTML only — we skip plain-text for brevity)
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    outer.attach(alt)

    # ICS attachment
    if ics_content:
        ics_bytes = ics_content.encode("utf-8")
        ics_part = MIMEApplication(ics_bytes, _subtype="octet-stream")
        ics_part.replace_header("Content-Type", 'text/calendar; charset="utf-8"; method=REQUEST')
        ics_part.add_header("Content-Disposition", f'attachment; filename="{ics_filename}"')
        outer.attach(ics_part)

    try:
        await aiosmtplib.send(
            outer,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"Email sent to {to_email} (subject: {subject!r})")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def send_appointment_confirmation(
    client_name: str,
    client_email: str,
    barber_name: str,
    service_name: str,
    date_str: str,
    time_str: str,
    appointment_id: str,
    date_obj: datetime.date,
    start_time_obj: datetime.time,
    end_time_obj: datetime.time,
    duration_minutes: int,
) -> None:
    """Send a confirmation email with an ICS calendar attachment."""
    if not client_email:
        return

    html = _build_appointment_email_html(
        client_name=client_name,
        barber_name=barber_name,
        service_name=service_name,
        date_str=date_str,
        time_str=time_str,
        duration_minutes=duration_minutes,
        is_reminder=False,
    )
    ics = _build_ics_content(
        appointment_id=appointment_id,
        client_name=client_name,
        barber_name=barber_name,
        service_name=service_name,
        date_obj=date_obj,
        start_time_obj=start_time_obj,
        end_time_obj=end_time_obj,
        duration_minutes=duration_minutes,
    )
    await send_email_async(
        to_email=client_email,
        subject="Confirmaci\u00f3n de tu cita \u2013 Cellar Barber Studio",
        html_body=html,
        ics_content=ics,
        ics_filename="cita.ics",
    )


async def send_appointment_reminder(
    client_name: str,
    client_email: str,
    barber_name: str,
    service_name: str,
    date_str: str,
    time_str: str,
    appointment_id: str,
    date_obj: datetime.date,
    start_time_obj: datetime.time,
    end_time_obj: datetime.time,
    duration_minutes: int,
) -> None:
    """Send a reminder email 24 h before the appointment."""
    if not client_email:
        return

    html = _build_appointment_email_html(
        client_name=client_name,
        barber_name=barber_name,
        service_name=service_name,
        date_str=date_str,
        time_str=time_str,
        duration_minutes=duration_minutes,
        is_reminder=True,
    )
    ics = _build_ics_content(
        appointment_id=appointment_id,
        client_name=client_name,
        barber_name=barber_name,
        service_name=service_name,
        date_obj=date_obj,
        start_time_obj=start_time_obj,
        end_time_obj=end_time_obj,
        duration_minutes=duration_minutes,
    )
    await send_email_async(
        to_email=client_email,
        subject="Recordatorio: tu cita es ma\u00f1ana \u2013 Cellar Barber Studio",
        html_body=html,
        ics_content=ics,
        ics_filename="cita.ics",
    )
