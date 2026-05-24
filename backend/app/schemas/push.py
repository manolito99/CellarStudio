from datetime import datetime

from pydantic import BaseModel


class PushSubscribeRequest(BaseModel):
    endpoint: str
    p256dh_key: str
    auth_key: str
    client_phone: str


class PushTestRequest(BaseModel):
    client_phone: str


class NotificationResponse(BaseModel):
    id: str
    title: str
    body: str
    icon: str
    read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PhoneLookup(BaseModel):
    phone: str
