from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__, template_folder="templates")
app.secret_key = "ngo_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "..", "aashray.db")

NGO_USERNAME = "ngo"
NGO_PASSWORD = "1234"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ngo_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        hospital_name TEXT,
        hospital_address TEXT,
        appointment_reason TEXT,
        appointment_date TEXT,
        appointment_time TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    if session.get("ngo_logged_in"):
        return redirect(url_for("ngo_dashboard"))
    return redirect(url_for("ngo_login"))


@app.route("/ngo-login", methods=["GET", "POST"])
def ngo_login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == NGO_USERNAME and password == NGO_PASSWORD:
            session["ngo_logged_in"] = True
            return redirect(url_for("ngo_dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("ngo_login.html", error=error)


@app.route("/ngo-dashboard")
def ngo_dashboard():
    if not session.get("ngo_logged_in"):
        return redirect(url_for("ngo_login"))

    conn = get_db()
    data = conn.execute(
        "SELECT * FROM ngo_requests ORDER BY id DESC"
    ).fetchall()
    conn.close()

    message = request.args.get("message", "")
    action_id = request.args.get("action_id", "")

    return render_template(
        "ngo_dashboard.html",
        data=data,
        message=message,
        action_id=action_id
    )


@app.route("/approve/<int:request_id>", methods=["POST"])
def approve(request_id):
    if not session.get("ngo_logged_in"):
        return redirect(url_for("ngo_login"))

    conn = get_db()
    conn.execute(
        "UPDATE ngo_requests SET status = 'Approved' WHERE id = ?",
        (request_id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("ngo_dashboard", message="approved", action_id=request_id))


@app.route("/reject/<int:request_id>", methods=["POST"])
def reject(request_id):
    if not session.get("ngo_logged_in"):
        return redirect(url_for("ngo_login"))

    conn = get_db()
    conn.execute(
        "UPDATE ngo_requests SET status = 'Rejected' WHERE id = ?",
        (request_id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("ngo_dashboard", message="rejected", action_id=request_id))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("ngo_login"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)