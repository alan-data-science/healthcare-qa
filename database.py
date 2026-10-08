import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    patient_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    department TEXT NOT NULL,
    doctor_id INTEGER NOT NULL,
    appt_date TEXT NOT NULL,
    appt_time TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Booked',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

CREATE TABLE IF NOT EXISTS api_tokens (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""


def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(current_app.config["DATABASE"]) or ".", exist_ok=True)
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) AS c FROM doctors").fetchone()["c"] == 0:
        db.executemany(
            "INSERT INTO doctors (name, department) VALUES (?, ?)",
            [
                ("Dr. Meera Shah", "General Medicine"),
                ("Dr. Rohan Patel", "Cardiology"),
                ("Dr. Aisha Khan", "Pediatrics"),
            ],
        )
    if db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"] == 0:
        db.executemany(
            """INSERT INTO users (username, password_hash, role, full_name, email, phone)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    "admin",
                    generate_password_hash("Admin@123"),
                    "admin",
                    "Clinic Admin",
                    "admin@medislot.local",
                    "9000000001",
                ),
                (
                    "patient",
                    generate_password_hash("Patient@123"),
                    "patient",
                    "Alan Patient",
                    "alan@medislot.local",
                    "9000000002",
                ),
            ],
        )
    db.commit()
