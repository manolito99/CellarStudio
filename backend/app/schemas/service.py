import datetime as dt
from typing import Optional

from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration_minutes: int = 30
    image_url: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class ServiceResponse(ServiceBase):
    id: str
    created_at: dt.datetime

    model_config = {"from_attributes": True}
