from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from app.services.phone import normalize_phone, phone_contains, phone_matches

router = APIRouter(prefix="/api/admin/clients", tags=["Admin - Clients"])


def _find_by_phone(db: Session, phone: str, exclude_id: str | None = None):
    """Return (active, soft_deleted) clients holding this phone number.

    Phone is the de-facto identity of a client across the app: the public
    booking flow does find-or-create by phone, and push subscriptions and
    notifications are keyed by phone. Two rows with the same phone would split
    a client's history and deliver notifications to the wrong record, so both
    create and update have to check for collisions — comparing normalized
    numbers, since "600 111 222" and "+34600111222" are the same client.
    """
    query = db.query(Client).filter(phone_matches(Client.phone, phone))
    if exclude_id:
        query = query.filter(Client.id != exclude_id)
    active = query.filter(Client.deleted_at.is_(None)).first()
    soft_deleted = query.filter(Client.deleted_at.is_not(None)).first()
    return active, soft_deleted


@router.get("/", response_model=list[ClientResponse])
def list_clients(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    search: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    query = db.query(Client).filter(Client.deleted_at.is_(None))

    if search:
        # Searching by phone has to ignore formatting. Numbers are stored as
        # typed, so an ILIKE on the raw column misses "634 660 976" when the
        # admin types the 634660976 they read off their own phone — which is
        # how the client picker in "Nueva cita" ends up finding nobody.
        phone_filter = (
            phone_contains(Client.phone, search)
            if normalize_phone(search)
            else Client.phone.ilike(f"%{search}%")
        )
        query = query.filter(
            Client.name.ilike(f"%{search}%")
            | phone_filter
            | Client.email.ilike(f"%{search}%")
        )

    return (
        query.order_by(Client.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    """Create a client by hand from the admin panel."""
    active, soft_deleted = _find_by_phone(db, data.phone)
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un cliente con ese teléfono ({active.name})",
        )

    if soft_deleted:
        # A hidden client owns this number. Inserting a second row is not an
        # option (the booking flow looks clients up by phone without filtering
        # deleted_at, so the duplicate would take over their appointments), but
        # neither is reusing the row silently: it keeps the old id, so the
        # "new" client would inherit the hidden one's appointment history,
        # their push subscriptions and their notifications, and the write would
        # destroy the old name/notes. Require an explicit confirmation instead.
        if not data.restore_hidden:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "hidden_client",
                    "message": (
                        f"Un cliente oculto ({soft_deleted.name}) ya tiene ese "
                        "teléfono. Si continúas se restaurará su ficha y se "
                        "conservará su historial de citas."
                    ),
                    "hidden_client_name": soft_deleted.name,
                },
            )
        soft_deleted.name = data.name
        soft_deleted.email = data.email
        soft_deleted.notes = data.notes
        soft_deleted.deleted_at = None
        db.commit()
        db.refresh(soft_deleted)
        return soft_deleted

    client = Client(
        name=data.name,
        phone=data.phone,
        email=data.email,
        notes=data.notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.deleted_at.is_(None))
        .first()
    )
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
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.deleted_at.is_(None))
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    new_phone = update_data.get("phone")
    if new_phone and new_phone != client.phone:
        active, soft_deleted = _find_by_phone(db, new_phone, exclude_id=client_id)
        if active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un cliente con ese teléfono ({active.name})",
            )
        if soft_deleted:
            # Reject rather than revive: unlike create, this would leave two
            # rows on the same phone and merging their histories is not a
            # decision this endpoint should make silently. Creating a client
            # with that number is the supported way to bring the record back.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Ese teléfono pertenece a un cliente oculto "
                    f"({soft_deleted.name}). Restáuralo desde «Nuevo cliente»."
                ),
            )

    for key, value in update_data.items():
        setattr(client, key, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.deleted_at.is_(None))
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    # Soft delete: clients are referenced by appointments (FK). Mark as deleted so
    # the client is hidden from admin lists and dashboard counts, while keeping the
    # appointment history intact. If the same phone books again it is revived.
    client.deleted_at = datetime.now(timezone.utc)
    db.commit()


@router.get("/{client_id}/appointments")
def get_client_appointments(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.deleted_at.is_(None))
        .first()
    )
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
