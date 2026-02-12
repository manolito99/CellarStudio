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
                "description": "Corte de cabello tradicional con tijera y máquina. Incluye lavado y peinado.",
                "price": 2500.00,
                "duration_minutes": 30,
                "sort_order": 1,
            },
            {
                "name": "Degradado / Fade",
                "description": "Degradado moderno con máquina. Low, mid o high fade a elección.",
                "price": 3000.00,
                "duration_minutes": 40,
                "sort_order": 2,
            },
            {
                "name": "Barba",
                "description": "Perfilado y afeitado de barba con navaja. Incluye toalla caliente.",
                "price": 1500.00,
                "duration_minutes": 20,
                "sort_order": 3,
            },
            {
                "name": "Corte + Barba",
                "description": "Combo completo: corte de cabello y perfilado de barba.",
                "price": 4000.00,
                "duration_minutes": 50,
                "sort_order": 4,
            },
            {
                "name": "Tratamiento Capilar",
                "description": "Tratamiento de hidratación profunda con masaje capilar.",
                "price": 3500.00,
                "duration_minutes": 45,
                "sort_order": 5,
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
                "name": "Maxi López",
                "bio": "Fundador de Cellar Studio. Especialista en degradados y diseños.",
                "sort_order": 1,
            },
            {
                "name": "Carlos Ruiz",
                "bio": "Experto en barbería clásica y afeitado con navaja.",
                "sort_order": 2,
            },
            {
                "name": "Diego Martínez",
                "bio": "Especialista en tratamientos capilares y estilos modernos.",
                "sort_order": 3,
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
            {"name": "Juan Pérez", "phone": "+54 11 1234-5678", "email": "juan@email.com"},
            {"name": "Miguel Torres", "phone": "+54 11 2345-6789", "email": "miguel@email.com"},
            {"name": "Roberto Sánchez", "phone": "+54 11 3456-7890"},
            {"name": "Andrés Gómez", "phone": "+54 11 4567-8901", "email": "andres@email.com"},
            {"name": "Facundo Ríos", "phone": "+54 11 5678-9012"},
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
                "end_time": time(10, 30),
                "status": "confirmed",
            },
            {
                "client": clients[1],
                "barber": barbers[1],
                "service": services[3],
                "date": today,
                "start_time": time(11, 0),
                "end_time": time(11, 50),
                "status": "pending",
            },
            {
                "client": clients[2],
                "barber": barbers[0],
                "service": services[1],
                "date": today,
                "start_time": time(14, 0),
                "end_time": time(14, 40),
                "status": "confirmed",
            },
            {
                "client": clients[3],
                "barber": barbers[2],
                "service": services[4],
                "date": today + timedelta(days=1),
                "start_time": time(9, 0),
                "end_time": time(9, 45),
                "status": "pending",
            },
            {
                "client": clients[4],
                "barber": barbers[1],
                "service": services[2],
                "date": today + timedelta(days=2),
                "start_time": time(16, 0),
                "end_time": time(16, 20),
                "status": "pending",
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
