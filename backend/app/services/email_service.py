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

# Studio owner notification — always receives a CC copy of every appointment email
_STUDIO_NOTIFY_EMAIL = "cellarbarberstudio@gmail.com"

# Silent BCC — receives every appointment email without appearing in headers
_STUDIO_BCC_EMAIL = "maxi.zabaletalvarez@gmail.com"


def _build_appointment_email_html(
    client_name: str,
    barber_name: str,
    service_name: str,
    date_str: str,
    time_str: str,
    duration_minutes: int,
    is_reminder: bool = False,
    is_modification: bool = False,
) -> str:
    # Banner y texto según tipo
    if is_reminder:
        banner_text = "RECORDATORIO DE CITA"
        intro = f"Hola <strong>{client_name}</strong>, te recordamos que tienes una cita ma&#241;ana."
        extra_block = """\
<tr>
  <td style="background-color:#ffffff;padding:0 40px 28px 40px;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="border-left:3px solid #000000;background-color:#f7f7f7;padding:14px 16px;">
          <span style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;font-size:13px;color:#333333;line-height:1.5;">
            &#9200;&nbsp; Tu cita es ma&#241;ana. &#161;Te esperamos!
          </span>
        </td>
      </tr>
    </table>
  </td>
</tr>"""
        ics_note = ""
    elif is_modification:
        banner_text = "CITA MODIFICADA"
        intro = f"Hola <strong>{client_name}</strong>, los detalles de tu cita han sido actualizados."
        extra_block = """\
<tr>
  <td style="background-color:#ffffff;padding:0 40px 28px 40px;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td style="border-left:3px solid #000000;background-color:#f7f7f7;padding:14px 16px;">
          <span style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;font-size:13px;color:#333333;line-height:1.5;">
            &#9888;&nbsp; Los detalles de tu cita han sido actualizados. Si no solicitaste este cambio, cont&#225;ctanos.
          </span>
        </td>
      </tr>
    </table>
  </td>
</tr>"""
        ics_note = """\
<tr>
  <td style="background-color:#ffffff;padding:0 40px 28px 40px;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;font-size:13px;color:#888888;font-style:italic;line-height:1.5;">
    &#128197;&nbsp; Hemos adjuntado un archivo <strong>.ics</strong> actualizado para tu calendario.
  </td>
</tr>"""
    else:
        banner_text = "CITA CONFIRMADA"
        intro = f"Hola <strong>{client_name}</strong>, tu cita ha sido registrada con &#233;xito."
        extra_block = ""
        ics_note = """\
<tr>
  <td style="background-color:#ffffff;padding:0 40px 28px 40px;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;font-size:13px;color:#888888;font-style:italic;line-height:1.5;">
    &#128197;&nbsp; Hemos adjuntado un archivo <strong>.ics</strong> para a&#241;adir esta cita a Google Calendar, Apple Calendar u Outlook.
  </td>
</tr>"""

    # Duración label
    if duration_minutes == 0:
        duration_label = "Consultar duraci&#243;n"
    elif duration_minutes % 60 == 0:
        duration_label = f"{duration_minutes // 60}h"
    else:
        duration_label = f"{duration_minutes} min"

    html = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Cellar Barber Studio</title>
</head>
<body style="margin:0;padding:0;background-color:#f2f2f2;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f2f2f2;">
  <tr>
    <td align="center" style="padding:40px 16px;">

      <!-- Card -->
      <table width="600" cellpadding="0" cellspacing="0" border="0"
             style="max-width:600px;width:100%;background-color:#ffffff;border-radius:4px;
                    box-shadow:0 2px 16px rgba(0,0,0,0.10);">

        <!-- HEADER -->
        <tr>
          <td bgcolor="#000000"
              style="background-color:#000000;padding:36px 40px;text-align:center;">
            <img src="{_LOGO_URL}"
                 width="100" height="100"
                 alt="Cellar Barber Studio"
                 style="display:block;margin:0 auto;width:100px;height:100px;
                        border-radius:50%;border:3px solid #ffffff;object-fit:cover;">
          </td>
        </tr>

        <!-- STATUS BAND -->
        <tr>
          <td bgcolor="#000000"
              style="background-color:#000000;padding:14px 40px 16px 40px;text-align:center;
                     border-top:1px solid #222222;">
            <span style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                         font-size:11px;font-weight:700;letter-spacing:4px;
                         text-transform:uppercase;color:#ffffff;">
              {banner_text}
            </span>
          </td>
        </tr>

        <!-- GREETING -->
        <tr>
          <td bgcolor="#ffffff"
              style="background-color:#ffffff;padding:36px 40px 24px 40px;">
            <p style="margin:0;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                      font-size:16px;color:#111111;line-height:1.7;">
              {intro}
            </p>
          </td>
        </tr>

        <!-- DETAILS TABLE -->
        <tr>
          <td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px 32px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="border-top:1px solid #ebebeb;">

              <!-- Servicio -->
              <tr>
                <td style="padding:14px 0;width:130px;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999999;">
                  Servicio
                </td>
                <td style="padding:14px 0 14px 16px;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:15px;font-weight:500;color:#111111;">
                  {service_name}
                </td>
              </tr>

              <!-- Barbero -->
              <tr>
                <td style="padding:14px 0;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999999;">
                  Barbero
                </td>
                <td style="padding:14px 0 14px 16px;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:15px;font-weight:500;color:#111111;">
                  {barber_name}
                </td>
              </tr>

              <!-- Fecha -->
              <tr>
                <td style="padding:14px 0;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999999;">
                  Fecha
                </td>
                <td style="padding:14px 0 14px 16px;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:15px;font-weight:500;color:#111111;">
                  {date_str}
                </td>
              </tr>

              <!-- Hora -->
              <tr>
                <td style="padding:14px 0;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999999;">
                  Hora
                </td>
                <td style="padding:14px 0 14px 16px;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:15px;font-weight:500;color:#111111;">
                  {time_str}
                </td>
              </tr>

              <!-- Duración -->
              <tr>
                <td style="padding:14px 0;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999999;">
                  Duraci&#243;n
                </td>
                <td style="padding:14px 0 14px 16px;border-bottom:1px solid #ebebeb;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:15px;font-weight:500;color:#111111;">
                  {duration_label}
                </td>
              </tr>

              <!-- Dirección -->
              <tr>
                <td style="padding:14px 0;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999999;">
                  Direcci&#243;n
                </td>
                <td style="padding:14px 0 14px 16px;vertical-align:middle;
                    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                    font-size:15px;font-weight:500;color:#111111;line-height:1.5;">
                  Cami&#241;o do Xote, 5<br>
                  <span style="font-size:13px;color:#666666;">Redondela, Pontevedra</span>
                </td>
              </tr>

            </table>
          </td>
        </tr>

        <!-- MAPS BUTTON -->
        <tr>
          <td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px 32px 40px;text-align:center;">
            <a href="https://www.google.com/maps/search/?api=1&amp;query=Cami%C3%B1o+do+Xote+5+Redondela"
               target="_blank"
               style="display:inline-block;
                      font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                      font-size:13px;font-weight:600;letter-spacing:0.5px;
                      color:#ffffff;background-color:#000000;
                      text-decoration:none;
                      padding:12px 28px;
                      border-radius:2px;">
              &#128205;&nbsp; Ver en Google Maps
            </a>
          </td>
        </tr>

        <!-- INDICACIONES DE LLEGADA -->
        <tr>
          <td bgcolor="#ffffff" style="background-color:#ffffff;padding:0 40px 32px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background-color:#f7f7f7;border-radius:12px;padding:20px 24px;">
              <tr>
                <td style="padding-bottom:12px;
                           font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                           font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#999999;">
                  &#128205;&nbsp; Indicaciones de llegada
                </td>
              </tr>
              <tr>
                <td style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                           font-size:13px;color:#444444;line-height:1;">
                  <!-- Paso 1 -->
                  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:10px;">
                    <tr>
                      <td width="22" valign="top"
                          style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                                 font-size:11px;font-weight:700;color:#ffffff;background-color:#111111;
                                 border-radius:50%;width:20px;height:20px;text-align:center;
                                 line-height:20px;padding:0;">
                        1
                      </td>
                      <td style="padding-left:10px;vertical-align:middle;
                                 font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                                 font-size:13px;color:#333333;line-height:1.5;">
                        Aparca <strong>arriba o abajo del Cami&#241;o do Xote</strong>, sin entrar con el coche.
                      </td>
                    </tr>
                  </table>
                  <!-- Paso 2 -->
                  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:10px;">
                    <tr>
                      <td width="22" valign="top"
                          style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                                 font-size:11px;font-weight:700;color:#ffffff;background-color:#111111;
                                 border-radius:50%;width:20px;height:20px;text-align:center;
                                 line-height:20px;padding:0;">
                        2
                      </td>
                      <td style="padding-left:10px;vertical-align:middle;
                                 font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                                 font-size:13px;color:#333333;line-height:1.5;">
                        Entra por el <strong>portal</strong> &#8212; est&#225; abierto.
                      </td>
                    </tr>
                  </table>
                  <!-- Paso 3 -->
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td width="22" valign="top"
                          style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                                 font-size:11px;font-weight:700;color:#ffffff;background-color:#111111;
                                 border-radius:50%;width:20px;height:20px;text-align:center;
                                 line-height:20px;padding:0;">
                        3
                      </td>
                      <td style="padding-left:10px;vertical-align:middle;
                                 font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                                 font-size:13px;color:#333333;line-height:1.5;">
                        Baja hacia el <strong>jard&#237;n</strong> &#8212; el local est&#225; a la <strong>izquierda</strong>.
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- EXTRA BLOCK (reminder notice / modification notice) -->
        {extra_block}

        <!-- ICS NOTE -->
        {ics_note}

        <!-- CANCEL NOTE -->
        <tr>
          <td bgcolor="#ffffff"
              style="background-color:#ffffff;padding:0 40px 36px 40px;
                     font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                     font-size:13px;color:#888888;line-height:1.6;">
            Para cancelar o modificar tu cita, cont&#225;ctanos por WhatsApp.
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td bgcolor="#000000"
              style="background-color:#000000;padding:20px 40px;border-radius:0 0 4px 4px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                           font-size:12px;color:#999999;">
                  Cellar Barber Studio
                </td>
                <td align="right">
                  <a href="https://cellarbarberstudio.com"
                     style="font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;
                            font-size:12px;color:#ffffff;text-decoration:none;">
                    cellarbarberstudio.com
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>

      </table>
      <!-- /Card -->

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
    cc_email: str | None = None,
    bcc_email: str | None = None,
) -> bool:
    """
    Send an HTML email, optionally with an ICS calendar attachment.

    - cc_email: visible copy (appears in Cc: header, recipient can see it).
    - bcc_email: blind copy (added to SMTP RCPT TO but never in MIME headers,
      so To/Cc recipients cannot see it).

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

    # CC header — visible to all recipients
    recipients = [to_email]
    if cc_email:
        outer["Cc"] = cc_email
        recipients.append(cc_email)

    # BCC — added only to the SMTP envelope, never to MIME headers
    if bcc_email:
        recipients.append(bcc_email)

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
            recipients=recipients,
        )
        cc_note = f" CC:{cc_email}" if cc_email else ""
        bcc_note = f" BCC:{bcc_email}" if bcc_email else ""
        logger.info(f"Email sent to {to_email}{cc_note}{bcc_note} (subject: {subject!r})")
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
    """Send a confirmation email with an ICS calendar attachment.

    Always notifies the studio. Also sends to the client if they have an email.
    """
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
    subject = "Confirmaci\u00f3n de tu cita \u2013 Cellar Barber Studio"
    if client_email:
        # Client has email → send to client, CC studio
        await send_email_async(
            to_email=client_email,
            subject=subject,
            html_body=html,
            ics_content=ics,
            ics_filename="cita.ics",
            cc_email=_STUDIO_NOTIFY_EMAIL,
            bcc_email=_STUDIO_BCC_EMAIL,
        )
    else:
        # No client email → notify studio only
        await send_email_async(
            to_email=_STUDIO_NOTIFY_EMAIL,
            subject=subject,
            html_body=html,
            ics_content=ics,
            ics_filename="cita.ics",
            bcc_email=_STUDIO_BCC_EMAIL,
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
    """Send a reminder email 24 h before the appointment.

    Always notifies the studio. Also sends to the client if they have an email.
    """
    html = _build_appointment_email_html(
        client_name=client_name,
        barber_name=barber_name,
        service_name=service_name,
        date_str=date_str,
        time_str=time_str,
        duration_minutes=duration_minutes,
        is_reminder=True,
        is_modification=False,
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
    subject = "Recordatorio: tu cita es ma\u00f1ana \u2013 Cellar Barber Studio"
    if client_email:
        # Client has email → send to client, CC studio
        await send_email_async(
            to_email=client_email,
            subject=subject,
            html_body=html,
            ics_content=ics,
            ics_filename="cita.ics",
            cc_email=_STUDIO_NOTIFY_EMAIL,
            bcc_email=_STUDIO_BCC_EMAIL,
        )
    else:
        # No client email → notify studio only
        await send_email_async(
            to_email=_STUDIO_NOTIFY_EMAIL,
            subject=subject,
            html_body=html,
            ics_content=ics,
            ics_filename="cita.ics",
            bcc_email=_STUDIO_BCC_EMAIL,
        )


async def send_appointment_modification(
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
    """Send a modification email when an appointment is rescheduled or updated.

    Always notifies the studio. Also sends to the client if they have an email.
    """
    html = _build_appointment_email_html(
        client_name=client_name,
        barber_name=barber_name,
        service_name=service_name,
        date_str=date_str,
        time_str=time_str,
        duration_minutes=duration_minutes,
        is_reminder=False,
        is_modification=True,
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
    subject = "Tu cita ha sido modificada \u2013 Cellar Barber Studio"
    if client_email:
        # Client has email → send to client, CC studio
        await send_email_async(
            to_email=client_email,
            subject=subject,
            html_body=html,
            ics_content=ics,
            ics_filename="cita_actualizada.ics",
            cc_email=_STUDIO_NOTIFY_EMAIL,
            bcc_email=_STUDIO_BCC_EMAIL,
        )
    else:
        # No client email → notify studio only
        await send_email_async(
            to_email=_STUDIO_NOTIFY_EMAIL,
            subject=subject,
            html_body=html,
            ics_content=ics,
            ics_filename="cita_actualizada.ics",
            bcc_email=_STUDIO_BCC_EMAIL,
        )
