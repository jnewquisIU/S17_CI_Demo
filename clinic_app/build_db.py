"""
build_db.py
===========
Creates clinic.db and fills it with seed data.

The four tables below are the same ones modeled in Session 4 and queried in
Session 5. Nothing about the schema changed for Session 9. The appointment
list now reads names out of Pet, Owner, and Vet, using the id numbers stored
in Appointment to find them.

Run this only if you want to start over with a fresh database:

    python build_db.py

It deletes any existing clinic.db in this folder first.
"""

import os
import sqlite3

DATABASE = "clinic.db"

SCHEMA = """
CREATE TABLE Owner (
  owner_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT NOT NULL
);

CREATE TABLE Pet (
  pet_id INTEGER PRIMARY KEY,
  owner_id INTEGER NOT NULL REFERENCES Owner(owner_id),
  name TEXT NOT NULL,
  species TEXT NOT NULL
);

CREATE TABLE Vet (
  vet_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  specialty TEXT NOT NULL
);

CREATE TABLE Appointment (
  appointment_id INTEGER PRIMARY KEY,
  pet_id INTEGER NOT NULL REFERENCES Pet(pet_id),
  vet_id INTEGER NOT NULL REFERENCES Vet(vet_id),
  appt_time TEXT NOT NULL,
  reason TEXT NOT NULL
);
"""

OWNERS = [
    (1, "Maria Chen", "812-555-0143"),
    (2, "Darnell Brooks", "812-555-0192"),
    (3, "Priya Raman", "812-555-0177"),
]

PETS = [
    (1, 1, "Buddy", "Dog"),
    (2, 1, "Whiskers", "Cat"),
    (3, 2, "Mango", "Parrot"),
    (4, 3, "Tucker", "Dog"),
]

VETS = [
    (1, "Dr. Alvarez", "Small animal"),
    (2, "Dr. Kim", "Exotics"),
]

APPOINTMENTS = [
    (1, 1, 1, "2026-09-14 09:00", "Annual checkup"),
    (2, 2, 1, "2026-09-14 10:30", "Dental cleaning"),
    (3, 3, 2, "2026-09-14 11:15", "Beak trim"),
    (4, 4, 1, "2026-09-14 13:45", "Limping on left front paw"),
    (5, 1, 1, "2026-09-15 08:30", "Vaccine booster"),
]


def main():
    """Delete any old database file, create the tables, insert the sample rows, and print a summary."""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    db = sqlite3.connect(DATABASE)
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO Owner VALUES (?, ?, ?)", OWNERS)
    db.executemany("INSERT INTO Pet VALUES (?, ?, ?, ?)", PETS)
    db.executemany("INSERT INTO Vet VALUES (?, ?, ?)", VETS)
    db.executemany("INSERT INTO Appointment VALUES (?, ?, ?, ?, ?)", APPOINTMENTS)
    db.commit()
    db.close()

    print("Created %s with %d owners, %d pets, %d vets, %d appointments." % (
        DATABASE, len(OWNERS), len(PETS), len(VETS), len(APPOINTMENTS)))


if __name__ == "__main__":
    main()
