"""Phone number handling.

`clients.phone` is the de-facto identity key of a client across the whole app:
the public booking flow does find-or-create by phone, and push subscriptions
and in-app notifications are keyed by the phone string. Numbers are stored as
the user typed them, so every lookup must compare *normalized* forms —
otherwise "+34 600 111 222" and "600111222" become two different people, and a
client registered by hand in the admin never links up with their own online
bookings.
"""

import re

from sqlalchemy import func

_NON_DIGITS = re.compile(r"\D")

# Length of a Spanish subscriber number. Comparing only the tail makes lookups
# immune to the country prefix being present, absent, or written as 0034.
LOCAL_DIGITS = 9


def normalize_phone(raw: str | None) -> str:
    """Return only the digits of a phone number."""
    return _NON_DIGITS.sub("", raw or "")


def phone_matches(column, raw: str | None):
    """SQLAlchemy predicate: `column` is the same number as `raw`, any format.

    Compares digits only, and for full-length numbers only the last
    ``LOCAL_DIGITS`` digits, so 600111222 == "600 111 222" == "+34 600 111 222"
    == "0034600111222". Postgres-specific (``regexp_replace``/``right``), which
    is the only backend this app runs on.
    """
    digits = normalize_phone(raw)
    col_digits = func.regexp_replace(column, r"[^0-9]", "", "g")
    if len(digits) >= LOCAL_DIGITS:
        return func.right(col_digits, LOCAL_DIGITS) == digits[-LOCAL_DIGITS:]
    return col_digits == digits
