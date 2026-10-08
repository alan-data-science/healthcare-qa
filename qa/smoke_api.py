import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def request(path, payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def check(label, result, expected_status):
    status, body = result
    if status != expected_status:
        raise AssertionError(f"{label}: expected HTTP {expected_status}, got {status}: {body}")
    print(label, status, body)
    return body


health = check("health", request("/api/health"), 200)
assert health["status"] == "ok"
doctors = check("doctors", request("/api/doctors"), 200)
assert len(doctors["doctors"]) == 3
login = check(
    "login",
    request("/api/login", {"username": "patient", "password": "Patient@123"}),
    200,
)
token = login["token"]
check("appointments", request("/api/appointments", token=token), 200)
check("empty appointment", request("/api/appointments", {}, token), 400)
check("unknown appointment", request("/api/appointments/99999", token=token), 404)
