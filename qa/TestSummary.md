# Test Summary Report

**Project:** Quality Assurance of an Online Healthcare Appointment Portal Using Manual and API Testing
**Builds:** MediSlot v1.0 baseline and MediSlot v2.0 retest
**Execution date:** 8 Oct 2026

## Original v1.0 baseline

| Metric | Count |
|--------|-------|
| Test cases planned | 35 |
| Executed | 35 |
| Passed | 22 |
| Failed | 13 |
| Pass % | 62.9% |
| Defects logged | 12 |
| Critical | 1 |
| High | 6 |
| Medium | 5 |

## v2.0 retest

| Metric | Result |
|--------|--------|
| Test cases planned / executed | 35 / 35 |
| Passed / failed | 35 / 0 |
| Pass rate | 100% |
| Historical defects retested and passing | 12 / 12 |
| Current open defects from this log | 0 |
| Automated pytest regression | 16 passed |

The existing 35 cases were exercised on 8 Oct 2026 against MediSlot v2.0 using Flask's test client, with a fresh temporary SQLite database. API appointment operations used a bearer token obtained from `/api/login`; API detail verification used an appointment created during the run. The temporary database was discarded afterward; the local demo database was not changed.

## Conclusion

The v2.0 retest passed all 35 existing scenarios, including login, booking, validation, duplicate-slot handling, API authentication, and error responses. Patient registration is also covered by the automated pytest suite. All 12 v1.0 findings passed their linked verification cases. The historical v1.0 results remain in `TestCases.csv` for traceability; no cases were added.

This is an academic demonstration and is not suitable for real clinical use.
