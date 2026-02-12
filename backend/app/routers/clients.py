from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientResponse, ClientUpdate

router = APIRouter(prefix="/api/admin/clients", tags=["Admin - Clients"])


@router.get("/", response_model=list[ClientResponse])
def list_clients(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    search: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    query = db.query(Client)

    if search:
        query = query.filter(
            Client.name.ilike(f"%{search}%")
            | Client.phone.ilike(f"%{search}%")
            | Client.email.ilike(f"%{search}%")
        )

    return (
        query.order_by(Client.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: str,
    data: ClientUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(client, key, value)

    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}/appointments")
def get_client_appointments(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    appointments = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.barber),
            joinedload(Appointment.service),
            joinedload(Appointment.client),
        )
        .filter(Appointment.client_id == client_id)
        .order_by(Appointment.date.desc(), Appointment.start_time.desc())
        .all()
    )
    return appointments
