import datetime as dt
from typing import Optional

from pydantic import BaseModel

from app.schemas.barber import BarberBase
from app.schemas.client import ClientBase
from app.schemas.service import ServiceBase


class AppointmentCreate(BaseModel):
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    barber_id: str
    service_id: str
    date: dt.date
    start_time: dt.time
    notes: Optional[str] = None


class AppointmentAdminCreate(BaseModel):
    client_id: str
    barber_id: str
    service_id: str
    date: dt.date
    start_time: dt.time
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    barber_id: Optional[str] = None
    service_id: Optional[str] = None
    date: Optional[dt.date] = None
    start_time: Optional[dt.time] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


class AppointmentClientInfo(ClientBase):
    id: str
    model_config = {"from_attributes": True}


class AppointmentBarberInfo(BarberBase):
    id: str
    model_config = {"from_attributes": True}


class AppointmentServiceInfo(ServiceBase):
    id: str
    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    id: str
    client_id: str
    barber_id: str
    service_id: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    status: str
    notes: Optional[str] = None
    created_at: dt.datetime
    updated_at: dt.datetime
    client: AppointmentClientInfo
    barber: AppointmentBarberInfo
    service: AppointmentServiceInfo

    model_config = {"from_attributes": True}


class AppointmentListResponse(BaseModel):
    id: str
    client_id: str
    barber_id: str
    service_id: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    status: str
    notes: Optional[str] = None
    created_at: dt.datetime
    client: AppointmentClientInfo
    barber: AppointmentBarberInfo
    service: AppointmentServiceInfo

    model_config = {"from_attributes": True}
