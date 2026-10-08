# Quality Assurance of an Online Healthcare Appointment Portal

Manual + API testing project on a small clinic booking demo (**MediSlot**). Built as a portfolio piece for QA / software testing interviews (including IQVIA).

## Project structure

```text
healthcare-qa-portal/
├── app.py                         # Flask web application and REST API
├── database.py                    # SQLite schema, connection, and demo seed data
├── validation.py                  # Shared appointment and registration validation
├── requirements.txt               # Flask and pytest dependencies
├── pytest.ini                     # pytest configuration
├── templates/                     # Jinja pages for login, booking, and appointments
├── static/                        # Application stylesheet
├── tests/                          # Automated Flask regression tests
├── qa/                             # Test plan, cases, defect log, RTM, summary, smoke check
└── postman/                        # REST API test collection
```

`instance/`, `venv/`, and Python/test cache folders are generated locally and ignored by Git. The original **MediSlot v1.0 baseline** (22/35 passed; 12 defects) and the completed **v2.0 retest** (35/35 passed) are both preserved in `qa/`. The current app fixes the behaviors reported in the original defect log.

## How to run the website

```bash
cd healthcare-qa-portal
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

**Demo logins**

- `patient` / `Patient@123`
- `admin` / `Admin@123`

For local use, Flask generates a temporary session key automatically. When deploying, set a stable, private `MEDISLOT_SECRET_KEY` environment variable; never commit it to GitHub. Debug mode is off by default and can be enabled locally with `FLASK_DEBUG=1`.

## How to run QA checks

Run automated regression tests from the project root:

```bash
python -m pytest -q
```

For a live API smoke check, start the app and in a second terminal run:

```bash
python qa/smoke_api.py
```

For manual API testing, import `postman/MediSlot_API.postman_collection.json` in Postman and run the collection. It obtains a login token before calling protected endpoints.

The original v1.0 black-box execution, defect report, and traceability matrix are in `qa/`, along with the completed v2.0 retest results. All 35 existing cases passed on v2.0; no cases were added.

This is an academic demonstration, not a real clinic system. Use only the included demo accounts and non-sensitive test data.
