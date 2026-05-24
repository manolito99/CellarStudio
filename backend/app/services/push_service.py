import json
import logging

from pywebpush import WebPushException, webpush

from app.config import settings

logger = logging.getLogger(__name__)


def send_push_notification(
    subscription_info: dict,
    title: str,
    body: str,
    icon: str = "/icons/CellarStudio_Logo.png",
) -> bool | None:
    """Send a Web Push notification.

    Returns True on success, False on transient error, None if the
    subscription is gone (caller should delete it).
    """
    if not settings.VAPID_PRIVATE_KEY:
        logger.warning("VAPID_PRIVATE_KEY not configured — skipping push")
        return False

    payload = json.dumps(
        {
            "title": title,
            "body": body,
            "icon": icon,
            "badge": icon,
            "data": {"url": "/"},
        }
    )

    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIMS_EMAIL}"},
        )
        return True
    except WebPushException as exc:
        logger.error(f"Push failed: {exc}")
        if exc.response is not None and exc.response.status_code in (404, 410):
            return None
        return False
