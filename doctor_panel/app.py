from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "doctor_secret"
app.config["SESSION_COOKIE_NAME"] = "doctor_session"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "..", "aashray.db")

DOCTOR_USERNAME = "doctor"
DOCTOR_PASSWORD = "1234"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    if session.get("doctor_logged_in"):
        return redirect(url_for("doctor_dashboard"))
    return redirect(url_for("doctor_login"))


@app.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == DOCTOR_USERNAME and password == DOCTOR_PASSWORD:
            session["doctor_logged_in"] = True
            return redirect(url_for("doctor_dashboard"))

    return render_template("doctor_login.html")


@app.route("/doctor-dashboard")
def doctor_dashboard():
    if not session.get("doctor_logged_in"):
        return redirect(url_for("doctor_login"))

    conn = get_db()
    appointments = conn.execute("""
        SELECT * FROM appointments
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    return render_template("doctor_dashboard.html", appointments=appointments)


@app.route("/approve/<int:appointment_id>", methods=["POST"])
def approve(appointment_id):
    if not session.get("doctor_logged_in"):
        return redirect(url_for("doctor_login"))

    conn = get_db()
    conn.execute("""
        UPDATE appointments
        SET status = 'Approved'
        WHERE id = ?
    """, (appointment_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("doctor_dashboard"))


@app.route("/reject/<int:appointment_id>", methods=["POST"])
def reject(appointment_id):
    if not session.get("doctor_logged_in"):
        return redirect(url_for("doctor_login"))

    conn = get_db()
    conn.execute("""
        UPDATE appointments
        SET status = 'Rejected'
        WHERE id = ?
    """, (appointment_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("doctor_dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("doctor_login"))


if __name__ == "__main__":
    app.run(port=5002, debug=True)