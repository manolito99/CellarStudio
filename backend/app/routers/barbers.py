from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db
from app.models.barber import Barber
from app.models.service import Service
from app.models.user import User
from app.schemas.barber import BarberCreate, BarberResponse, BarberUpdate

router = APIRouter(prefix="/api/admin/barbers", tags=["Admin - Barbers"])


@router.get("/", response_model=list[BarberResponse])
def list_barbers(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    return (
        db.query(Barber)
        .options(joinedload(Barber.services))
        .order_by(Barber.sort_order)
        .all()
    )


@router.post("/", response_model=BarberResponse, status_code=status.HTTP_201_CREATED)
def create_barber(
    data: BarberCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    barber = Barber(
        name=data.name,
        photo_url=data.photo_url,
        bio=data.bio,
        is_active=data.is_active,
        sort_order=data.sort_order,
    )

    if data.service_ids:
        services = db.query(Service).filter(Service.id.in_(data.service_ids)).all()
        barber.services = services

    db.add(barber)
    db.commit()
    db.refresh(barber)
    return barber


@router.get("/{barber_id}", response_model=BarberResponse)
def get_barber(
    barber_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    barber = (
        db.query(Barber)
        .options(joinedload(Barber.services))
        .filter(Barber.id == barber_id)
        .first()
    )
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")
    return barber


@router.put("/{barber_id}", response_model=BarberResponse)
def update_barber(
    barber_id: str,
    data: BarberUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    barber = (
        db.query(Barber)
        .options(joinedload(Barber.services))
        .filter(Barber.id == barber_id)
        .first()
    )
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    if "service_ids" in update_data:
        service_ids = update_data.pop("service_ids")
        services = db.query(Service).filter(Service.id.in_(service_ids)).all()
        barber.services = services

    for key, value in update_data.items():
        setattr(barber, key, value)

    db.commit()
    db.refresh(barber)
    return barber


@router.delete("/{barber_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_barber(
    barber_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    barber = db.query(Barber).filter(Barber.id == barber_id).first()
    if not barber:
        raise HTTPException(status_code=404, detail="Barbero no encontrado")
    db.delete(barber)
    db.commit()
