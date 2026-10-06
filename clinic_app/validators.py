"""
validators.py
=============
Every rule about what counts as usable input is written in this file.

Session 10's form accepted whatever arrived. An empty reason, a 4,000
character paragraph, the word "banana" where a date belongs, and a pet_id
for a pet that does not exist all went straight into the database.

The browser can be told to check some of that, by putting `required` and
`maxlength` on the input tags. Those attributes help the person filling in
the form and they stop nothing else. A request built without a browser
never sees them.

So the rules live here, and the route runs them before it calls models.py.

This file contains no SQL. When it needs to know which pets exist, it asks
models.py, the same way a route does.

The rules below are finished and working. In this copy, TODO 1 from
Session 11 (rejecting a time that has already passed) is filled in.
"""

from datetime import datetime

import models

# The format the appointment form expects, and the one build_db.py seeds.
TIME_FORMAT = "%Y-%m-%d %H:%M"
TIME_EXAMPLE = "2026-09-16 14:00"

MAX_REASON = 200


def validate_appointment(pet_id, vet_id, appt_time, reason):
    """Check one submitted appointment and return a list of problems.

    An empty list means the input is usable. Every other case returns one
    plain sentence per problem, written for the person who filled in the
    form rather than for a developer.

    The list is returned rather than raised, because a form with three
    problems should show all three at once instead of making the user
    discover them one submission at a time.
    """
    errors = []

    # --- reason -----------------------------------------------------------
    if not reason.strip():
        errors.append("Reason is required.")
    elif len(reason) > MAX_REASON:
        errors.append(
            "Reason must be %d characters or fewer. You entered %d."
            % (MAX_REASON, len(reason))
        )

    # --- appointment time -------------------------------------------------
    if not appt_time.strip():
        errors.append("Date and time are required.")
    else:
        try:
            when = datetime.strptime(appt_time, TIME_FORMAT)
        except ValueError:
            errors.append(
                "Date and time must look like %s." % TIME_EXAMPLE
            )
        else:
            # TODO 1 from Session 11, completed for this worked example.
            if when < datetime.now():
                errors.append("Choose a date and time that has not passed yet.")

    # --- pet and vet ------------------------------------------------------
    # request.form values are always strings, and the ids from the database
    # are integers, so both sides are compared as strings here.
    valid_pet_ids = {str(row["pet_id"]) for row in models.get_all_pets()}
    if pet_id not in valid_pet_ids:
        errors.append("Choose a pet from the list.")

    valid_vet_ids = {str(row["vet_id"]) for row in models.get_all_vets()}
    if vet_id not in valid_vet_ids:
        errors.append("Choose a vet from the list.")

    return errors
