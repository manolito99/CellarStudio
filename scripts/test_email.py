"""
Test script: books a real appointment and verifies the confirmation email is triggered.

Usage:
    python scripts/test_email.py

The script will:
  1. Wait until the API is healthy
  2. Fetch the first active barber and a service with duration > 0
  3. Find the next available date + slot for that barber/service
  4. Create an appointment for nolomanolo990@gmail.com
  5. Print the result — check your inbox afterwards!
"""

import sys
import time
import datetime
import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000"
TARGET_EMAIL = "nolomanolo990@gmail.com"
MAX_WAIT_SECS = 60


# ── helpers ──────────────────────────────────────────────────────────────────

def get(path: str) -> dict | list:
    url = BASE_URL + path
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def post(path: str, body: dict) -> dict:
    url = BASE_URL + path
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def wait_for_api():
    print("⏳ Waiting for API to be ready...")
    deadline = time.time() + MAX_WAIT_SECS
    while time.time() < deadline:
        try:
            get("/api/health")
            print("✅ API is ready\n")
            return
        except Exception:
            time.sleep(2)
    print("❌ API did not become ready in time. Is docker-compose running?")
    sys.exit(1)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    wait_for_api()

    # 1. Get barbers
    barbers = get("/api/public/barbers")
    if not barbers:
        print("❌ No active barbers found in DB")
        sys.exit(1)
    barber = barbers[0]
    print(f"💈 Barber: {barber['name']} (id={barber['id']})")

    # 2. Get services — pick one with duration > 0 so end_time is meaningful
    services = get("/api/public/services")
    service = next((s for s in services if s.get("duration_minutes", 0) > 0), None)
    if not service:
        print("❌ No services with duration > 0 found")
        sys.exit(1)
    print(f"✂️  Service: {service['name']} ({service['duration_minutes']} min, id={service['id']})")

    # 3. Find next available date with at least one free slot (search up to 14 days)
    today = datetime.date.today()
    chosen_date = None
    chosen_slot = None

    for delta in range(1, 15):
        check_date = today + datetime.timedelta(days=delta)
        date_str = check_date.isoformat()
        try:
            avail = get(
                f"/api/public/availability"
                f"?barber_id={barber['id']}"
                f"&date={date_str}"
                f"&service_id={service['id']}"
            )
            free_slots = [s for s in avail.get("slots", []) if s["available"]]
            if free_slots:
                chosen_date = check_date
                chosen_slot = free_slots[0]["start_time"]  # e.g. "09:00:00"
                break
        except Exception as e:
            print(f"  ⚠️  Availability check failed for {date_str}: {e}")

    if not chosen_date:
        print("❌ No available slots found in the next 14 days")
        sys.exit(1)

    slot_display = chosen_slot[:5]  # "HH:MM"
    print(f"📅 First available slot: {chosen_date} @ {slot_display}\n")

    # 4. Book the appointment
    payload = {
        "client_name": "Test Email Prueba",
        "client_phone": "+34 666 000 000",
        "client_email": TARGET_EMAIL,
        "barber_id": barber["id"],
        "service_id": service["id"],
        "date": chosen_date.isoformat(),
        "start_time": chosen_slot,
        "notes": "Cita de prueba — script test_email.py",
    }

    print(f"📨 Booking appointment for {TARGET_EMAIL}...")
    print(f"   Payload: {json.dumps(payload, indent=2)}\n")

    try:
        result = post("/api/public/appointments", payload)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ HTTP {e.code}: {body}")
        sys.exit(1)

    print("✅ Appointment created successfully!")
    print(f"   ID:      {result['id']}")
    print(f"   Client:  {result['client']['name']} <{result['client'].get('email', '—')}>")
    print(f"   Barber:  {result['barber']['name']}")
    print(f"   Service: {result['service']['name']}")
    print(f"   Date:    {result['date']}  {result['start_time'][:5]} → {result['end_time'][:5]}")
    print(f"   Status:  {result['status']}")
    print(f"\n📬 Check inbox: {TARGET_EMAIL}")
    print("   Subject: 'Confirmación de tu cita - Cellar Barber Studio'")


if __name__ == "__main__":
    main()
