"""
conftest.py
===========
Shared setup for every test in this folder. pytest reads this file
automatically before it runs any test.

What it does, in order, for every single test:

    1. Copies the real database file into a temporary folder.
    2. Points models.py at the copy, so a test that adds or deletes rows
       never touches the database you use in the browser.
    3. Hands the test a "client": a pretend browser that sends requests
       to the Flask app without starting a server.

When the test finishes, the copy is thrown away. Every test starts from
the same seed data, so the order the tests run in does not matter.

To use this file in your own A4 application, change the two settings
below if your names are different.
"""

import os
import shutil
import sqlite3
import sys

import pytest

# ---- The two settings to check ---------------------------------------------
DB_FILE = "clinic.db"         # your database file, in the same folder as app.py
DB_SETTING = "DATABASE"       # the name of the variable in models.py that holds it
# ----------------------------------------------------------------------------

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

import models  # noqa: E402
from app import app as flask_app  # noqa: E402


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """A fresh copy of the database for one test. Returns its path."""
    copy = tmp_path / "test.db"
    shutil.copy(os.path.join(APP_DIR, DB_FILE), copy)
    monkeypatch.setattr(models, DB_SETTING, str(copy))
    return str(copy)


@pytest.fixture
def client(db_path):
    """A pretend browser for the Flask app, using the copied database."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def count_rows(db_path):
    """count_rows("Appointment") returns how many rows that table has now."""
    def _count(table):
        """Count the rows in one table of the copied database."""
        db = sqlite3.connect(db_path)
        n = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        db.close()
        return n
    return _count


@pytest.fixture
def fetch_one(db_path):
    """fetch_one(sql, params) runs one SELECT on the copy and returns one row."""
    def _fetch(sql, params=()):
        """Run one SELECT on the copied database and return the first row."""
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        row = db.execute(sql, params).fetchone()
        db.close()
        return row
    return _fetch
