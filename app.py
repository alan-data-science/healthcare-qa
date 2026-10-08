"""MediSlot Clinic — Healthcare Appointment Management System."""

from __future__ import annotations

import os
import secrets
from datetime import date

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import close_db, get_db, init_db
from validation import TIME_SLOTS, validate_appointment, validate_register


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("MEDISLOT_SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.path.join(os.path.dirname(__file__), "instance", "clinic.db"),
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    def current_user():
        user_id = session.get("user_id")
        if not user_id:
            return None
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    def doctor_by_id(doctor_id):
        if not doctor_id:
            return None
        row = get_db().execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
        return dict(row) if row else None

    def api_user():
        header = request.headers.get("Authorization", "")
        token = header.replace("Bearer ", "").strip()
        if not token:
            return None
        row = get_db().execute(
            """SELECT users.* FROM api_tokens
               JOIN users ON users.id = api_tokens.user_id
               WHERE api_tokens.token = ?""",
            (token,),
        ).fetchone()
        return dict(row) if row else None

    def slot_taken(doctor_id, appt_date, appt_time, exclude_id=None):
        sql = """SELECT id FROM appointments
                 WHERE doctor_id = ? AND appt_date = ? AND appt_time = ?
                   AND status = 'Booked'"""
        params = [doctor_id, appt_date, appt_time]
        if exclude_id:
            sql += " AND id != ?"
            params.append(exclude_id)
        return get_db().execute(sql, params).fetchone() is not None

    def appointment_dict(row):
        item = dict(row)
        doctor = doctor_by_id(item["doctor_id"])
        item["doctor_name"] = doctor["name"] if doctor else ""
        item["confirmation_id"] = f"APT-{item['id']:04d}"
        return item

    @app.context_processor
    def inject_user():
        return {"user": current_user()}

    @app.route("/")
    def home():
        doctors = get_db().execute("SELECT * FROM doctors ORDER BY id").fetchall()
        return render_template("index.html", doctors=doctors, today=date.today().isoformat())

    @app.route("/register", methods=["GET", "POST"])
    def register():
        error = None
        if request.method == "POST":
            payload = {
                "username": request.form.get("username", ""),
                "password": request.form.get("password", ""),
                "full_name": request.form.get("full_name", ""),
                "email": request.form.get("email", ""),
                "phone": request.form.get("phone", ""),
            }
            errors = validate_register(payload)
            db = get_db()
            if db.execute(
                "SELECT id FROM users WHERE username = ?", (payload["username"].strip(),)
            ).fetchone():
                errors.append("Username already exists.")
            if errors:
                error = " ".join(errors)
            else:
                db.execute(
                    """INSERT INTO users (username, password_hash, role, full_name, email, phone)
                       VALUES (?, ?, 'patient', ?, ?, ?)""",
                    (
                        payload["username"].strip(),
                        generate_password_hash(payload["password"]),
                        payload["full_name"].strip(),
                        payload["email"].strip(),
                        payload["phone"].strip(),
                    ),
                )
                db.commit()
                return redirect(url_for("login"))
        return render_template("register.html", error=error)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            row = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if row and check_password_hash(row["password_hash"], password):
                session.clear()
                session["user_id"] = row["id"]
                return redirect(url_for("book"))
            error = "Invalid username or password."
        return render_template("login.html", error=error)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.route("/forgot-password")
    def forgot_password():
        return render_template("forgot.html")

    @app.route("/book", methods=["GET", "POST"])
    def book():
        user = current_user()
        if not user:
            return redirect(url_for("login"))
        db = get_db()
        doctors = [dict(r) for r in db.execute("SELECT * FROM doctors ORDER BY id").fetchall()]
        message = None
        error = None
        if request.method == "POST":
            doctor_id = request.form.get("doctor_id", type=int)
            payload = {
                "patient_name": request.form.get("patient_name", user["full_name"]),
                "age": request.form.get("age", ""),
                "phone": request.form.get("phone", user["phone"]),
                "email": request.form.get("email", user["email"]),
                "department": request.form.get("department", ""),
                "date": request.form.get("date", ""),
                "time": request.form.get("time", ""),
                "reason": request.form.get("reason", ""),
            }
            doctor = doctor_by_id(doctor_id)
            errors = validate_appointment(payload, doctor)
            if doctor and not errors and slot_taken(doctor["id"], payload["date"], payload["time"]):
                errors.append("This doctor is already booked for the selected date and time.")
            if errors:
                error = " ".join(errors)
            else:
                cur = db.execute(
                    """INSERT INTO appointments
                       (user_id, patient_name, age, phone, email, department, doctor_id,
                        appt_date, appt_time, reason, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Booked')""",
                    (
                        user["id"],
                        payload["patient_name"].strip(),
                        int(payload["age"]),
                        payload["phone"].strip(),
                        payload["email"].strip(),
                        payload["department"],
                        doctor["id"],
                        payload["date"],
                        payload["time"],
                        payload["reason"].strip(),
                    ),
                )
                db.commit()
                message = f"Appointment booked. Confirmation ID: APT-{cur.lastrowid:04d}"
        return render_template(
            "book.html",
            doctors=doctors,
            slots=TIME_SLOTS,
            message=message,
            error=error,
            min_date=date.today().isoformat(),
        )

    @app.route("/appointments")
    def list_appointments():
        user = current_user()
        if not user:
            return redirect(url_for("login"))
        db = get_db()
        if user["role"] == "admin":
            rows = db.execute(
                """SELECT a.*, d.name AS doctor_name
                   FROM appointments a JOIN doctors d ON d.id = a.doctor_id
                   ORDER BY appt_date, appt_time"""
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT a.*, d.name AS doctor_name
                   FROM appointments a JOIN doctors d ON d.id = a.doctor_id
                   WHERE a.user_id = ?
                   ORDER BY appt_date, appt_time""",
                (user["id"],),
            ).fetchall()
        items = [appointment_dict(r) for r in rows]
        return render_template("appointments.html", appointments=items)

    @app.route("/appointments/<int:appt_id>/cancel", methods=["POST"])
    def cancel_appointment(appt_id):
        user = current_user()
        if not user:
            return redirect(url_for("login"))
        db = get_db()
        row = db.execute("SELECT * FROM appointments WHERE id = ?", (appt_id,)).fetchone()
        if not row:
            return redirect(url_for("list_appointments"))
        if user["role"] != "admin" and row["user_id"] != user["id"]:
            return redirect(url_for("list_appointments"))
        if row["status"] == "Booked":
            db.execute("UPDATE appointments SET status = 'Cancelled' WHERE id = ?", (appt_id,))
            db.commit()
        return redirect(url_for("list_appointments"))

    @app.route("/api/health")
    def api_health():
        return jsonify({"status": "ok", "service": "MediSlot API", "version": "2.0"})

    @app.route("/api/doctors")
    def api_doctors():
        rows = get_db().execute("SELECT id, name, department FROM doctors ORDER BY id").fetchall()
        return jsonify({"doctors": [dict(r) for r in rows]})

    @app.route("/api/login", methods=["POST"])
    def api_login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        row = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not row or not check_password_hash(row["password_hash"], password):
            return jsonify({"error": "Invalid credentials"}), 401
        token = secrets.token_hex(16)
        db = get_db()
        db.execute("INSERT INTO api_tokens (token, user_id) VALUES (?, ?)", (token, row["id"]))
        db.commit()
        return jsonify({"token": token, "role": row["role"], "name": row["full_name"]})

    def require_api_user():
        user = api_user()
        if not user:
            return None, (jsonify({"error": "Unauthorized"}), 401)
        return user, None

    @app.route("/api/appointments", methods=["GET", "POST"])
    def api_appointments():
        user, err = require_api_user()
        if err:
            return err
        db = get_db()
        if request.method == "GET":
            if user["role"] == "admin":
                rows = db.execute("SELECT * FROM appointments ORDER BY id").fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM appointments WHERE user_id = ? ORDER BY id", (user["id"],)
                ).fetchall()
            return jsonify({"appointments": [appointment_dict(r) for r in rows]})

        data = request.get_json(silent=True) or {}
        doctor = doctor_by_id(data.get("doctor_id"))
        errors = validate_appointment(data, doctor)
        if doctor and not errors and slot_taken(doctor["id"], str(data.get("date") or ""), str(data.get("time") or "")):
            errors.append("This doctor is already booked for the selected date and time.")
        if errors:
            return jsonify({"errors": errors}), 400
        cur = db.execute(
            """INSERT INTO appointments
               (user_id, patient_name, age, phone, email, department, doctor_id,
                appt_date, appt_time, reason, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Booked')""",
            (
                user["id"],
                data["patient_name"].strip(),
                int(data["age"]),
                data["phone"].strip(),
                data["email"].strip(),
                data["department"],
                doctor["id"],
                data["date"],
                data["time"],
                data["reason"].strip(),
            ),
        )
        db.commit()
        row = db.execute("SELECT * FROM appointments WHERE id = ?", (cur.lastrowid,)).fetchone()
        return jsonify({"appointment": appointment_dict(row)}), 201

    @app.route("/api/appointments/<int:appt_id>")
    def api_appointment_detail(appt_id):
        user, err = require_api_user()
        if err:
            return err
        row = get_db().execute("SELECT * FROM appointments WHERE id = ?", (appt_id,)).fetchone()
        if not row:
            return jsonify({"error": "Appointment not found"}), 404
        if user["role"] != "admin" and row["user_id"] != user["id"]:
            return jsonify({"error": "Forbidden"}), 403
        return jsonify({"appointment": appointment_dict(row)})

    return app


app = create_app()

if __name__ == "__main__":
    print("MediSlot Clinic  http://127.0.0.1:5000")
    print("Admin: admin / Admin@123")
    print("Patient: patient / Patient@123")
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
