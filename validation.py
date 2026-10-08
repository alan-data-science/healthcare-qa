"""Shared validation rules for UI and REST API."""

from __future__ import annotations

import re
from datetime import date, datetime

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\d{10}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .']{1,79}$")
TIME_SLOTS = ("09:00", "10:00", "11:00", "14:00", "16:00")
DEPARTMENTS = ("General Medicine", "Cardiology", "Pediatrics")


def validate_appointment(data: dict, doctor: dict | None) -> list[str]:
    errors: list[str] = []
    name = (data.get("patient_name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    department = (data.get("department") or "").strip()
    appt_date = (data.get("date") or "").strip()
    appt_time = (data.get("time") or "").strip()
    reason = (data.get("reason") or "").strip()

    if not NAME_RE.match(name):
        errors.append("Patient name must be 2–80 letters (spaces allowed).")
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid email address (example: name@clinic.com).")
    if not PHONE_RE.match(phone):
        errors.append("Phone must be exactly 10 digits.")

    try:
        age = int(data.get("age"))
        if age < 1 or age > 120:
            errors.append("Age must be between 1 and 120.")
    except (TypeError, ValueError):
        errors.append("Age must be a number between 1 and 120.")

    if department not in DEPARTMENTS:
        errors.append("Select a valid department.")
    if not doctor:
        errors.append("Select a doctor.")
    elif doctor["department"] != department:
        errors.append("Selected doctor does not belong to the chosen department.")

    try:
        parsed = datetime.strptime(appt_date, "%Y-%m-%d").date()
        if parsed < date.today():
            errors.append("Appointment date cannot be in the past.")
    except ValueError:
        errors.append("Select a valid appointment date.")

    if appt_time not in TIME_SLOTS:
        errors.append("Select a valid time slot.")
    if not reason:
        errors.append("Reason for visit is required.")
    return errors


def validate_register(data: dict) -> list[str]:
    errors: list[str] = []
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not re.match(r"^[A-Za-z0-9_]{4,20}$", username):
        errors.append("Username must be 4–20 letters, numbers, or underscore.")
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        errors.append("Password must be at least 8 characters and include letters and numbers.")
    if not NAME_RE.match(full_name):
        errors.append("Full name must be 2–80 letters (spaces allowed).")
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if not PHONE_RE.match(phone):
        errors.append("Phone must be exactly 10 digits.")
    return errors
