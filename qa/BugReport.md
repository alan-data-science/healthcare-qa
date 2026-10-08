# Bug Report — MediSlot Clinic

Originally logged after executing `qa/TestCases.csv` against v1.0. All reported defects were retested against MediSlot v2.0 on 8 Oct 2026; linked verification cases passed. The original defect descriptions below document the v1.0 behavior.

| Bug ID | Title | Linked TC | Severity | Status | Module |
|--------|--------|-----------|----------|--------|--------|
| BUG-01 | Forgot password returns 404 | TC-07 | High | Fixed; retest passed | Login |
| BUG-02 | Trailing space in username blocks valid login | TC-06 | Medium | Fixed; retest passed | Login |
| BUG-03 | Incomplete email `test@` is accepted | TC-13 | High | Fixed; retest passed | Book |
| BUG-04 | Phone number accepts alphabetic characters | TC-14 | High | Fixed; retest passed | Book |
| BUG-05 | Past appointment dates are accepted | TC-15 | High | Fixed; retest passed | Book |
| BUG-06 | Age 0 and 200 are accepted | TC-16, TC-17 | Medium | Fixed; retest passed | Book |
| BUG-07 | Whitespace-only patient name is accepted | TC-18 | Medium | Fixed; retest passed | Book |
| BUG-08 | Department and doctor are not cross-checked | TC-20 | Medium | Fixed; retest passed | Book |
| BUG-09 | Duplicate doctor + date + time bookings allowed | TC-21 | High | Fixed; retest passed | Book |
| BUG-10 | Empty time slot still creates a booking | TC-32 | Medium | Fixed; retest passed | Book |
| BUG-11 | POST /api/appointments with empty body returns 201 | TC-29 | Critical | Fixed; retest passed | API |
| BUG-12 | Unknown appointment id returns 200 empty object | TC-30 | High | Fixed; retest passed | API |

---

## BUG-01 — Forgot password returns 404

**Steps:** Login page → click **Forgot password?**
**Expected:** Password reset form or support message.
**Actual:** HTTP 404, “This page is not available.”
**Impact:** Patients cannot recover access.

## BUG-03 — Incomplete email accepted

**Steps:** Book with email `test@` and a selected doctor.
**Expected:** Validation error.
**Actual:** Confirmation ID generated.
**Impact:** Bad contact data in a healthcare record.

## BUG-04 — Phone accepts letters

**Steps:** Phone = `ABCDE12345`, otherwise valid booking.
**Expected:** 10-digit numeric rule.
**Actual:** Saved as typed.
**Impact:** Clinic cannot call the patient.

## BUG-05 — Past dates allowed

**Steps:** Date = `2020-01-01`.
**Expected:** Reject past dates.
**Actual:** Booking saved.
**Impact:** Invalid clinic schedule.

## BUG-09 — Double booking

**Steps:** Book Dr. Meera Shah, 2026-10-21 09:00 twice.
**Expected:** Second request blocked.
**Actual:** Two confirmation IDs.
**Impact:** Overlapping visits.

## BUG-11 — API creates empty appointments

**Steps:** `POST /api/appointments` with `{}`.
**Expected:** 400 Bad Request.
**Actual:** 201 Created, null fields.
**Impact:** Corrupt appointment store (highest severity).
