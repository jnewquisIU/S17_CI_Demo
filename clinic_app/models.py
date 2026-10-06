"""
models.py
=========
Every SQL statement this application runs is written in this file.

Session 9 split the database job out of app.py and put it here. Everything in
this file so far has been a SELECT, which only reads. Session 10 adds three
functions that change what is stored: an INSERT, an UPDATE, and a DELETE.

Two things a write needs that a read did not:

    1. db.commit(). Until commit runs, the change exists only inside this
       connection. Close without committing and the change is gone.
    2. The ? placeholder. Values from a form are passed as a separate tuple,
       never pasted into the SQL string. See insert_appointment below.

This file still contains no URLs and builds no HTML.
"""

import sqlite3

# The database file this application reads and writes. It sits in this folder.
DATABASE = "clinic.db"


def get_connection():
    """Open a connection to clinic.db and return it.

    Setting row_factory makes sqlite3 return rows that can be read by column
    name, so a template can write appt.pet_name instead of appt[2].
    """
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_all_appointments():
    """Return every appointment, with the pet, owner, and vet names included.

    New in Session 10: the SELECT now also returns Appointment.appointment_id.
    The list page needs it, because every row on that page now carries an Edit
    link and a Delete button, and both have to say which row they mean.
    """
    db = get_connection()
    rows = db.execute(
        """
        SELECT Appointment.appointment_id,
               Appointment.appt_time,
               Appointment.reason,
               Pet.name    AS pet_name,
               Pet.species AS species,
               Owner.name  AS owner_name,
               Vet.name    AS vet_name
        FROM Appointment
        JOIN Pet   ON Appointment.pet_id = Pet.pet_id
        JOIN Owner ON Pet.owner_id       = Owner.owner_id
        JOIN Vet   ON Appointment.vet_id = Vet.vet_id
        ORDER BY Appointment.appt_time
        """
    ).fetchall()
    db.close()
    return rows


def get_appointment(appointment_id):
    """Return the one appointment row with this id, or None if there isn't one.

    The edit form calls this to fill its fields with the values already stored.
    fetchone() returns a single row instead of a list of them.
    """
    db = get_connection()
    row = db.execute(
        "SELECT * FROM Appointment WHERE appointment_id = ?",
        (appointment_id,),
    ).fetchone()
    db.close()
    return row


def get_all_pets():
    """Return every pet with its owner's name, for the form's Pet dropdown."""
    db = get_connection()
    rows = db.execute(
        """
        SELECT Pet.pet_id, Pet.name AS pet_name, Owner.name AS owner_name
        FROM Pet
        JOIN Owner ON Pet.owner_id = Owner.owner_id
        ORDER BY Pet.name
        """
    ).fetchall()
    db.close()
    return rows


def get_all_vets():
    """Return every vet. One table, no join needed."""
    db = get_connection()
    rows = db.execute(
        "SELECT vet_id, name, specialty FROM Vet ORDER BY name"
    ).fetchall()
    db.close()
    return rows


# ---------------------------------------------------------------------------
# WRITE
#
# All three functions below have the same five lines: open a connection, run
# one statement, commit, close, done. Only the SQL verb changes.
# ---------------------------------------------------------------------------

def insert_appointment(pet_id, vet_id, appt_time, reason):
    """Add one new appointment row.

    The four question marks are placeholders. sqlite3 substitutes the values
    from the tuple on the next line, and it escapes them while doing it. Never
    build this string with an f-string: a reason of

        Annual checkup'); DELETE FROM Appointment; --

    typed into the form would then run as SQL instead of being stored as text.
    """
    db = get_connection()
    db.execute(
        """
        INSERT INTO Appointment (pet_id, vet_id, appt_time, reason)
        VALUES (?, ?, ?, ?)
        """,
        (pet_id, vet_id, appt_time, reason),
    )
    db.commit()
    db.close()


def update_appointment(appointment_id, pet_id, vet_id, appt_time, reason):
    """Change the four editable columns on one existing appointment.

    The WHERE clause is what limits this to a single row. An UPDATE with no
    WHERE changes every row in the table.
    """
    db = get_connection()
    db.execute(
        """
        UPDATE Appointment
        SET pet_id = ?, vet_id = ?, appt_time = ?, reason = ?
        WHERE appointment_id = ?
        """,
        (pet_id, vet_id, appt_time, reason, appointment_id),
    )
    db.commit()
    db.close()


def delete_appointment(appointment_id):
    """Remove one appointment row.

    Same WHERE warning as above, and it matters more here. A DELETE with no
    WHERE empties the table.
    """
    db = get_connection()
    db.execute(
        "DELETE FROM Appointment WHERE appointment_id = ?",
        (appointment_id,),
    )
    db.commit()
    db.close()
