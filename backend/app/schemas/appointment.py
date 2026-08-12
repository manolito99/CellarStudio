import datetime as dt
from typing import Optional

from pydantic import BaseModel

from app.schemas.barber import BarberBase
from app.schemas.client import ClientBase, EmailTextStr, NameStr, PhoneStr
from app.schemas.service import ServiceBase


class AppointmentCreate(BaseModel):
    # Same constraints as ClientCreate: this endpoint is public and unauthenticated,
    # and it writes straight into the clients table via find-or-create, so it is the
    # weakest door into the client records the admin panel manages.
    client_name: NameStr
    client_phone: PhoneStr
    # Not EmailStr: the booking form should not hard-fail on a typo'd address.
    # Capped because clients.email is VARCHAR(255) — a longer value is a 500.
    client_email: Optional[EmailTextStr] = None
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


class MyAppointmentsLookup(BaseModel):
    phone: str
    email: str


class PublicAppointmentModify(BaseModel):
    phone: str
    email: str
    barber_id: str
    service_id: str
    date: dt.date
    start_time: dt.time


class PublicCancelRequest(BaseModel):
    phone: str
    email: str
