# The eval table behind the tests

This table is where the first thirteen tests in `clinic_app/tests/test_appointments.py` came from. Each row is an eval: a requirement, an input, an expected result, and the test that checks it. The test name starts with the eval number, so E7 is `test_e07_...`. The same table appears in the A7 worked example, where it is the model for the eval table you write.

This repository has two more tests at the bottom of the test file that are not in this table. All 15 pass.

| # | Kind | Requirement, in plain English | Input | Expected | Test |
|---|---|---|---|---|---|
| E1 | Normal | The list page shows each appointment with the pet's name from the Pet table. | GET `/appointments` | Status 200. The page contains "Buddy" and "Mango". | `test_e01` |
| E2 | Normal | A valid appointment is saved. | The new-appointment form with pet 1, vet 1, 2030-03-04 10:00, "Annual checkup" | Redirect (302). One more row in Appointment, with that reason and time. | `test_e02` |
| E3 | Normal | Editing an appointment saves the change. | Edit appointment 2 with reason "Follow-up visit" | Redirect. Appointment 2's reason is now "Follow-up visit". | `test_e03` |
| E4 | Normal | Deleting removes that appointment and no other. | POST delete for appointment 3 | One fewer row. Appointment 3 is gone. | `test_e04` |
| E5 | Boundary | A reason of up to 200 characters is allowed. | Reason of exactly 200 characters | The row is saved. | `test_e05` |
| E6 | Boundary | A reason over 200 characters is refused, with a message that says how long it was. | Reason of 201 characters | "Reason must be 200 characters or fewer. You entered 201." No row added. | `test_e06` |
| E7 | Bad input | A reason made only of spaces counts as empty. | Reason of five spaces | "Reason is required." No row added. | `test_e07` |
| E8 | Bad input | A date that does not exist is refused. | 2030-02-30 10:00 | "Date and time must look like 2026-09-16 14:00." No row added. | `test_e08` |
| E9 | Bad input | A pet that is not in the Pet table is refused. | pet_id 999 | "Choose a pet from the list." No row added. | `test_e09` |
| E10 | Bad input | A request with a field left out entirely is refused, the same as a blank one. | The form with no reason field at all | "Reason is required." No row added. | `test_e10` |
| E11 | Bad input | An appointment cannot be booked for a time that has passed. | 2020-01-06 09:00 | "Choose a date and time that has not passed yet." No row added. | `test_e11` |
| E12 | Bad input | The edit form applies the same rules as the new form. | Edit appointment 2 with an empty reason | "Reason is required." Appointment 2 still says "Dental cleaning". | `test_e12` |
| E13 | Rule, direct | The validator reports every problem at once. | `validate_appointment` with pet 999, time "tomorrow", empty reason | A list of 3 messages. | `test_e13` |

**What the Expected column does:** every row names something a person or a test can look at (a status code, a message, a row count, a stored value). None of them says "works" or "correct."

**Why E10 is separate from E7:** a browser always sends every field, but a script does not have to. The route uses `request.form.get("reason", "")` so that a missing field and a blank one are handled the same way. E10 is the test that would fail if someone changed that line.
