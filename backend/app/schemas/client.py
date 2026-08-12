import datetime as dt
from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, EmailStr, Field, StringConstraints

from app.services.phone import normalize_phone

# Write-side constraints. They live on the Create/Update schemas and NOT on
# ClientBase on purpose: ClientBase is also the read model (ClientResponse and
# the client block embedded in appointment responses), and legacy rows created
# before validation existed would fail response serialization -> 500.

_PHONE_CHARS = set("0123456789 +-().")
MIN_PHONE_DIGITS = 6


def _no_control_chars(value: str) -> str:
    # Control characters are not just cosmetic: a NUL byte makes psycopg2 raise
    # on commit (500 instead of 422), and a newline breaks the CSV export.
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("no puede contener saltos de línea ni caracteres de control")
    return value


def _plain_text(value: str) -> str:
    # Same as above but newlines and tabs are legitimate in a notes field.
    if any((ord(c) < 32 and c not in "\n\r\t") or ord(c) == 127 for c in value):
        raise ValueError("no puede contener caracteres de control")
    return value


def _valid_phone(value: str) -> str:
    # An explicit allow-list, so invisible characters (zero-width space, RTL
    # marks) cannot be used to slip a look-alike duplicate past the uniqueness
    # check — `str.strip()` does not remove them.
    invalid = {c for c in value if c not in _PHONE_CHARS}
    if invalid:
        raise ValueError("solo puede contener dígitos y los símbolos + - ( ) .")
    if len(normalize_phone(value)) < MIN_PHONE_DIGITS:
        raise ValueError(f"debe tener al menos {MIN_PHONE_DIGITS} dígitos")
    return value


NameStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    AfterValidator(_no_control_chars),
]
PhoneStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=MIN_PHONE_DIGITS, max_length=50),
    AfterValidator(_valid_phone),
]
EmailStrField = Annotated[EmailStr, Field(max_length=255)]
# Free-text email for the public booking form, which must not hard-fail on a
# typo. Length-capped to the DB column so an over-long value is a 422, not a 500.
EmailTextStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=255),
    AfterValidator(_no_control_chars),
]
NotesStr = Annotated[
    str, StringConstraints(max_length=2000), AfterValidator(_plain_text)
]


class ClientBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(BaseModel):
    name: NameStr
    phone: PhoneStr
    email: Optional[EmailStrField] = None
    notes: Optional[NotesStr] = None
    # Opt-in confirmation for the "a hidden client already owns this phone"
    # case. Without it the endpoint refuses, so an admin can never merge into
    # someone else's record — and their appointment history and push
    # subscriptions — by accident. See create_client in routers/clients.py.
    restore_hidden: bool = False


class ClientUpdate(BaseModel):
    name: Optional[NameStr] = None
    phone: Optional[PhoneStr] = None
    email: Optional[EmailStrField] = None
    notes: Optional[NotesStr] = None


class ClientResponse(ClientBase):
    id: str
    created_at: dt.datetime

    model_config = {"from_attributes": True}
