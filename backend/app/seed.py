"""Seed script to populate database with initial data."""

import uuid
from datetime import date, time, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import (
    Appointment,
    Barber,
    BlockedSlot,
    Client,
    Schedule,
    Service,
    User,
)
from app.utils.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded. Skipping.")
            return

        # --- Admin User ---
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@cellarstudio.com",
            password_hash=hash_password("admin123"),
            name="Administrador",
            role="admin",
        )
        db.add(admin)

        # --- Services ---
        services_data = [
            {
                "name": "Corte Clásico",
                "description": "Corte de cabello con tijera y máquina. Incluye lavado y peinado.",
                "price": 0,
                "duration_minutes": 60,
                "sort_order": 1,
            },
            {
                "name": "Corte + Barba",
                "description": "Corte de cabello completo y perfilado de barba.",
                "price": 0,
                "duration_minutes": 60,
                "sort_order": 2,
            },
            {
                "name": "Mechas",
                "description": "Mechas personalizadas. Duración a consultar según el trabajo.",
                "price": 0,
                "duration_minutes": 120,
                "sort_order": 3,
            },
        ]

        services = []
        for sdata in services_data:
            s = Service(id=str(uuid.uuid4()), **sdata)
            db.add(s)
            services.append(s)

        # --- Barbers ---
        barbers_data = [
            {
                "name": "Maxi Zabaleta",
                "bio": "Fundador de Cellar Studio. Especialista en cortes y estilos modernos.",
                "sort_order": 1,
            },
        ]

        barbers = []
        for bdata in barbers_data:
            b = Barber(id=str(uuid.uuid4()), **bdata)
            b.services = services  # All barbers offer all services
            db.add(b)
            barbers.append(b)

        # --- Schedules (Mon-Sat, 9:00-20:00) ---
        for barber in barbers:
            for day in range(6):  # 0=Monday to 5=Saturday
                schedule = Schedule(
                    id=str(uuid.uuid4()),
                    barber_id=barber.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(20, 0),
                )
                db.add(schedule)

        # --- Clients ---
        clients_data = [
            {"name": "Juan Pérez", "phone": "+34 611 111 111", "email": "juan@email.com"},
            {"name": "Miguel Torres", "phone": "+34 622 222 222", "email": "miguel@email.com"},
            {"name": "Roberto Sánchez", "phone": "+34 633 333 333"},
        ]

        clients = []
        for cdata in clients_data:
            c = Client(id=str(uuid.uuid4()), **cdata)
            db.add(c)
            clients.append(c)

        # --- Example Appointments (today and upcoming) ---
        today = date.today()
        appointments_data = [
            {
                "client": clients[0],
                "barber": barbers[0],
                "service": services[0],
                "date": today,
                "start_time": time(10, 0),
                "end_time": time(11, 0),
                "status": "confirmed",
            },
            {
                "client": clients[1],
                "barber": barbers[0],
                "service": services[1],
                "date": today,
                "start_time": time(11, 0),
                "end_time": time(12, 0),
                "status": "pending",
            },
            {
                "client": clients[2],
                "barber": barbers[0],
                "service": services[0],
                "date": today + timedelta(days=1),
                "start_time": time(14, 0),
                "end_time": time(15, 0),
                "status": "confirmed",
            },
        ]

        for adata in appointments_data:
            a = Appointment(
                id=str(uuid.uuid4()),
                client_id=adata["client"].id,
                barber_id=adata["barber"].id,
                service_id=adata["service"].id,
                date=adata["date"],
                start_time=adata["start_time"],
                end_time=adata["end_time"],
                status=adata["status"],
            )
            db.add(a)

        db.commit()
        print("Database seeded successfully!")
        print(f"  - Admin: admin@cellarstudio.com / admin123")
        print(f"  - {len(services)} services created")
        print(f"  - {len(barbers)} barbers created")
        print(f"  - {len(clients)} clients created")
        print(f"  - {len(appointments_data)} appointments created")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
