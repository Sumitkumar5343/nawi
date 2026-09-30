from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps
from datetime import datetime
import os

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "sih26035_secret_key"

DATABASE = "sih26035.db"


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_no TEXT UNIQUE NOT NULL,
            manufacturer TEXT,
            model TEXT,
            serial_no TEXT,
            instrument_type TEXT,
            max_capacity REAL,
            scale_interval REAL,
            accuracy_class TEXT,
            laboratory TEXT,
            location TEXT,
            temperature REAL,
            humidity REAL,
            inspector TEXT,
            test_date TEXT,
            status TEXT DEFAULT 'DRAFT',
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER,
            test_name TEXT,
            reference_value REAL,
            observed_value REAL,
            permissible_error REAL,
            error REAL,
            result TEXT,
            FOREIGN KEY(report_id) REFERENCES reports(id)
        )
    """)

    # Default admin
    cur.execute("SELECT * FROM users WHERE username = ?", ("admin",))

    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            "Administrator"
        ))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# LOGIN DECORATOR
# ---------------------------------------------------------

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/", methods=["GET"])
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db()

    total_reports = conn.execute(
        "SELECT COUNT(*) FROM reports"
    ).fetchone()[0]

    passed = conn.execute(
        "SELECT COUNT(*) FROM reports WHERE status = 'PASS'"
    ).fetchone()[0]

    failed = conn.execute(
        "SELECT COUNT(*) FROM reports WHERE status = 'FAIL'"
    ).fetchone()[0]

    drafts = conn.execute(
        "SELECT COUNT(*) FROM reports WHERE status = 'DRAFT'"
    ).fetchone()[0]

    recent_reports = conn.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_reports=total_reports,
        passed=passed,
        failed=failed,
        drafts=drafts,
        recent_reports=recent_reports
    )


# ---------------------------------------------------------
# NEW REPORT
# ---------------------------------------------------------

@app.route("/new-report", methods=["GET", "POST"])
@login_required
def new_report():

    if request.method == "POST":

        report_no = request.form.get("report_no")

        manufacturer = request.form.get("manufacturer")
        model = request.form.get("model")
        serial_no = request.form.get("serial_no")
        instrument_type = request.form.get("instrument_type")

        max_capacity = request.form.get("max_capacity")
        scale_interval = request.form.get("scale_interval")
        accuracy_class = request.form.get("accuracy_class")

        laboratory = request.form.get("laboratory")
        location = request.form.get("location")

        temperature = request.form.get("temperature")
        humidity = request.form.get("humidity")

        inspector = request.form.get("inspector")
        test_date = request.form.get("test_date")

        conn = get_db()

        try:

            conn.execute("""
                INSERT INTO reports (
                    report_no,
                    manufacturer,
                    model,
                    serial_no,
                    instrument_type,
                    max_capacity,
                    scale_interval,
                    accuracy_class,
                    laboratory,
                    location,
                    temperature,
                    humidity,
                    inspector,
                    test_date,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_no,
                manufacturer,
                model,
                serial_no,
                instrument_type,
                max_capacity or 0,
                scale_interval or 0,
                accuracy_class,
                laboratory,
                location,
                temperature or 0,
                humidity or 0,
                inspector,
                test_date,
                "DRAFT",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()

            report_id = conn.execute(
                "SELECT id FROM reports WHERE report_no = ?",
                (report_no,)
            ).fetchone()["id"]

            conn.close()

            return redirect(
                url_for("tests", report_id=report_id)
            )

        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "Report number already exists.",
                "danger"
            )

    return render_template("new_report.html")


# ---------------------------------------------------------
# TEST OBSERVATIONS
# ---------------------------------------------------------

@app.route("/tests/<int:report_id>", methods=["GET", "POST"])
@login_required
def tests(report_id):

    conn = get_db()

    report = conn.execute(
        "SELECT * FROM reports WHERE id = ?",
        (report_id,)
    ).fetchone()

    if report is None:

        conn.close()

        flash("Report not found.", "danger")

        return redirect(url_for("dashboard"))

    if request.method == "POST":

        test_name = request.form.get("test_name")

        reference_value = float(
            request.form.get("reference_value") or 0
        )

        observed_value = float(
            request.form.get("observed_value") or 0
        )

        permissible_error = float(
            request.form.get("permissible_error") or 0
        )

        error = observed_value - reference_value

        if abs(error) <= permissible_error:
            result = "PASS"
        else:
            result = "FAIL"

        conn.execute("""
            INSERT INTO tests (
                report_id,
                test_name,
                reference_value,
                observed_value,
                permissible_error,
                error,
                result
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            test_name,
            reference_value,
            observed_value,
            permissible_error,
            error,
            result
        ))

        conn.commit()

    test_records = conn.execute("""
        SELECT *
        FROM tests
        WHERE report_id = ?
        ORDER BY id
    """, (report_id,)).fetchall()

    conn.close()

    return render_template(
        "tests.html",
        report=report,
        tests=test_records
    )


# ---------------------------------------------------------
# FINALIZE REPORT
# ---------------------------------------------------------

@app.route("/finalize/<int:report_id>")
@login_required
def finalize(report_id):

    conn = get_db()

    tests_data = conn.execute("""
        SELECT *
        FROM tests
        WHERE report_id = ?
    """, (report_id,)).fetchall()

    if not tests_data:

        conn.close()

        flash(
            "Please add at least one test observation.",
            "warning"
        )

        return redirect(
            url_for("tests", report_id=report_id)
        )

    failed = False

    for test in tests_data:

        if test["result"] == "FAIL":
            failed = True
            break

    status = "FAIL" if failed else "PASS"

    conn.execute("""
        UPDATE reports
        SET status = ?
        WHERE id = ?
    """, (status, report_id))

    conn.commit()

    conn.close()

    return redirect(
        url_for("report", report_id=report_id)
    )


# ---------------------------------------------------------
# REPORT
# ---------------------------------------------------------

@app.route("/report/<int:report_id>")
@login_required
def report(report_id):

    conn = get_db()

    report_data = conn.execute("""
        SELECT *
        FROM reports
        WHERE id = ?
    """, (report_id,)).fetchone()

    tests_data = conn.execute("""
        SELECT *
        FROM tests
        WHERE report_id = ?
    """, (report_id,)).fetchall()

    conn.close()

    if report_data is None:

        flash("Report not found.", "danger")

        return redirect(url_for("dashboard"))

    return render_template(
        "report.html",
        report=report_data,
        tests=tests_data
    )


# ---------------------------------------------------------
# REPORT REPOSITORY
# ---------------------------------------------------------

@app.route("/reports")
@login_required
def reports():

    search = request.args.get("search", "")

    conn = get_db()

    if search:

        reports_data = conn.execute("""
            SELECT *
            FROM reports
            WHERE report_no LIKE ?
               OR manufacturer LIKE ?
               OR model LIKE ?
               OR serial_no LIKE ?
            ORDER BY id DESC
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        )).fetchall()

    else:

        reports_data = conn.execute("""
            SELECT *
            FROM reports
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "reports.html",
        reports=reports_data,
        search=search
    )


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
