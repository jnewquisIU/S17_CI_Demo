"""
app.py
======
A small, "progressive" Flask demo built across Sessions 6 through 10:

    Session 6 - route() returns a hardcoded string, no templates.        -> home()
                                                                            greeting()
    Session 6/7 - route() builds a string in Python, still no templates. -> greeting()
    Session 7 - route() uses templates + Jinja, fed with Python data.    -> about()
    Session 8 - route() queries one table in clinic.db and renders it.
    Session 9 - the query joins four tables and moves into models.py.    -> appointments()
    Session 10 - three new routes write to the database.                 -> new_appointment()
                                                                            edit_appointment()
                                                                            delete_appointment()
    Session 11 - every write is checked before it runs.                  -> validators.py

Every route in Sessions 6 through 9 only read. The three routes at the bottom
of this file change what is stored, and all three are built the same way: show
a form, receive it, call one models.py function, redirect back to the list.

Session 11 puts one step in front of that: the route runs the submitted
values through validators.py first, and only calls models.py if nothing came
back. Nothing else about the four steps changed.

This is the Session 11 demo with its tests, for the Session 17 lab. The
tests are in the tests/ folder next to this file. Three of them fail. The lab
is about finding out why.

Run it with:
    python app.py
Then visit http://127.0.0.1:5000/ in a browser.

To put the database back the way it started, run:
    python build_db.py
"""

from datetime import datetime

from flask import Flask, abort, redirect, render_template, request, url_for

# models.py holds every SQL statement this application runs.
import models

# validators.py holds every rule about what counts as usable input.
import validators

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Route 1 (Session 6 concept): a fully hardcoded string, no templates at all.
# Notice the <link> tag below is a plain, "old school" HTML stylesheet
# reference. It is NOT using {{ url_for(...) }} because this page isn't
# rendered through Jinja, it is just a Python string being returned.
# ---------------------------------------------------------------------------
@app.route("/")
@app.route("/home")
def home():
    """Home page. Returns one HTML string. No template and no database."""
    html = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Flask Demo - Home</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <header>
            <h1>Flask Learning Demo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/greeting">Greeting</a>
                <a href="/about">About This Class</a>
                <a href="/appointments">Appointments</a>
                <a href="/vets">Vets</a>
            </nav>
        </header>
        <main>
            <h2>Welcome!</h2>
            <p>This is the simplest kind of Flask route: it just returns a
               plain string of HTML. No templates, no Python logic, no
               database. That's exactly how we started on Session 6.</p>
        </main>
        <footer>
            <p>Session 6 style route: hardcoded string</p>
        </footer>
    </body>
    </html>
    """
    return html


# ---------------------------------------------------------------------------
# Route 2 (Session 6/7 concept): still just a string, but this time Python
# code decides what the string says. Still no templates, no database.
# ---------------------------------------------------------------------------
@app.route("/greeting")
def greeting():
    """Greeting page. Picks Good morning, afternoon, or evening from the current hour."""
    current_hour = datetime.now().hour

    if current_hour < 12:
        message = "Good morning!"
    elif current_hour < 17:
        message = "Good afternoon!"
    else:
        message = "Good evening!"

    # We build the whole page as one Python string using an f-string.
    # The message changes based on the if/elif/else above.
    html = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Flask Demo - Greeting</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <header>
            <h1>Flask Learning Demo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/greeting">Greeting</a>
                <a href="/about">About This Class</a>
                <a href="/appointments">Appointments</a>
                <a href="/vets">Vets</a>
            </nav>
        </header>
        <main>
            <h2>{message}</h2>
            <p>The current server time is {current_hour}:00 (24-hour clock).
               A simple if/elif/else in Python picked the greeting above.</p>
        </main>
        <footer>
            <p>Session 6/7 style route: string built with Python logic</p>
        </footer>
    </body>
    </html>
    """
    return html


# ---------------------------------------------------------------------------
# Route 3 (Session 7 concept): uses templates. base.html defines the shared
# layout, about.html fills in the content block. We pass a dict and a
# list of dicts, no database involved.
# ---------------------------------------------------------------------------
@app.route("/about")
def about():
    """About page. Passes a small dict about the instructor to about.html."""
    instructor = {
        "name": "Ms. Rivera",
        "years_teaching": 6,
    }

    topics = [
        {
            "session": 6,
            "title": "Routes and hardcoded strings",
            "description": "Returning plain HTML strings from a view function.",
        },
        {
            "session": 7,
            "title": "Templates and Jinja",
            "description": "Passing dicts and lists into templates with render_template.",
        },
        {
            "session": 8,
            "title": "Databases",
            "description": "Querying one table in SQLite and rendering the results.",
        },
        {
            "session": 9,
            "title": "Joins and the model layer",
            "description": "Reading four tables in one query, written in models.py.",
        },
        {
            "session": 10,
            "title": "Writing to the database",
            "description": "Adding, editing, and removing rows through a form.",
        },
        {
            "session": 11,
            "title": "Server-side validation",
            "description": "Checking submitted values before anything is written.",
        },
    ]

    # render_template looks in the templates/ folder for about.html
    # and hands it the two Python variables below to use in Jinja.
    return render_template("about.html", instructor=instructor, topics=topics)


# ---------------------------------------------------------------------------
# Route 4 (Session 9 concept): the route contains no SQL.
#
# This version does three things: it matches the URL, calls models.py, and
# passes the result to a template.
# ---------------------------------------------------------------------------
@app.route("/appointments")
def appointments():
    """List page. Reads every appointment from the database and shows them in appointments.html."""
    rows = models.get_all_appointments()
    return render_template("appointments.html", appointments=rows)


@app.route("/vets")
def vets():
    """Vets page. Reads every vet from the database and shows them in vets.html."""
    rows = models.get_all_vets()
    return render_template("vets.html", vets=rows)


# ---------------------------------------------------------------------------
# Session 10: the three routes that write.
#
# All three follow the same four steps:
#     1. show a form              (GET)
#     2. receive the form         (POST)
#     3. call one models.py function that runs the SQL and commits
#     4. redirect back to the list
#
# Delete skips step 1, because there is nothing to fill in.
# ---------------------------------------------------------------------------

# CREATE. One URL, two jobs, decided by request.method. A GET renders the
# empty form. A POST inserts the row and sends the browser somewhere else.
@app.route("/appointments/new", methods=["GET", "POST"])
def new_appointment():
    """New-appointment form. A GET shows the empty form. A POST checks the fields with the validator, saves a new row if there are no problems, and otherwise shows the form again with the error messages."""
    if request.method == "POST":
        # The "" default matters. A request built without a browser can leave
        # a field out of the submission entirely, and .get returns None for a
        # field that was never sent. Defaulting to an empty string lets the
        # validator treat a missing field and a blank one the same way.
        submitted = {
            "pet_id": request.form.get("pet_id", ""),
            "vet_id": request.form.get("vet_id", ""),
            "appt_time": request.form.get("appt_time", ""),
            "reason": request.form.get("reason", ""),
        }
        # **submitted passes the dict's four entries as the four arguments,
        # the same way render_template has been taking heading=... all along.
        errors = validators.validate_appointment(**submitted)

        if not errors:
            models.insert_appointment(**submitted)
            # redirect sends the browser to a different URL instead of
            # returning a page here. Without it, a refresh would re-submit the
            # form and insert the same appointment a second time.
            return redirect(url_for("appointments"))

        # Something was wrong, so nothing was written. Render the same form
        # again with the problems listed and the submitted values still in the
        # fields, so nobody has to retype four boxes because one was wrong.
        return render_template(
            "appointment_form.html",
            heading="New Appointment",
            action_url=url_for("new_appointment"),
            appointment=submitted,
            errors=errors,
            pets=models.get_all_pets(),
            vets=models.get_all_vets(),
        )

    # A GET lands here. Every field starts empty, so the template does not
    # need to know whether it is creating or editing.
    blank = {"pet_id": "", "vet_id": "", "appt_time": "", "reason": ""}
    return render_template(
        "appointment_form.html",
        heading="New Appointment",
        action_url=url_for("new_appointment"),
        appointment=blank,
        errors=[],
        pets=models.get_all_pets(),
        vets=models.get_all_vets(),
    )


# UPDATE. <int:appointment_id> in the URL is new. Flask pulls that number out
# of the URL and passes it to the function as an argument, so /appointments/3/edit
# calls edit_appointment(appointment_id=3).
@app.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    """Edit form for one appointment. A GET shows the stored values. A POST checks the fields with the same validator, updates the row if there are no problems, and otherwise shows the form again with the error messages."""
    if models.get_appointment(appointment_id) is None:
        abort(404)

    if request.method == "POST":
        submitted = {
            "pet_id": request.form.get("pet_id", ""),
            "vet_id": request.form.get("vet_id", ""),
            "appt_time": request.form.get("appt_time", ""),
            "reason": request.form.get("reason", ""),
        }
        # The same function, called from a second route, so the rules exist
        # in exactly one file.
        errors = validators.validate_appointment(**submitted)

        if not errors:
            models.update_appointment(appointment_id, **submitted)
            return redirect(url_for("appointments"))

        return render_template(
            "appointment_form.html",
            heading="Edit Appointment",
            action_url=url_for("edit_appointment", appointment_id=appointment_id),
            appointment=submitted,
            errors=errors,
            pets=models.get_all_pets(),
            vets=models.get_all_vets(),
        )

    # A GET fills the same form with the values already stored.
    return render_template(
        "appointment_form.html",
        heading="Edit Appointment",
        action_url=url_for("edit_appointment", appointment_id=appointment_id),
        appointment=models.get_appointment(appointment_id),
        errors=[],
        pets=models.get_all_pets(),
        vets=models.get_all_vets(),
    )


# DELETE. methods=["POST"] only, on purpose. A plain link is a GET, and
# browsers, bookmarks, and crawlers follow GET links on their own. A row
# should only disappear because a person pressed a button.
@app.route("/appointments/<int:appointment_id>/delete", methods=["POST"])
def delete_appointment(appointment_id):
    """Delete one appointment by its id, then go back to the list. POST only."""
    models.delete_appointment(appointment_id)
    return redirect(url_for("appointments"))


if __name__ == "__main__":
    # debug=False: keep error pages simple for class instead of the Werkzeug debugger.
    app.run(debug=False)
