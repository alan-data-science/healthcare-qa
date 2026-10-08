# Software Test Plan

**Project title:** Development and Quality Assurance of a Healthcare Appointment Management System
**Application:** MediSlot Clinic v2.0
**Document type:** STLC — Test Plan (adapted from IEEE 829)
**Student:** Alan

## 1. Purpose

This plan describes how the healthcare appointment system is verified: functional testing of web modules, negative testing of validation rules, and REST API testing.

## 2. Test items

- Patient registration and authentication
- Appointment booking, listing, and cancellation
- REST APIs (`/api/health`, `/api/login`, `/api/doctors`, `/api/appointments`)
- SQLite persistence across requests

## 3. Features to be tested

| ID | Feature |
|----|---------|
| REQ-01 | Home, login, logout, forgot-password information page |
| REQ-02 | Patient self-registration |
| REQ-03 | Book appointment with validated patient and slot data |
| REQ-04 | View appointments (patient: own records; admin: all records) |
| REQ-05 | Cancel a booked appointment |
| REQ-06 | REST API with authentication and error codes |

## 4. Approach

Black-box functional testing of web routes, API tests in Postman, and automated regression with pytest. Protected appointment API requests require the bearer token returned by `/api/login`. API detail tests create an appointment during the run and use its returned ID; they do not rely on pre-seeded appointment data. Boundary values include age 1 and 120, 10-digit phone, date = today, and a past date.

## 5. Environment

Windows 10, Python 3, Flask, Chrome, Postman, pytest.

## 6. Entry and exit criteria

**Entry:** application starts; seeded `admin` and `patient` accounts exist.
**Exit:** all planned test cases executed; critical defects closed or verified fixed; pytest suite green; test summary signed off.

## 7. Deliverables

Test plan, test cases, defect log, RTM, test summary, pytest results, Postman collection.

## 8. Current-build retest

The existing 35 test cases were re-executed against MediSlot v2.0 on 8 Oct 2026 using Flask's test client and an isolated temporary SQLite database. This exercises the application through HTTP requests without altering the local demo database. Results and the preserved v1.0 execution are recorded side by side in `TestCases.csv` and summarized in `TestSummary.md`.
