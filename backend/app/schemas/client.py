import datetime as dt
from typing import Optional

from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: str
    created_at: dt.datetime

    model_config = {"from_attributes": True}
