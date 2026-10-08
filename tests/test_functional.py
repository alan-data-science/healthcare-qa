from datetime import date, timedelta

FUTURE = (date.today() + timedelta(days=14)).isoformat()


def login(client, username="patient", password="Patient@123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def valid_book(**overrides):
    data = {
        "patient_name": "Alan Patient",
        "age": "32",
        "phone": "9000000002",
        "email": "alan@medislot.local",
        "department": "Cardiology",
        "doctor_id": "2",
        "date": FUTURE,
        "time": "11:00",
        "reason": "Routine checkup",
    }
    data.update(overrides)
    return data


def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Healthcare Appointment Management System" in res.data


def test_login_success_and_logout(client):
    res = login(client)
    assert res.status_code == 200
    assert b"Book appointment" in res.data
    res = client.get("/logout", follow_redirects=True)
    assert b"Login" in res.data


def test_login_rejects_wrong_password(client):
    res = login(client, password="wrong")
    assert b"Invalid username or password" in res.data


def test_book_requires_login(client):
    res = client.get("/book", follow_redirects=True)
    assert b"Sign in" in res.data


def test_happy_path_booking(client):
    login(client)
    res = client.post("/book", data=valid_book(), follow_redirects=True)
    assert b"Appointment booked" in res.data
    assert b"APT-" in res.data


def test_rejects_invalid_email(client):
    login(client)
    res = client.post("/book", data=valid_book(email="test@"), follow_redirects=True)
    assert b"valid email" in res.data


def test_rejects_alpha_phone(client):
    login(client)
    res = client.post("/book", data=valid_book(phone="ABCDE12345"), follow_redirects=True)
    assert b"10 digits" in res.data


def test_rejects_past_date(client):
    login(client)
    res = client.post("/book", data=valid_book(date="2020-01-01"), follow_redirects=True)
    assert b"cannot be in the past" in res.data


def test_rejects_invalid_age(client):
    login(client)
    res = client.post("/book", data=valid_book(age="200"), follow_redirects=True)
    assert b"Age must be between 1 and 120" in res.data


def test_rejects_department_mismatch(client):
    login(client)
    res = client.post("/book", data=valid_book(department="Pediatrics", doctor_id="2"), follow_redirects=True)
    assert b"does not belong" in res.data


def test_rejects_duplicate_slot(client):
    login(client)
    payload = valid_book(time="09:00")
    first = client.post("/book", data=payload, follow_redirects=True)
    assert b"Appointment booked" in first.data
    second = client.post("/book", data=payload, follow_redirects=True)
    assert b"already booked" in second.data


def test_cancel_appointment(client):
    login(client)
    client.post("/book", data=valid_book(time="16:00"), follow_redirects=True)
    res = client.post("/appointments/1/cancel", follow_redirects=True)
    assert b"Cancelled" in res.data


def test_register_new_patient(client):
    res = client.post(
        "/register",
        data={
            "full_name": "Neha Verma",
            "username": "neha_v",
            "password": "Neha12345",
            "email": "neha@example.com",
            "phone": "9876543210",
        },
        follow_redirects=True,
    )
    assert b"Sign in" in res.data
    res = login(client, "neha_v", "Neha12345")
    assert b"Book appointment" in res.data


def test_forgot_password_page(client):
    res = client.get("/forgot-password")
    assert res.status_code == 200
    assert b"Contact the clinic administrator" in res.data


def test_api_health_and_doctors(client):
    assert client.get("/api/health").json["status"] == "ok"
    doctors = client.get("/api/doctors").json["doctors"]
    assert len(doctors) == 3


def test_api_login_and_validation(client):
    bad = client.post("/api/login", json={"username": "patient", "password": "x"})
    assert bad.status_code == 401
    ok = client.post("/api/login", json={"username": "patient", "password": "Patient@123"})
    token = ok.json["token"]
    headers = {"Authorization": f"Bearer {token}"}
    empty = client.post("/api/appointments", json={}, headers=headers)
    assert empty.status_code == 400
    created = client.post(
        "/api/appointments",
        json={
            "patient_name": "Alan Patient",
            "age": 32,
            "phone": "9000000002",
            "email": "alan@medislot.local",
            "department": "General Medicine",
            "doctor_id": 1,
            "date": FUTURE,
            "time": "14:00",
            "reason": "Fever",
        },
        headers=headers,
    )
    assert created.status_code == 201
    appt_id = created.json["appointment"]["id"]
    detail = client.get(f"/api/appointments/{appt_id}", headers=headers)
    assert detail.status_code == 200
    missing = client.get("/api/appointments/99999", headers=headers)
    assert missing.status_code == 404
    unauth = client.get("/api/appointments")
    assert unauth.status_code == 401
