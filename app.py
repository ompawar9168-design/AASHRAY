from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.secret_key = "aashray_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "aashray.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

translations = {
    "en": {
        "app_name": "AASHRAY",
        "subtitle": "Healthcare Support for 50+ Citizens",
        "select_language": "Select Language",
        "choose_language": "Choose your preferred language to continue",
        "continue": "Continue",
        "upload_aadhaar": "Upload Aadhaar Card",
        "upload_text": "Please upload your Aadhaar card for age verification",
        "selected_file": "Selected File",
        "verify_now": "Verify Now",
        "verification_result": "Verification Result",
        "autofilled_details": "Autofilled Details",
        "name": "Name",
        "age": "Age",
        "location": "Location",
        "verified": "Verified",
        "eligible": "Eligible",
        "invalid": "Invalid",
        "invalid_age": "Invalid Age. Only 50+ users can proceed.",
        "cannot_proceed": "Cannot Proceed",
        "valid_age": "Age verified successfully. You can proceed.",
        "proceed": "Proceed",
        "ngo": "NGO",
        "reminder": "Medical Reminder",
        "sos": "SOS",
        "appointment": "Appointment",
        "go_back": "Go Back",
        "dashboard_title": "Main Dashboard",
        "dashboard_text": "Choose an option to continue.",
        "welcome_user": "Welcome",
        "ngo_text": "Request NGO support and track approval status.",
        "reminder_text": "Set tablet reminders and medicine alerts.",
        "sos_text": "Use emergency SOS support in urgent situations.",
        "appointment_text": "Book medical appointments and hospital visits.",
        "back_dashboard": "Back to Dashboard",
        "hospital_name": "Hospital Name",
        "hospital_address": "Hospital Address",
        "appointment_reason": "Appointment Reason",
        "appointment_date": "Appointment Date",
        "appointment_time": "Appointment Time",
        "submit_request": "Submit Request",
        "ngo_status": "NGO Request Status",
        "status": "Status",
        "pending": "Pending",
        "approved": "Approved",
        "rejected": "Rejected",
        "no_requests": "No requests found.",
        "view_status": "View Status",
        "reminder_form_title": "Set Medicine Reminder",
        "medicine_name": "Medicine Name",
        "start_date": "Start Date",
        "time": "Time",
        "total_days": "Total Days",
        "note": "Optional Note",
        "save_reminder": "Save Reminder",
        "my_reminders": "My Reminders",
        "no_reminders": "No reminders found.",
        "call_from": "AASHRAY Reminder",
        "incoming_call": "Incoming Reminder Call",
        "receive": "Receive",
        "dismiss": "Dismiss",
        "tablet_message": "It is time to take your tablet.",
        "days_left": "Days Left",
        "completed": "Completed",
        "active": "Active",
        "doctor_type": "Doctor Type",
        "choose_doctor_type": "Choose doctor type",
        "general_physician": "General Physician",
        "cardiology": "Cardiology",
        "orthopedic": "Orthopedic",
        "neurology": "Neurology",
        "eye_specialist": "Eye Specialist",
        "ent": "ENT",
        "show_doctors": "Show Doctors",
        "available_doctors": "Available Doctors",
        "specialization": "Specialization",
        "experience": "Experience",
        "fees": "Consulting Fees",
        "available_slot": "Available Slot",
        "current_location": "Current Location",
        "select_doctor": "Select Doctor",
        "my_appointments": "My Appointments",
        "doctor_name": "Doctor Name",
        "selected_doctor_type": "Selected Doctor Type",
        "no_doctors_found": "No doctors found for this category.",
        "permanent_disease": "Permanent Disease",
        "no_previous_record": "No previous record",
        "first_time_appointment": "First Time Appointment",
        "repeat_appointment": "Repeat Appointment",
        "tell_permanent_disease": "Tell your permanent disease",
        "doctor_needed": "Which type of doctor do you need?"
    }
}


DOCTOR_DATA = {
    "general": [
        {
            "name": "Dr. Amit Sharma",
            "specialization": "General Physician",
            "experience": "12 years",
            "fees": "₹500",
            "slot": "10:00 AM - 11:00 AM",
            "hospital": "City Care Hospital",
            "location": "Nagpur"
        },
        {
            "name": "Dr. Meera Patil",
            "specialization": "General Physician",
            "experience": "8 years",
            "fees": "₹400",
            "slot": "4:00 PM - 5:00 PM",
            "hospital": "Health First Clinic",
            "location": "Nagpur"
        }
    ],
    "cardiology": [
        {
            "name": "Dr. Rohan Kulkarni",
            "specialization": "Cardiologist",
            "experience": "15 years",
            "fees": "₹900",
            "slot": "1:00 PM - 2:00 PM",
            "hospital": "Heart Plus Hospital",
            "location": "Nagpur"
        }
    ],
    "orthopedic": [
        {
            "name": "Dr. Sandeep Verma",
            "specialization": "Orthopedic",
            "experience": "10 years",
            "fees": "₹700",
            "slot": "5:00 PM - 6:00 PM",
            "hospital": "Bone & Joint Center",
            "location": "Nagpur"
        }
    ],
    "neurology": [
        {
            "name": "Dr. Kavita Rao",
            "specialization": "Neurologist",
            "experience": "11 years",
            "fees": "₹1000",
            "slot": "12:00 PM - 1:00 PM",
            "hospital": "Neuro Care Hospital",
            "location": "Nagpur"
        }
    ],
    "eye": [
        {
            "name": "Dr. Pooja Deshmukh",
            "specialization": "Eye Specialist",
            "experience": "9 years",
            "fees": "₹600",
            "slot": "3:00 PM - 4:00 PM",
            "hospital": "Vision Eye Center",
            "location": "Nagpur"
        }
    ],
    "ent": [
        {
            "name": "Dr. Nikhil Joshi",
            "specialization": "ENT Specialist",
            "experience": "7 years",
            "fees": "₹550",
            "slot": "6:00 PM - 7:00 PM",
            "hospital": "ENT Care Clinic",
            "location": "Nagpur"
        }
    ]
}


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn, table_name, column_name, column_type):
    cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    names = [c[1] for c in cols]
    if column_name not in names:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ngo_requests (
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            medicine_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            total_days INTEGER NOT NULL,
            note TEXT,
            last_alert_date TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            doctor_type TEXT,
            doctor_name TEXT,
            specialization TEXT,
            experience TEXT,
            fees TEXT,
            slot TEXT,
            hospital_name TEXT,
            location TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    ensure_column(conn, "appointments", "age", "TEXT")
    ensure_column(conn, "appointments", "permanent_disease", "TEXT")
    ensure_column(conn, "appointments", "previous_medical_history", "TEXT")
    ensure_column(conn, "appointments", "previous_visit_date", "TEXT")
    ensure_column(conn, "appointments", "previous_visit_reason", "TEXT")

    conn.commit()
    conn.close()


init_db()


def get_language():
    return session.get("lang", "en")


def get_language_data():
    return translations["en"]


def is_user_valid():
    data = session.get("verification_data")
    if not data:
        return False
    return data.get("name_valid") and data.get("age_valid") and data.get("location_valid")


def get_alert_message(lang_code):
    return "It is time to take your tablet."


def get_reminder_status(item):
    today = date.today()
    start_dt = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
    end_dt = start_dt + timedelta(days=item["total_days"] - 1)

    if today > end_dt:
        return "completed", 0
    if today < start_dt:
        return "active", item["total_days"]
    return "active", (end_dt - today).days + 1


@app.route("/")
def home():
    return render_template("language.html", t=get_language_data(), current_lang=get_language())


@app.route("/set-language", methods=["POST"])
def set_language():
    session["lang"] = request.form.get("language", "en")
    return redirect(url_for("aadhaar_page"))


@app.route("/aadhaar")
def aadhaar_page():
    return render_template("aadhaar.html", t=get_language_data(), current_lang=get_language())


@app.route("/verify-aadhaar", methods=["POST"])
def verify_aadhaar():
    uploaded_file = request.files.get("aadhaar_file")
    filename = ""

    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        session["uploaded_filename"] = filename
    else:
        session["uploaded_filename"] = "No file selected"

    lower_filename = filename.lower()

    if "om" in lower_filename:
        mock_user = {"name": "Om Pawar", "age": 52, "location": "Nagpur"}
    elif "ashok" in lower_filename:
        mock_user = {"name": "Ashok Patil", "age": 58, "location": "Pune"}
    elif "invalid" in lower_filename:
        mock_user = {"name": "Rohan Sharma", "age": 45, "location": "Nashik"}
    else:
        mock_user = {"name": "Demo User", "age": 58, "location": "Nagpur"}

    session["verification_data"] = {
        "name": mock_user["name"],
        "age": mock_user["age"],
        "location": mock_user["location"],
        "name_valid": bool(mock_user["name"]),
        "age_valid": mock_user["age"] >= 50,
        "location_valid": bool(mock_user["location"])
    }

    return redirect(url_for("verification_page"))


@app.route("/verification")
def verification_page():
    verification_data = session.get("verification_data")
    if not verification_data:
        return redirect(url_for("aadhaar_page"))

    return render_template(
        "verification.html",
        t=get_language_data(),
        current_lang=get_language(),
        uploaded_filename=session.get("uploaded_filename", "No file selected"),
        verification_data=verification_data,
        all_valid=is_user_valid()
    )


@app.route("/proceed")
def proceed():
    if not is_user_valid():
        return redirect(url_for("verification_page"))
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    return render_template(
        "dashboard.html",
        t=get_language_data(),
        current_lang=get_language(),
        user_name=session["verification_data"]["name"]
    )


@app.route("/ngo-voice")
def ngo_voice():
    if not is_user_valid():
        return redirect(url_for("verification_page"))
    return render_template("ngo_voice.html", t=get_language_data(), current_lang=get_language())


@app.route("/save-ngo-voice", methods=["POST"])
def save_ngo_voice():
    if not is_user_valid():
        return jsonify({"status": "error"}), 403

    data = request.get_json() or {}

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO ngo_requests (
            user_name, hospital_name, hospital_address,
            appointment_reason, appointment_date, appointment_time, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session["verification_data"]["name"],
        data.get("hospital", "Voice Input"),
        "Voice Input",
        data.get("reason", "Voice Input"),
        data.get("datetime", "Voice Input"),
        data.get("datetime", "Voice Input"),
        "Pending"
    ))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


@app.route("/ngo-status")
def ngo_status_page():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    conn = get_db_connection()
    requests_data = conn.execute("""
        SELECT * FROM ngo_requests
        WHERE user_name = ?
        ORDER BY id DESC
    """, (session["verification_data"]["name"],)).fetchall()
    conn.close()

    return render_template(
        "ngo_status.html",
        t=get_language_data(),
        current_lang=get_language(),
        requests_data=requests_data
    )


@app.route("/reminder")
def reminder_page():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    user_name = session["verification_data"]["name"]
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM reminders
        WHERE user_name = ?
        ORDER BY start_date ASC, reminder_time ASC
    """, (user_name,)).fetchall()
    conn.close()

    reminders = []
    due_reminder = None
    now_dt = datetime.now()
    today_dt = now_dt.date()
    current_time_only = now_dt.time()

    for item in rows:
        start_dt = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
        end_dt = start_dt + timedelta(days=item["total_days"] - 1)
        reminder_time_obj = datetime.strptime(item["reminder_time"], "%H:%M").time()
        last_alert_date = item["last_alert_date"]

        status_text, days_left = get_reminder_status(item)
        item_dict = dict(item)
        item_dict["status_text"] = status_text
        item_dict["days_left"] = days_left
        reminders.append(item_dict)

        if (
            due_reminder is None
            and start_dt <= today_dt <= end_dt
            and current_time_only >= reminder_time_obj
            and last_alert_date != today_dt.strftime("%Y-%m-%d")
        ):
            due_reminder = item

    return render_template(
        "reminder.html",
        t=get_language_data(),
        current_lang=get_language(),
        reminders=reminders,
        due_reminder=due_reminder,
        alert_message=get_alert_message(get_language())
    )


@app.route("/save-reminder", methods=["POST"])
def save_reminder():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO reminders (
            user_name, medicine_name, start_date, reminder_time, total_days, note, last_alert_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session["verification_data"]["name"],
        request.form.get("medicine_name", "").strip(),
        request.form.get("start_date", "").strip(),
        request.form.get("reminder_time", "").strip(),
        int(request.form.get("total_days", "1").strip()),
        request.form.get("note", "").strip(),
        None
    ))
    conn.commit()
    conn.close()

    return redirect(url_for("reminder_page"))


@app.route("/mark-reminder-alerted/<int:reminder_id>", methods=["POST"])
def mark_reminder_alerted(reminder_id):
    if not is_user_valid():
        return jsonify({"success": False}), 403

    conn = get_db_connection()
    conn.execute("""
        UPDATE reminders
        SET last_alert_date = ?
        WHERE id = ? AND user_name = ?
    """, (
        date.today().strftime("%Y-%m-%d"),
        reminder_id,
        session["verification_data"]["name"]
    ))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.route("/check-due-reminder")
def check_due_reminder():
    if not is_user_valid():
        return jsonify({"due": False}), 403

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM reminders
        WHERE user_name = ?
        ORDER BY start_date ASC, reminder_time ASC
    """, (session["verification_data"]["name"],)).fetchall()
    conn.close()

    now_dt = datetime.now()
    today_dt = now_dt.date()
    current_time_only = now_dt.time()

    for item in rows:
        start_dt = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
        end_dt = start_dt + timedelta(days=item["total_days"] - 1)
        reminder_time_obj = datetime.strptime(item["reminder_time"], "%H:%M").time()
        last_alert_date = item["last_alert_date"]

        if (
            start_dt <= today_dt <= end_dt
            and current_time_only >= reminder_time_obj
            and last_alert_date != today_dt.strftime("%Y-%m-%d")
        ):
            return jsonify({
                "due": True,
                "id": item["id"],
                "medicine_name": item["medicine_name"],
                "message": get_alert_message(get_language()),
                "lang": get_language()
            })

    return jsonify({"due": False})


@app.route("/appointment")
def appointment_page():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    user_name = session["verification_data"]["name"]
    conn = get_db_connection()
    last_record = conn.execute("""
        SELECT * FROM appointments
        WHERE user_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_name,)).fetchone()
    conn.close()

    first_time = last_record is None
    saved_disease = ""
    if last_record and last_record["permanent_disease"]:
        saved_disease = last_record["permanent_disease"]

    return render_template(
        "appointment.html",
        t=get_language_data(),
        current_lang=get_language(),
        first_time=first_time,
        saved_disease=saved_disease
    )


@app.route("/show-doctors", methods=["POST"])
def show_doctors():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    doctor_type = request.form.get("doctor_type", "").strip()
    permanent_disease = request.form.get("permanent_disease", "").strip()

    if not permanent_disease:
        user_name = session["verification_data"]["name"]
        conn = get_db_connection()
        last_record = conn.execute("""
            SELECT * FROM appointments
            WHERE user_name = ?
            ORDER BY id DESC
            LIMIT 1
        """, (user_name,)).fetchone()
        conn.close()
        if last_record and last_record["permanent_disease"]:
            permanent_disease = last_record["permanent_disease"]

    session["appointment_doctor_type"] = doctor_type
    session["appointment_permanent_disease"] = permanent_disease

    return redirect(url_for("show_doctors_page"))


@app.route("/show-doctors-page")
def show_doctors_page():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    doctor_type = session.get("appointment_doctor_type", "")
    permanent_disease = session.get("appointment_permanent_disease", "")

    if not doctor_type:
        return redirect(url_for("appointment_page"))

    doctors = DOCTOR_DATA.get(doctor_type, [])

    return render_template(
        "appointment_doctors.html",
        t=get_language_data(),
        current_lang=get_language(),
        doctor_type=doctor_type,
        permanent_disease=permanent_disease,
        doctors=doctors
    )


@app.route("/select-doctor", methods=["POST"])
def select_doctor():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    user_name = session["verification_data"]["name"]
    age = str(session["verification_data"]["age"])
    permanent_disease = request.form.get("permanent_disease", "").strip()

    conn = get_db_connection()

    if not permanent_disease:
        last_pd = conn.execute("""
            SELECT permanent_disease FROM appointments
            WHERE user_name = ?
            ORDER BY id DESC
            LIMIT 1
        """, (user_name,)).fetchone()
        if last_pd and last_pd["permanent_disease"]:
            permanent_disease = last_pd["permanent_disease"]

    last_record = conn.execute("""
        SELECT * FROM appointments
        WHERE user_name = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_name,)).fetchone()

    if last_record:
        previous_medical_history = last_record["doctor_type"] or "No previous record"
        previous_visit_date = last_record["slot"] or "No previous record"
        previous_visit_reason = last_record["specialization"] or "No previous record"
    else:
        previous_medical_history = "No previous record"
        previous_visit_date = "No previous record"
        previous_visit_reason = "No previous record"

    conn.execute("""
        INSERT INTO appointments (
            user_name, age, permanent_disease, doctor_type, doctor_name, specialization,
            experience, fees, slot, hospital_name, location, status,
            previous_medical_history, previous_visit_date, previous_visit_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_name,
        age,
        permanent_disease,
        request.form.get("doctor_type", "").strip(),
        request.form.get("doctor_name", "").strip(),
        request.form.get("specialization", "").strip(),
        request.form.get("experience", "").strip(),
        request.form.get("fees", "").strip(),
        request.form.get("slot", "").strip(),
        request.form.get("hospital_name", "").strip(),
        request.form.get("location", "").strip(),
        "Pending",
        previous_medical_history,
        previous_visit_date,
        previous_visit_reason
    ))
    conn.commit()
    conn.close()

    return redirect(url_for("appointment_status_page"))


@app.route("/appointment-status")
def appointment_status_page():
    if not is_user_valid():
        return redirect(url_for("verification_page"))

    conn = get_db_connection()
    appointments = conn.execute("""
        SELECT * FROM appointments
        WHERE user_name = ?
        ORDER BY id DESC
    """, (session["verification_data"]["name"],)).fetchall()
    conn.close()

    return render_template(
        "appointment_status.html",
        t=get_language_data(),
        current_lang=get_language(),
        appointments=appointments
    )


@app.route("/sos")
def sos_page():
    if not is_user_valid():
        return redirect(url_for("verification_page"))
    return render_template("sos.html", t=get_language_data(), current_lang=get_language())


if __name__ == "__main__":
    app.run(debug=True)