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


# ==============================
# LANGUAGE DATA
# ==============================

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
    },

    "hi": {
        "app_name": "आश्रय",
        "subtitle": "50+ नागरिकों के लिए स्वास्थ्य सहायता",
        "select_language": "भाषा चुनें",
        "choose_language": "जारी रखने के लिए अपनी भाषा चुनें",
        "continue": "आगे बढ़ें",
        "upload_aadhaar": "आधार कार्ड अपलोड करें",
        "upload_text": "आयु सत्यापन के लिए कृपया अपना आधार कार्ड अपलोड करें",
        "selected_file": "चयनित फ़ाइल",
        "verify_now": "अभी सत्यापित करें",
        "verification_result": "सत्यापन परिणाम",
        "autofilled_details": "ऑटोफिल विवरण",
        "name": "नाम",
        "age": "आयु",
        "location": "स्थान",
        "verified": "सत्यापित",
        "eligible": "पात्र",
        "invalid": "अमान्य",
        "invalid_age": "अमान्य आयु। केवल 50+ उपयोगकर्ता आगे बढ़ सकते हैं।",
        "cannot_proceed": "आगे नहीं बढ़ सकते",
        "valid_age": "आयु सफलतापूर्वक सत्यापित हुई। आप आगे बढ़ सकते हैं।",
        "proceed": "आगे बढ़ें",
        "ngo": "एनजीओ",
        "reminder": "मेडिकल रिमाइंडर",
        "sos": "एसओएस",
        "appointment": "अपॉइंटमेंट",
        "go_back": "वापस जाएँ",
        "dashboard_title": "मुख्य डैशबोर्ड",
        "dashboard_text": "आगे बढ़ने के लिए एक विकल्प चुनें।",
        "welcome_user": "स्वागत है",
        "ngo_text": "एनजीओ सहायता के लिए अनुरोध करें और स्थिति देखें।",
        "reminder_text": "दवा और टैबलेट रिमाइंडर सेट करें।",
        "sos_text": "आपातकालीन स्थिति में एसओएस सहायता का उपयोग करें।",
        "appointment_text": "मेडिकल अपॉइंटमेंट और अस्पताल विज़िट बुक करें।",
        "back_dashboard": "डैशबोर्ड पर वापस जाएँ",
        "hospital_name": "अस्पताल का नाम",
        "hospital_address": "अस्पताल का पता",
        "appointment_reason": "अपॉइंटमेंट का कारण",
        "appointment_date": "अपॉइंटमेंट की तारीख",
        "appointment_time": "अपॉइंटमेंट का समय",
        "submit_request": "अनुरोध सबमिट करें",
        "ngo_status": "एनजीओ अनुरोध स्थिति",
        "status": "स्थिति",
        "pending": "लंबित",
        "approved": "स्वीकृत",
        "rejected": "अस्वीकृत",
        "no_requests": "कोई अनुरोध नहीं मिला।",
        "view_status": "स्थिति देखें",
        "reminder_form_title": "दवा रिमाइंडर सेट करें",
        "medicine_name": "दवा का नाम",
        "start_date": "शुरू होने की तारीख",
        "time": "समय",
        "total_days": "कुल दिन",
        "note": "वैकल्पिक नोट",
        "save_reminder": "रिमाइंडर सेव करें",
        "my_reminders": "मेरे रिमाइंडर",
        "no_reminders": "कोई रिमाइंडर नहीं मिला।",
        "call_from": "आश्रय रिमाइंडर",
        "incoming_call": "इनकमिंग रिमाइंडर कॉल",
        "receive": "रिसीव",
        "dismiss": "बंद करें",
        "tablet_message": "दवा लेने का समय हो गया है।",
        "days_left": "बचे हुए दिन",
        "completed": "पूरा हुआ",
        "active": "सक्रिय",
        "doctor_type": "डॉक्टर का प्रकार",
        "choose_doctor_type": "डॉक्टर का प्रकार चुनें",
        "general_physician": "जनरल फिजिशियन",
        "cardiology": "कार्डियोलॉजी",
        "orthopedic": "ऑर्थोपेडिक",
        "neurology": "न्यूरोलॉजी",
        "eye_specialist": "आंख विशेषज्ञ",
        "ent": "ईएनटी",
        "show_doctors": "डॉक्टर दिखाएँ",
        "available_doctors": "उपलब्ध डॉक्टर",
        "specialization": "विशेषज्ञता",
        "experience": "अनुभव",
        "fees": "कंसल्टिंग फीस",
        "available_slot": "उपलब्ध स्लॉट",
        "current_location": "वर्तमान स्थान",
        "select_doctor": "डॉक्टर चुनें",
        "my_appointments": "मेरे अपॉइंटमेंट",
        "doctor_name": "डॉक्टर का नाम",
        "selected_doctor_type": "चुना गया डॉक्टर प्रकार",
        "no_doctors_found": "इस श्रेणी के लिए कोई डॉक्टर नहीं मिला।",
        "permanent_disease": "स्थायी बीमारी",
        "no_previous_record": "कोई पिछला रिकॉर्ड नहीं",
        "first_time_appointment": "पहली बार अपॉइंटमेंट",
        "repeat_appointment": "दोबारा अपॉइंटमेंट",
        "tell_permanent_disease": "अपनी स्थायी बीमारी बताएं",
        "doctor_needed": "आपको किस प्रकार के डॉक्टर चाहिए?"
    },

    "mr": {
        "app_name": "आश्रय",
        "subtitle": "50+ नागरिकांसाठी आरोग्य सहाय्य",
        "select_language": "भाषा निवडा",
        "choose_language": "पुढे जाण्यासाठी आपली भाषा निवडा",
        "continue": "पुढे जा",
        "upload_aadhaar": "आधार कार्ड अपलोड करा",
        "upload_text": "वय पडताळणीसाठी कृपया आपले आधार कार्ड अपलोड करा",
        "selected_file": "निवडलेली फाइल",
        "verify_now": "आता पडताळणी करा",
        "verification_result": "पडताळणी निकाल",
        "autofilled_details": "ऑटोफिल तपशील",
        "name": "नाव",
        "age": "वय",
        "location": "स्थान",
        "verified": "पडताळले",
        "eligible": "पात्र",
        "invalid": "अवैध",
        "invalid_age": "अवैध वय. फक्त 50+ वापरकर्ते पुढे जाऊ शकतात.",
        "cannot_proceed": "पुढे जाता येणार नाही",
        "valid_age": "वय यशस्वीरित्या पडताळले गेले. आपण पुढे जाऊ शकता.",
        "proceed": "पुढे जा",
        "ngo": "एनजीओ",
        "reminder": "मेडिकल रिमाइंडर",
        "sos": "एसओएस",
        "appointment": "अपॉइंटमेंट",
        "go_back": "मागे जा",
        "dashboard_title": "मुख्य डॅशबोर्ड",
        "dashboard_text": "पुढे जाण्यासाठी एक पर्याय निवडा.",
        "welcome_user": "स्वागत",
        "ngo_text": "एनजीओ मदतीसाठी विनंती करा आणि स्थिती पहा.",
        "reminder_text": "औषध आणि टॅबलेट रिमाइंडर सेट करा.",
        "sos_text": "आपत्कालीन परिस्थितीत एसओएस वापरा.",
        "appointment_text": "मेडिकल अपॉइंटमेंट आणि हॉस्पिटल भेट बुक करा.",
        "back_dashboard": "डॅशबोर्डवर परत जा",
        "hospital_name": "हॉस्पिटलचे नाव",
        "hospital_address": "हॉस्पिटलचा पत्ता",
        "appointment_reason": "अपॉइंटमेंटचे कारण",
        "appointment_date": "अपॉइंटमेंट तारीख",
        "appointment_time": "अपॉइंटमेंट वेळ",
        "submit_request": "विनंती सबमिट करा",
        "ngo_status": "एनजीओ विनंती स्थिती",
        "status": "स्थिती",
        "pending": "प्रलंबित",
        "approved": "मंजूर",
        "rejected": "नाकारले",
        "no_requests": "कोणतीही विनंती आढळली नाही.",
        "view_status": "स्थिती पहा",
        "reminder_form_title": "औषध रिमाइंडर सेट करा",
        "medicine_name": "औषधाचे नाव",
        "start_date": "सुरुवातीची तारीख",
        "time": "वेळ",
        "total_days": "एकूण दिवस",
        "note": "पर्यायी नोट",
        "save_reminder": "रिमाइंडर सेव्ह करा",
        "my_reminders": "माझे रिमाइंडर",
        "no_reminders": "कोणतेही रिमाइंडर आढळले नाहीत.",
        "call_from": "आश्रय रिमाइंडर",
        "incoming_call": "इनकमिंग रिमाइंडर कॉल",
        "receive": "उचला",
        "dismiss": "बंद करा",
        "tablet_message": "गोळी घेण्याची वेळ झाली आहे.",
        "days_left": "उरलेले दिवस",
        "completed": "पूर्ण",
        "active": "सक्रिय",
        "doctor_type": "डॉक्टर प्रकार",
        "choose_doctor_type": "डॉक्टर प्रकार निवडा",
        "general_physician": "जनरल फिजिशियन",
        "cardiology": "कार्डिओलॉजी",
        "orthopedic": "ऑर्थोपेडिक",
        "neurology": "न्युरॉलॉजी",
        "eye_specialist": "डोळ्यांचे तज्ञ",
        "ent": "ईएनटी",
        "show_doctors": "डॉक्टर दाखवा",
        "available_doctors": "उपलब्ध डॉक्टर",
        "specialization": "विशेषज्ञता",
        "experience": "अनुभव",
        "fees": "कन्सल्टिंग फी",
        "available_slot": "उपलब्ध स्लॉट",
        "current_location": "सध्याचे स्थान",
        "select_doctor": "डॉक्टर निवडा",
        "my_appointments": "माझे अपॉइंटमेंट",
        "doctor_name": "डॉक्टरचे नाव",
        "selected_doctor_type": "निवडलेला डॉक्टर प्रकार",
        "no_doctors_found": "या प्रकारासाठी डॉक्टर सापडला नाही.",
        "permanent_disease": "कायमस्वरूपी आजार",
        "no_previous_record": "मागील नोंद नाही",
        "first_time_appointment": "पहिली अपॉइंटमेंट",
        "repeat_appointment": "पुन्हा अपॉइंटमेंट",
        "tell_permanent_disease": "तुमचा कायमस्वरूपी आजार सांगा",
        "doctor_needed": "तुम्हाला कोणत्या प्रकारचा डॉक्टर हवा आहे?"
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


# ==============================
# DB HELPERS
# ==============================

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
            family_name TEXT,
            family_phone TEXT,
            last_alert_date TEXT,
            family_last_alert_date TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            age TEXT,
            permanent_disease TEXT,
            doctor_type TEXT,
            doctor_name TEXT,
            specialization TEXT,
            experience TEXT,
            fees TEXT,
            slot TEXT,
            hospital_name TEXT,
            location TEXT,
            status TEXT DEFAULT 'Pending',
            previous_medical_history TEXT,
            previous_visit_date TEXT,
            previous_visit_reason TEXT
        )
    """)

    ensure_column(conn, "appointments", "age", "TEXT")
    ensure_column(conn, "appointments", "permanent_disease", "TEXT")
    ensure_column(conn, "appointments", "previous_medical_history", "TEXT")
    ensure_column(conn, "appointments", "previous_visit_date", "TEXT")
    ensure_column(conn, "appointments", "previous_visit_reason", "TEXT")

    ensure_column(conn, "reminders", "family_name", "TEXT")
    ensure_column(conn, "reminders", "family_phone", "TEXT")
    ensure_column(conn, "reminders", "family_last_alert_date", "TEXT")

    conn.commit()
    conn.close()


init_db()


# ==============================
# COMMON HELPERS
# ==============================

def get_language():
    return session.get("lang", "en")


def get_language_data():
    return translations.get(get_language(), translations["en"])


def is_user_valid():
    data = session.get("verification_data")
    if not data:
        return False
    return data.get("name_valid") and data.get("age_valid") and data.get("location_valid")


def get_alert_message(lang_code):
    if lang_code == "hi":
        return "दवा लेने का समय हो गया है।"
    if lang_code == "mr":
        return "गोळी घेण्याची वेळ झाली आहे."
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


# ==============================
# USER FLOW
# ==============================

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


# ==============================
# NGO USER VOICE FLOW
# ==============================

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

    hospital = (data.get("hospital") or "Voice Input").strip()
    reason = (data.get("reason") or "Voice Input").strip()
    date_time = (data.get("datetime") or "Voice Input").strip()

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO ngo_requests (
            user_name, hospital_name, hospital_address,
            appointment_reason, appointment_date, appointment_time, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session["verification_data"]["name"],
        hospital,
        "Voice Input",
        reason,
        date_time,
        date_time,
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


# ==============================
# REMINDER FLOW
# ==============================

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
            due_reminder = item_dict

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
            user_name, medicine_name, start_date, reminder_time, total_days,
            note, family_name, family_phone, last_alert_date, family_last_alert_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["verification_data"]["name"],
        request.form.get("medicine_name", "").strip(),
        request.form.get("start_date", "").strip(),
        request.form.get("reminder_time", "").strip(),
        int(request.form.get("total_days", "1").strip()),
        request.form.get("note", "").strip(),
        request.form.get("family_name", "").strip(),
        request.form.get("family_phone", "").strip(),
        None,
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
        SET last_alert_date = ?, family_last_alert_date = ?
        WHERE id = ? AND user_name = ?
    """, (
        date.today().strftime("%Y-%m-%d"),
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
                "lang": get_language(),
                "family_name": item["family_name"] if item["family_name"] else "",
                "family_phone": item["family_phone"] if item["family_phone"] else ""
            })

    return jsonify({"due": False})


# ==============================
# SOS
# ==============================

@app.route("/sos")
def sos_page():
    if not is_user_valid():
        return redirect(url_for("verification_page"))
    return render_template("sos.html", t=get_language_data(), current_lang=get_language())


# ==============================
# APPOINTMENT FLOW
# ==============================

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


# ==============================
# DOCTOR PANEL
# username: doctor
# password: 123
# ==============================

@app.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == "doctor" and password == "123":
            session["doctor_logged_in"] = True
            return redirect(url_for("doctor_dashboard"))

    return render_template("doctor_login.html")


@app.route("/doctor-dashboard")
def doctor_dashboard():
    if not session.get("doctor_logged_in"):
        return redirect(url_for("doctor_login"))

    conn = get_db_connection()
    appointments = conn.execute("""
        SELECT * FROM appointments
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    return render_template("doctor_dashboard.html", appointments=appointments)


@app.route("/approve-appointment/<int:appointment_id>", methods=["GET", "POST"])
def approve_appointment(appointment_id):
    if not session.get("doctor_logged_in"):
        return redirect(url_for("doctor_login"))

    conn = get_db_connection()
    conn.execute("UPDATE appointments SET status='Approved' WHERE id=?", (appointment_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("doctor_dashboard"))


@app.route("/reject-appointment/<int:appointment_id>", methods=["GET", "POST"])
def reject_appointment(appointment_id):
    if not session.get("doctor_logged_in"):
        return redirect(url_for("doctor_login"))

    conn = get_db_connection()
    conn.execute("UPDATE appointments SET status='Rejected' WHERE id=?", (appointment_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("doctor_dashboard"))


@app.route("/doctor-logout")
def doctor_logout():
    session.pop("doctor_logged_in", None)
    return redirect(url_for("doctor_login"))


# ==============================
# NGO PANEL
# username: ngo
# password: 123
# ==============================

@app.route("/ngo-login", methods=["GET", "POST"])
def ngo_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == "ngo" and password == "123":
            session["ngo_logged_in"] = True
            return redirect(url_for("ngo_dashboard"))

    return render_template("ngo_login.html")


@app.route("/ngo-dashboard")
def ngo_dashboard():
    if not session.get("ngo_logged_in"):
        return redirect(url_for("ngo_login"))

    conn = get_db_connection()
    requests_data = conn.execute("""
        SELECT * FROM ngo_requests
        ORDER BY id DESC
    """).fetchall()

    total_requests = len(requests_data)
    pending_count = sum(1 for r in requests_data if r["status"] == "Pending")
    approved_count = sum(1 for r in requests_data if r["status"] == "Approved")
    rejected_count = sum(1 for r in requests_data if r["status"] == "Rejected")
    conn.close()

    return render_template(
        "ngo_dashboard.html",
        requests_data=requests_data,
        total_requests=total_requests,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count
    )


@app.route("/approve-ngo/<int:request_id>", methods=["GET", "POST"])
def approve_ngo(request_id):
    if not session.get("ngo_logged_in"):
        return redirect(url_for("ngo_login"))

    conn = get_db_connection()
    conn.execute("UPDATE ngo_requests SET status='Approved' WHERE id=?", (request_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("ngo_dashboard"))


@app.route("/reject-ngo/<int:request_id>", methods=["GET", "POST"])
def reject_ngo(request_id):
    if not session.get("ngo_logged_in"):
        return redirect(url_for("ngo_login"))

    conn = get_db_connection()
    conn.execute("UPDATE ngo_requests SET status='Rejected' WHERE id=?", (request_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("ngo_dashboard"))


@app.route("/ngo-logout")
def ngo_logout():
    session.pop("ngo_logged_in", None)
    return redirect(url_for("ngo_login"))


if __name__ == "__main__":
    app.run(debug=True)