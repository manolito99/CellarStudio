import datetime as dt
from typing import Optional

from pydantic import BaseModel

from app.schemas.service import ServiceResponse


class BarberBase(BaseModel):
    name: str
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class BarberCreate(BarberBase):
    service_ids: list[str] = []


class BarberUpdate(BaseModel):
    name: Optional[str] = None
    photo_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    service_ids: Optional[list[str]] = None


class BarberResponse(BarberBase):
    id: str
    user_id: Optional[str] = None
    created_at: dt.datetime
    services: list[ServiceResponse] = []

    model_config = {"from_attributes": True}
