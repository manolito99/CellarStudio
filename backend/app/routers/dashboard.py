from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.service import Service
from app.models.user import User

router = APIRouter(prefix="/api/admin/dashboard", tags=["Admin - Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Total appointments today
    appointments_today = (
        db.query(func.count(Appointment.id))
        .filter(Appointment.date == today, Appointment.status != "cancelled")
        .scalar()
    )

    # Revenue today
    revenue_today = (
        db.query(func.sum(Service.price))
        .join(Appointment, Appointment.service_id == Service.id)
        .filter(
            Appointment.date == today,
            Appointment.status.in_(["completed", "confirmed"]),
        )
        .scalar()
    ) or 0

    # Revenue this week
    revenue_week = (
        db.query(func.sum(Service.price))
        .join(Appointment, Appointment.service_id == Service.id)
        .filter(
            Appointment.date >= week_start,
            Appointment.date <= today,
            Appointment.status.in_(["completed", "confirmed"]),
        )
        .scalar()
    ) or 0

    # Revenue this month
    revenue_month = (
        db.query(func.sum(Service.price))
        .join(Appointment, Appointment.service_id == Service.id)
        .filter(
            Appointment.date >= month_start,
            Appointment.date <= today,
            Appointment.status.in_(["completed", "confirmed"]),
        )
        .scalar()
    ) or 0

    # New clients this month
    new_clients_month = (
        db.query(func.count(Client.id))
        .filter(Client.created_at >= datetime.combine(month_start, datetime.min.time()).replace(tzinfo=timezone.utc))
        .scalar()
    )

    # Total clients
    total_clients = db.query(func.count(Client.id)).scalar()

    return {
        "appointments_today": appointments_today,
        "revenue_today": float(revenue_today),
        "revenue_week": float(revenue_week),
        "revenue_month": float(revenue_month),
        "new_clients_month": new_clients_month,
        "total_clients": total_clients,
    }


@router.get("/revenue")
def get_revenue_data(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    period: str = Query("week", regex="^(day|week|month)$"),
):
    today = date.today()

    if period == "day":
        days = 7
    elif period == "week":
        days = 28
    else:
        days = 90

    start_date = today - timedelta(days=days)

    results = (
        db.query(
            Appointment.date,
            func.sum(Service.price).label("revenue"),
            func.count(Appointment.id).label("count"),
        )
        .join(Service, Appointment.service_id == Service.id)
        .filter(
            Appointment.date >= start_date,
            Appointment.date <= today,
            Appointment.status.in_(["completed", "confirmed"]),
        )
        .group_by(Appointment.date)
        .order_by(Appointment.date)
        .all()
    )

    return [
        {
            "date": r.date.isoformat(),
            "revenue": float(r.revenue),
            "count": r.count,
        }
        for r in results
    ]


@router.get("/appointments-today")
def get_appointments_today(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    today = date.today()
    appointments = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.client),
            joinedload(Appointment.barber),
            joinedload(Appointment.service),
        )
        .filter(Appointment.date == today)
        .order_by(Appointment.start_time)
        .all()
    )
    return appointments
