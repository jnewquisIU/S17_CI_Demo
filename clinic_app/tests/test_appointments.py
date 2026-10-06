"""
test_appointments.py
====================
Automated tests for the clinic app. The first thirteen were written from the
eval table in Evals.md, and the eval number is in the test's name and
docstring. Two more were added later at the bottom of the file.

Run every test from the clinic_app folder:

    python -m pytest

Run one test by name:

    python -m pytest -k e07
"""

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# New in Session 17: how to read a test
#
# assert is the check. It means "this must be true." If it is true, pytest
# goes on to the next line. If it is false, the test stops there and pytest
# reports a failure, showing the line and the two values it compared.
#
#     assert response.status_code == 200   the page loaded
#     assert response.status_code == 302   the app redirected, which is what it
#                                          does after a successful save
#     assert response.status_code == 404   the page was not found
#     assert b"Buddy" in response.data     "Buddy" appears somewhere in the page
#     assert count_rows("Appointment") == before + 1   one row was added
#
# The b in front of a string, as in b"Buddy", means bytes. response.data holds
# the page as bytes, so the text you search for has to be bytes too.
#
# client, count_rows, and fetch_one are not defined in this file. They are
# fixtures from conftest.py. When a test lists one as an argument, pytest
# builds it and passes it in.
# ---------------------------------------------------------------------------

import validators

# One valid appointment. Each test copies it and changes one field, so a
# failing test points at the field it changed.
GOOD = {
    "pet_id": "1",
    "vet_id": "1",
    "appt_time": "2030-03-04 10:00",
    "reason": "Annual checkup",
}


def submit(client, **changes):
    """Post the new-appointment form with GOOD, plus any changed fields."""
    form = dict(GOOD, **changes)
    return client.post("/appointments/new", data=form)


# ---------------------------------------------------------------------------
# Normal use
# ---------------------------------------------------------------------------

def test_e01_list_shows_pet_names(client):
    """E1: the list page loads and shows the pet's name from the Pet table."""
    response = client.get("/appointments")
    assert response.status_code == 200
    assert b"Buddy" in response.data
    assert b"Mango" in response.data


def test_e02_valid_appointment_is_stored(client, count_rows, fetch_one):
    """E2: a valid form adds one row and sends the browser back to the list."""
    before = count_rows("Appointment")
    response = submit(client)
    assert response.status_code == 302
    assert count_rows("Appointment") == before + 1
    newest = fetch_one("SELECT * FROM Appointment ORDER BY appointment_id DESC")
    assert newest["reason"] == "Annual checkup"
    assert newest["appt_time"] == "2030-03-04 10:00"


def test_e03_edit_changes_the_stored_reason(client, fetch_one):
    """E3: editing appointment 2 with a new reason stores the new reason."""
    response = client.post(
        "/appointments/2/edit", data=dict(GOOD, reason="Follow-up visit")
    )
    assert response.status_code == 302
    row = fetch_one("SELECT reason FROM Appointment WHERE appointment_id = 2")
    assert row["reason"] == "Follow-up visit"


def test_e04_delete_removes_one_row(client, count_rows, fetch_one):
    """E4: deleting appointment 3 removes that row and no other."""
    before = count_rows("Appointment")
    client.post("/appointments/3/delete")
    assert count_rows("Appointment") == before - 1
    assert fetch_one("SELECT * FROM Appointment WHERE appointment_id = 3") is None


# ---------------------------------------------------------------------------
# Boundaries
# ---------------------------------------------------------------------------

def test_e05_reason_of_exactly_200_characters_is_accepted(client, count_rows):
    """E5: 200 characters is the limit, so 200 is allowed."""
    before = count_rows("Appointment")
    submit(client, reason="x" * 200)
    assert count_rows("Appointment") == before + 1


def test_e06_reason_of_201_characters_is_refused(client, count_rows):
    """E6: one character over the limit is refused with the length message."""
    before = count_rows("Appointment")
    response = submit(client, reason="x" * 201)
    assert b"Reason must be 200 characters or fewer. You entered 201." in response.data
    assert count_rows("Appointment") == before


# ---------------------------------------------------------------------------
# Bad input
# ---------------------------------------------------------------------------

def test_e07_reason_of_only_spaces_is_refused(client, count_rows):
    """E7: a reason made of spaces counts as empty."""
    before = count_rows("Appointment")
    response = submit(client, reason="     ")
    assert b"Reason is required." in response.data
    assert count_rows("Appointment") == before


def test_e08_impossible_date_is_refused(client, count_rows):
    """E8: February 30 looks like a date and is not one."""
    before = count_rows("Appointment")
    response = submit(client, appt_time="2030-02-30 10:00")
    assert b"Date and time must look like 2026-09-16 14:00." in response.data
    assert count_rows("Appointment") == before


def test_e09_pet_that_does_not_exist_is_refused(client, count_rows):
    """E9: pet 999 is not in the Pet table."""
    before = count_rows("Appointment")
    response = submit(client, pet_id="999")
    assert b"Choose a pet from the list." in response.data
    assert count_rows("Appointment") == before


def test_e10_missing_field_is_refused(client, count_rows):
    """E10: a request with no reason field at all, as a script could send."""
    before = count_rows("Appointment")
    form = dict(GOOD)
    del form["reason"]
    response = client.post("/appointments/new", data=form)
    assert b"Reason is required." in response.data
    assert count_rows("Appointment") == before


def test_e11_time_in_the_past_is_refused(client, count_rows):
    """E11: an appointment cannot be booked for a time that has passed."""
    before = count_rows("Appointment")
    response = submit(client, appt_time="2020-01-06 09:00")
    assert b"Choose a date and time that has not passed yet." in response.data
    assert count_rows("Appointment") == before


def test_e12_edit_runs_the_same_rules(client, fetch_one):
    """E12: the edit route refuses the same bad input the new route refuses."""
    response = client.post("/appointments/2/edit", data=dict(GOOD, reason=""))
    assert b"Reason is required." in response.data
    row = fetch_one("SELECT reason FROM Appointment WHERE appointment_id = 2")
    assert row["reason"] == "Dental cleaning"


# ---------------------------------------------------------------------------
# One rule tested directly, without the browser
# ---------------------------------------------------------------------------

def test_e13_validator_reports_every_problem_at_once(db_path):
    """E13: three bad fields give three messages in one list."""
    errors = validators.validate_appointment(
        pet_id="999", vet_id="1", appt_time="tomorrow", reason=""
    )
    assert len(errors) == 3


# ---------------------------------------------------------------------------
# Added later
# ---------------------------------------------------------------------------

def test_book_checkup_later_this_week(client, count_rows):
    """A checkup booked for Wednesday afternoon is accepted."""
    before = count_rows("Appointment")
    later = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d 14:00")
    response = submit(client, appt_time=later)
    assert response.status_code == 302
    assert count_rows("Appointment") == before + 1


def test_edit_page_for_a_missing_appointment(client):
    """Opening the edit page for an appointment that does not exist."""
    response = client.get("/appointments/999/edit")
    assert response.status_code == 404
