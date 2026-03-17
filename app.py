import os
import sqlite3
import base64
from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ecomess-secret-key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DATABASE ---------------- #

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'student',
        hostel TEXT,
        branch TEXT,
        mess_name TEXT,
        ngo_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        before_image TEXT,
        after_image TEXT,
        before_food_area REAL,
        after_food_area REAL,
        food_served_grams REAL,
        leftover_grams REAL,
        leftover_percentage REAL,
        coins INTEGER,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HELPERS ---------------- #

def get_user_by_email(email):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def create_user(full_name, email, password, role="student", hostel=None, branch=None, mess_name=None, ngo_name=None):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO users (full_name, email, password, role, hostel, branch, mess_name, ngo_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, password, role, hostel, branch, mess_name, ngo_name))
    conn.commit()
    conn.close()


def login_required():
    return "user_id" in session


def student_only():
    return login_required() and session.get("user_role") == "student"


def staff_only():
    return login_required() and session.get("user_role") == "staff"


def ngo_only():
    return login_required() and session.get("user_role") == "ngo"


# ---------------- STUDENT HELPERS ---------------- #

def get_total_meals(user_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT COUNT(*) AS total
        FROM meal_sessions
        WHERE user_id = ? AND status IN ('green', 'yellow', 'red')
    """, (user_id,)).fetchone()
    conn.close()
    return row["total"] if row else 0


def get_total_coins(user_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT COALESCE(SUM(coins), 0) AS total
        FROM meal_sessions
        WHERE user_id = ? AND status IN ('green', 'yellow', 'red')
    """, (user_id,)).fetchone()
    conn.close()
    return row["total"] if row else 0


def get_latest_meal(user_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT *
        FROM meal_sessions
        WHERE user_id = ? AND status IN ('green', 'yellow', 'red')
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()
    conn.close()
    return row


def get_meal_history(user_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT *
        FROM meal_sessions
        WHERE user_id = ? AND status IN ('green', 'yellow', 'red')
        ORDER BY id DESC
    """, (user_id,)).fetchall()
    conn.close()
    return rows


def get_recent_meals(user_id, limit=5):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT *
        FROM meal_sessions
        WHERE user_id = ? AND status IN ('green', 'yellow', 'red')
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return rows


def get_leaderboard_data():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            users.id,
            users.full_name,
            users.email,
            users.hostel,
            COALESCE(SUM(meal_sessions.coins), 0) AS total_coins,
            COUNT(meal_sessions.id) AS total_meals
        FROM users
        LEFT JOIN meal_sessions
            ON users.id = meal_sessions.user_id
            AND meal_sessions.status IN ('green', 'yellow', 'red')
        WHERE users.role = 'student'
        GROUP BY users.id, users.full_name, users.email, users.hostel
        ORDER BY total_coins DESC, total_meals DESC, users.full_name ASC
    """).fetchall()
    conn.close()
    return rows


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return redirect("/choose-role")


@app.route("/choose-role")
def choose_role():
    return render_template("choose_role.html")


# ---------------- STUDENT AUTH ---------------- #

@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        hostel = request.form.get("hostel", "").strip()
        branch = request.form.get("branch", "").strip()

        if not full_name or not email or not password or not hostel or not branch:
            flash("All fields are required.")
            return redirect("/register/student")

        if get_user_by_email(email):
            flash("Email already registered.")
            return redirect("/login")

        create_user(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            role="student",
            hostel=hostel,
            branch=branch
        )
        flash("Student registration successful.")
        return redirect("/login")

    return render_template("register_student.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = get_user_by_email(email)

        if user and user["password"] and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            if user["role"] == "staff":
                return redirect("/staff-dashboard")
            if user["role"] == "ngo":
                return redirect("/ngo-dashboard")
            return redirect("/dashboard")

        flash("Invalid email or password.")
        return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/choose-role")


# ---------------- STUDENT FLOW ---------------- #

@app.route("/dashboard")
def dashboard():
    if not student_only():
        return redirect("/login")

    return render_template(
        "dashboard_mobile.html",
        user_name=session["user_name"],
        total_scans=get_total_meals(session["user_id"]),
        total_coins=get_total_coins(session["user_id"]),
        latest_scan=get_latest_meal(session["user_id"])
    )


@app.route("/start-meal")
def start_meal():
    if not student_only():
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO meal_sessions (user_id, status) VALUES (?, ?)",
        (session["user_id"], "started")
    )
    meal_id = cur.lastrowid
    conn.commit()
    conn.close()

    return redirect(f"/scan-before/{meal_id}")


@app.route("/scan-before/<int:meal_id>")
def scan_before(meal_id):
    if not student_only():
        return redirect("/login")
    return render_template("scan_before.html", meal_id=meal_id)


@app.route("/save-before/<int:meal_id>", methods=["POST"])
def save_before(meal_id):
    if not student_only():
        return redirect("/login")

    file = request.files.get("image")
    captured_image = request.form.get("captured_image", "").strip()

    filename = f"before_{meal_id}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)

    if file and file.filename:
        file.save(path)
    elif captured_image:
        try:
            if "," in captured_image:
                _, encoded = captured_image.split(",", 1)
            else:
                encoded = captured_image
            with open(path, "wb") as f:
                f.write(base64.b64decode(encoded))
        except Exception:
            flash("Before image process failed.")
            return redirect(f"/scan-before/{meal_id}")
    else:
        flash("Please capture or select before image.")
        return redirect(f"/scan-before/{meal_id}")

    before_food_area = 12000

    conn = get_db_connection()
    conn.execute("""
        UPDATE meal_sessions
        SET before_image = ?, before_food_area = ?, status = ?
        WHERE id = ?
    """, (filename, before_food_area, "before_done", meal_id))
    conn.commit()
    conn.close()

    return redirect(f"/scan-after/{meal_id}")


@app.route("/scan-after/<int:meal_id>")
def scan_after(meal_id):
    if not student_only():
        return redirect("/login")
    return render_template("scan_after.html", meal_id=meal_id)


@app.route("/save-after/<int:meal_id>", methods=["POST"])
def save_after(meal_id):
    if not student_only():
        return redirect("/login")

    file = request.files.get("image")
    captured_image = request.form.get("captured_image", "").strip()

    filename = f"after_{meal_id}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)

    if file and file.filename:
        file.save(path)
    elif captured_image:
        try:
            if "," in captured_image:
                _, encoded = captured_image.split(",", 1)
            else:
                encoded = captured_image
            with open(path, "wb") as f:
                f.write(base64.b64decode(encoded))
        except Exception:
            flash("After image process failed.")
            return redirect(f"/scan-after/{meal_id}")
    else:
        flash("Please capture or select after image.")
        return redirect(f"/scan-after/{meal_id}")

    conn = get_db_connection()
    meal = conn.execute(
        "SELECT before_food_area FROM meal_sessions WHERE id = ?",
        (meal_id,)
    ).fetchone()

    if not meal or not meal["before_food_area"]:
        conn.close()
        flash("Before scan missing.")
        return redirect("/dashboard")

    before_food_area = meal["before_food_area"]
    after_food_area = 3000

    food_served_grams = round(before_food_area / 20, 1)
    leftover_grams = round(after_food_area / 20, 1)

    conn.execute("""
        UPDATE meal_sessions
        SET after_image = ?, after_food_area = ?, food_served_grams = ?, leftover_grams = ?, status = ?
        WHERE id = ?
    """, (filename, after_food_area, food_served_grams, leftover_grams, "weight_pending", meal_id))
    conn.commit()
    conn.close()

    return redirect(f"/meal-weight/{meal_id}")


@app.route("/meal-weight/<int:meal_id>")
def meal_weight(meal_id):
    if not student_only():
        return redirect("/login")

    conn = get_db_connection()
    meal = conn.execute("SELECT * FROM meal_sessions WHERE id = ?", (meal_id,)).fetchone()
    conn.close()

    if not meal:
        return redirect("/dashboard")

    return render_template("meal_weight.html", meal=meal)


@app.route("/calculate-waste/<int:meal_id>", methods=["POST"])
def calculate_waste(meal_id):
    if not student_only():
        return redirect("/login")

    try:
        food_served_grams = float(request.form.get("food_served_grams", 0) or 0)
        leftover_grams = float(request.form.get("leftover_grams", 0) or 0)
    except ValueError:
        flash("Enter valid numbers.")
        return redirect(f"/meal-weight/{meal_id}")

    if food_served_grams <= 0:
        flash("Food served must be greater than 0.")
        return redirect(f"/meal-weight/{meal_id}")

    leftover_percentage = round((leftover_grams / food_served_grams) * 100, 2)

    if leftover_percentage <= 10:
        coins = 10
        status = "green"
    elif leftover_percentage <= 25:
        coins = 7
        status = "green"
    elif leftover_percentage <= 50:
        coins = 3
        status = "yellow"
    else:
        coins = 0
        status = "red"

    conn = get_db_connection()
    conn.execute("""
        UPDATE meal_sessions
        SET food_served_grams = ?, leftover_grams = ?, leftover_percentage = ?, coins = ?, status = ?
        WHERE id = ?
    """, (food_served_grams, leftover_grams, leftover_percentage, coins, status, meal_id))
    conn.commit()
    conn.close()

    return redirect(f"/meal-success/{meal_id}")


@app.route("/meal-success/<int:meal_id>")
def meal_success(meal_id):
    if not student_only():
        return redirect("/login")

    conn = get_db_connection()
    meal = conn.execute("SELECT * FROM meal_sessions WHERE id = ?", (meal_id,)).fetchone()
    conn.close()

    return render_template(
        "meal_success.html",
        meal=meal,
        recent_meals=get_recent_meals(session["user_id"])
    )


@app.route("/history")
def history():
    if not student_only():
        return redirect("/login")

    return render_template(
        "history.html",
        user_name=session["user_name"],
        scan_history=get_meal_history(session["user_id"])
    )


@app.route("/leaderboard")
def leaderboard():
    if not student_only():
        return redirect("/login")

    return render_template(
        "leaderboard.html",
        user_name=session["user_name"],
        leaderboard_data=get_leaderboard_data()
    )


@app.route("/profile")
def profile():
    if not student_only():
        return redirect("/login")

    return render_template(
        "profile.html",
        user_name=session["user_name"],
        user_email=session.get("user_email", ""),
        total_scans=get_total_meals(session["user_id"]),
        total_coins=get_total_coins(session["user_id"])
    )


# ---------------- STAFF FLOW ---------------- #

@app.route("/staff-auth")
def staff_auth():
    return render_template("staff_auth.html")


@app.route("/register/staff", methods=["GET", "POST"])
def register_staff():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        mess_name = request.form.get("mess_name", "").strip()

        if not full_name or not email or not password or not mess_name:
            flash("All fields are required.")
            return redirect("/register/staff")

        if get_user_by_email(email):
            flash("Email already registered.")
            return redirect("/staff-login")

        create_user(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            role="staff",
            mess_name=mess_name
        )
        flash("Staff registration successful.")
        return redirect("/staff-login")

    return render_template("register_staff.html")


@app.route("/staff-login", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = get_user_by_email(email)

        if user and user["password"] and check_password_hash(user["password"], password):
            if user["role"] != "staff":
                flash("This account is not a mess staff account.")
                return redirect("/staff-login")

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            return redirect("/staff-dashboard")

        flash("Invalid email or password.")
        return redirect("/staff-login")

    return render_template("staff_login.html")


@app.route("/staff-dashboard")
def staff_dashboard():
    if not staff_only():
        return redirect("/staff-login")

    stats = {
        "food_cooked": 652,
        "food_wasted": 78,
        "waste_percent": 12.0,
        "most_wasted": "Rajma",
        "most_wasted_qty": 16
    }

    suggestions = [
        "Reduce Raita quantity by 25% tomorrow",
        "Predicted demand for tomorrow: 619 kg based on trends"
    ]

    return render_template(
        "staff_dashboard.html",
        user_name=session["user_name"],
        stats=stats,
        suggestions=suggestions
    )


@app.route("/staff-menu")
def staff_menu():
    if not staff_only():
        return redirect("/staff-login")

    menu_items = [
        {"category": "Main Course", "name": "Chole", "cooked": 69, "wasted": 9, "waste_percent": 13},
        {"category": "Side", "name": "Kheer", "cooked": 69, "wasted": 6, "waste_percent": 9},
        {"category": "Others", "name": "Pulao", "cooked": 40, "wasted": 3, "waste_percent": 8},
        {"category": "Others", "name": "Soup", "cooked": 34, "wasted": 5, "waste_percent": 15},
        {"category": "Others", "name": "Gulab Jamun", "cooked": 20, "wasted": 2, "waste_percent": 10},
    ]

    return render_template("staff_menu.html", menu_items=menu_items)


@app.route("/staff-analytics")
def staff_analytics():
    if not staff_only():
        return redirect("/staff-login")

    metrics = {
        "total_students": 20,
        "avg_waste_student": 2018,
        "waste_rate": 12.0
    }

    return render_template("staff_analytics.html", metrics=metrics)


@app.route("/staff-settings", methods=["GET", "POST"])
def staff_settings():
    if not staff_only():
        return redirect("/staff-login")

    if request.method == "POST":
        flash("Notification sent successfully.")
        return redirect("/staff-settings")

    return render_template("staff_settings.html")


# ---------------- NGO FLOW ---------------- #

@app.route("/ngo-auth")
def ngo_auth():
    return render_template("ngo_auth.html")


@app.route("/register/ngo", methods=["GET", "POST"])
def register_ngo():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        ngo_name = request.form.get("ngo_name", "").strip()

        if not full_name or not email or not password or not ngo_name:
            flash("All fields are required.")
            return redirect("/register/ngo")

        if get_user_by_email(email):
            flash("Email already registered.")
            return redirect("/ngo-login")

        create_user(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            role="ngo",
            ngo_name=ngo_name
        )
        flash("NGO registration successful.")
        return redirect("/ngo-login")

    return render_template("register_ngo.html")


@app.route("/ngo-login", methods=["GET", "POST"])
def ngo_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = get_user_by_email(email)

        if user and user["password"] and check_password_hash(user["password"], password):
            if user["role"] != "ngo":
                flash("This account is not an NGO account.")
                return redirect("/ngo-login")

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            return redirect("/ngo-dashboard")

        flash("Invalid email or password.")
        return redirect("/ngo-login")

    return render_template("ngo_login.html")


@app.route("/ngo-dashboard")
def ngo_dashboard():
    if not ngo_only():
        return redirect("/ngo-login")

    stats = {
        "available": 2,
        "accepted": 2,
        "in_transit": 2,
        "delivered": 2,
        "total_rescued": 87,
        "delivered_kg": 19
    }

    recent_available = [
        {"food_name": "Dal", "quantity_kg": 6, "date": "2026-03-13", "status": "Available"},
        {"food_name": "Raita", "quantity_kg": 10, "date": "2026-03-09", "status": "Available"},
    ]

    weekly_counts = [3, 5, 2, 8, 4, 6, 2]

    return render_template(
        "ngo_dashboard.html",
        user_name=session["user_name"],
        stats=stats,
        recent_available=recent_available,
        weekly_counts=weekly_counts
    )


@app.route("/ngo-surplus")
def ngo_surplus():
    if not ngo_only():
        return redirect("/ngo-login")

    surplus_items = [
        {
            "id": 1,
            "food_name": "Dal",
            "quantity_kg": 6,
            "date": "2026-03-13",
            "accepted_by": "Food Bank NGO",
            "pickup_time": "2:00 PM",
            "status": "available"
        },
        {
            "id": 2,
            "food_name": "Kheer",
            "quantity_kg": 13,
            "date": "2026-03-12",
            "accepted_by": "",
            "pickup_time": "2:00 PM",
            "status": "accepted"
        },
        {
            "id": 3,
            "food_name": "Paneer Curry",
            "quantity_kg": 11,
            "date": "2026-03-11",
            "accepted_by": "Food Bank NGO",
            "pickup_time": "2:00 PM",
            "status": "in_transit"
        },
        {
            "id": 4,
            "food_name": "Idli",
            "quantity_kg": 5,
            "date": "2026-03-10",
            "accepted_by": "Food Bank NGO",
            "pickup_time": "2:00 PM",
            "status": "delivered"
        },
        {
            "id": 5,
            "food_name": "Raita",
            "quantity_kg": 10,
            "date": "2026-03-09",
            "accepted_by": "",
            "pickup_time": "2:00 PM",
            "status": "available"
        }
    ]

    return render_template("ngo_surplus.html", surplus_items=surplus_items)


@app.route("/ngo-tracking")
def ngo_tracking():
    if not ngo_only():
        return redirect("/ngo-login")

    tracking_items = [
        {
            "food_name": "Kheer",
            "quantity_kg": 13,
            "date": "2026-03-12",
            "pickup_time": "2:00 PM",
            "status": "accepted"
        },
        {
            "food_name": "Paneer Curry",
            "quantity_kg": 11,
            "date": "2026-03-11",
            "pickup_time": "2:00 PM",
            "status": "in_transit"
        },
        {
            "food_name": "Idli",
            "quantity_kg": 5,
            "date": "2026-03-10",
            "pickup_time": "2:00 PM",
            "status": "delivered"
        }
    ]

    return render_template("ngo_tracking.html", tracking_items=tracking_items)


if __name__ == "__main__":
    app.run(debug=True)