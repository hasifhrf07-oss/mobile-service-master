# Mobile Service Master - Full Web App v3.1 (Admin + Encryption + Meter + Comment + Subscription)

from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for)
from functools import wraps
from cryptography.fernet import Fernet
import os
import sys
import json
import hashlib
import secrets
import threading
import time
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Existing imports (core modules) ──
from core.adb_manager import ADBManager
from core.detector import Detector
from core.multi_detect import MultiDetector
from core.analyzer import Analyzer
from core.clone_checker import CloneChecker
from core.usb_reader import USBReader
from core.scanner.board_scanner import BoardScanner

# ── New imports (meter engine, comment engine, subscription) ──
from core.meter_engine import analyze_meter_photos
from core.comment_engine import (classify_comment, generate_reply,
                                  log_comment, needs_admin_review)

# Subscription module (created earlier via PART 2C — if missing, fallback)
try:
    from core.subscription import register_trial, check_status as check_sub
    HAS_SUB = True
except ImportError:
    HAS_SUB = False
    def check_sub(email):
        return {"status": "unknown", "days_left": -1, "show_warning": False}

# DB
from data import db


app = Flask(__name__)

# ============================================================
# Security — Session + Encryption
# ============================================================

SECRET_FILE = os.path.join(os.path.dirname(__file__), ".secret_key")

if os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, "rb") as f:
        app.secret_key = f.read()
else:
    key = secrets.token_bytes(32)
    with open(SECRET_FILE, "wb") as f:
        f.write(key)
    app.secret_key = key

ENC_KEY_FILE = os.path.join(os.path.dirname(__file__), ".encryption_key")

if os.path.exists(ENC_KEY_FILE):
    with open(ENC_KEY_FILE, "rb") as f:
        ENC_KEY = f.read()
else:
    ENC_KEY = Fernet.generate_key()
    with open(ENC_KEY_FILE, "wb") as f:
        f.write(ENC_KEY)

cipher = Fernet(ENC_KEY)

# ── Uploads config ──
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "bmp"}


def _allowed(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ============================================================
# User Database
# ============================================================

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# ADMIN EMAIL — can be overridden by env var (for Render deployment)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin.mobile.servicemaster@gmail.com")


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


def is_admin(email):
    return email and email.lower() == ADMIN_EMAIL.lower()


# ============================================================
# Decorators
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        if not is_admin(session.get("email")):
            return jsonify({"ok": False, "message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


# ============================================================
# Auth Routes
# ============================================================

@app.route("/")
def index():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")

    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"ok": False, "message": "Email ও Password দিন"})

    users = load_users()

    # New user - auto register + OTP
    if email not in users:
        otp = generate_otp()
        users[email] = {
            "email": email,
            "password_hash": hash_password(password),
            "verified": False,
            "otp": otp,
            "otp_created": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "scans_count": 0,
            "ip_address": request.remote_addr or "unknown",
        }
        save_users(users)

        session["pending_email"] = email

        print()
        print("=" * 60)
        print(f"  OTP for {email}: {otp}")
        print("=" * 60)
        print()

        return jsonify({
            "ok": True,
            "action": "verify",
            "message": "New account - OTP terminal-e print hoyeche",
            "dev_otp": otp,
        })

    user = users[email]

    if user["password_hash"] != hash_password(password):
        return jsonify({"ok": False, "message": "Password vul"})

    if user.get("verified"):
        session["logged_in"] = True
        session["email"] = email
        session["login_time"] = datetime.now().isoformat()

        user["last_login"] = datetime.now().isoformat()
        user["last_ip"] = request.remote_addr or "unknown"
        save_users(users)

        return jsonify({"ok": True, "action": "dashboard"})

    otp = generate_otp()
    user["otp"] = otp
    user["otp_created"] = datetime.now().isoformat()
    save_users(users)

    session["pending_email"] = email

    print()
    print("=" * 60)
    print(f"  New OTP for {email}: {otp}")
    print("=" * 60)
    print()

    return jsonify({
        "ok": True,
        "action": "verify",
        "message": "OTP terminal-e print hoyeche",
        "dev_otp": otp,
    })


@app.route("/verify", methods=["GET", "POST"])
def verify_page():
    if request.method == "GET":
        email = session.get("pending_email")
        if not email:
            return redirect(url_for("login_page"))
        return render_template("verify.html", email=email)

    data = request.json or {}
    otp = (data.get("otp") or "").strip()

    email = session.get("pending_email")
    if not email:
        return jsonify({"ok": False, "message": "Session expired"})

    users = load_users()
    if email not in users:
        return jsonify({"ok": False, "message": "User paowa jayni"})

    user = users[email]

    if user.get("otp") != otp:
        return jsonify({"ok": False, "message": "Verification code vul"})

    user["verified"] = True
    user["otp"] = None
    user["verified_at"] = datetime.now().isoformat()
    user["last_login"] = datetime.now().isoformat()
    save_users(users)

    session["logged_in"] = True
    session["email"] = email
    session["login_time"] = datetime.now().isoformat()
    session.pop("pending_email", None)

    return jsonify({"ok": True, "action": "dashboard"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ============================================================
# Dashboard
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():
    email = session.get("email", "")
    users = load_users()
    user = users.get(email, {})

    # Subscription warning
    sub = {}
    if HAS_SUB:
        try:
            sub = check_sub(email)
        except Exception:
            sub = {}

    return render_template(
        "dashboard.html",
        email=email,
        login_time=session.get("login_time", ""),
        scans_count=user.get("scans_count", 0),
        is_admin=is_admin(email),
        subscription=sub,
    )


# ============================================================
# API - Connect
# ============================================================

@app.route("/api/connect", methods=["POST"])
@login_required
def api_connect():
    try:
        adb = ADBManager()
        result = adb.check_connection()
        state = result.get("state", "unknown")

        if state == "device":
            detector = Detector()
            if detector.detect_adb():
                info = detector.info
                adb.mark_authorized(info.serial, info.brand, info.model)

                return jsonify({
                    "ok": True,
                    "state": "connected",
                    "device": {
                        "brand": info.brand or "Unknown",
                        "model": info.model or "Unknown",
                        "chipset": info.chipset or "Unknown",
                        "android": info.android or "Unknown",
                        "serial": info.serial or "Unknown",
                        "codename": info.codename or "",
                    },
                })

        elif state == "unauthorized":
            return jsonify({
                "ok": False,
                "state": "unauthorized",
                "message": "Phone-e 'Allow USB debugging' popup-e Allow chapa",
            })

        elif state == "no_device":
            multi = MultiDetector()
            mres = multi.auto_detect_all()
            if mres["mode"] != "none":
                return jsonify({
                    "ok": False,
                    "state": mres["mode"],
                    "message": mres["message"],
                })
            return jsonify({
                "ok": False,
                "state": "no_device",
                "message": "USB cable connect koro",
            })

        return jsonify({"ok": False, "state": state})

    except Exception as e:
        return jsonify({"ok": False, "state": "error", "message": str(e)})


# ============================================================
# API - Full Diagnose
# ============================================================

@app.route("/api/full-diagnose", methods=["POST"])
@login_required
def api_full_diagnose():
    try:
        detector = Detector()
        if not detector.detect_adb():
            return jsonify({"ok": False, "message": "Device detect hoyni"})

        info = detector.info

        device_result = {
            "brand": info.brand or "Unknown",
            "model": info.model or "Unknown",
            "codename": info.codename or "Unknown",
            "chipset": info.chipset or "Unknown",
            "android": info.android or "Unknown",
            "serial": info.serial or "Unknown",
        }

        battery = detector.get_battery_level()

        battery_info = {}
        try:
            battery_info = USBReader().get_battery_info()
        except Exception:
            pass

        cpu_info = {}
        try:
            cpu_info = USBReader().get_cpu_info()
        except Exception:
            pass

        memory_info = {}
        try:
            memory_info = USBReader().get_memory_info()
        except Exception:
            pass

        storage_info = {}
        try:
            storage_info = USBReader().get_storage_info()
        except Exception:
            pass

        network_info = {}
        try:
            network_info = USBReader().get_network_info()
        except Exception:
            pass

        checker = CloneChecker()
        clone_reasons = checker.analyze(info)
        is_clone = checker.is_clone(clone_reasons)

        symptoms = {
            "boot": "ok", "display": "ok", "charging": "ok",
            "touch": "ok", "network": "ok", "speaker": "ok",
            "camera": "ok", "battery": "ok", "water": "no",
            "lock_screen": "none",
        }
        if 0 <= battery < 15:
            symptoms["battery"] = "drain"

        analyzer = Analyzer()
        diag = analyzer.analyze(info, symptoms)

        problems = []

        if battery >= 0:
            problems.append({
                "type": "battery",
                "label": "Battery Level",
                "value": f"{battery}%",
                "status": "ok" if battery >= 20 else "warning",
            })

        problems.append({
            "type": "clone",
            "label": "Clone Detection",
            "value": f"{len(clone_reasons)} flags" if clone_reasons else "Original",
            "status": "warning" if clone_reasons else "ok",
        })

        if cpu_info.get("cores"):
            problems.append({
                "type": "cpu",
                "label": "CPU Cores",
                "value": str(cpu_info.get("cores")),
                "status": "ok",
            })

        if memory_info.get("total_str"):
            problems.append({
                "type": "ram",
                "label": "RAM",
                "value": memory_info.get("total_str"),
                "status": "ok",
            })

        for key, val in (storage_info or {}).items():
            if val:
                problems.append({
                    "type": f"storage_{key}",
                    "label": f"Storage ({key.capitalize()})",
                    "value": f"{val.get('used', '?')} / {val.get('total', '?')}",
                    "status": "ok",
                })

        problems.append({
            "type": "overall",
            "label": "Overall",
            "value": diag.issue_type.value.upper(),
            "status": "ok" if diag.issue_type.value == "software" else "warning",
        })

        try:
            scanner = BoardScanner()
            scanner.capture_state(
                brand=info.brand,
                model=info.model,
                chipset=info.chipset,
                phone_serial=info.serial,
                readings={"battery": battery},
                diagnosis=diag.summary,
                technician=session.get("email", "unknown"),
                notes="Web app diagnostic - pending",
            )
        except Exception:
            pass

        email = session.get("email")
        if email:
            users = load_users()
            if email in users:
                users[email]["scans_count"] = users[email].get("scans_count", 0) + 1
                save_users(users)

        return jsonify({
            "ok": True,
            "device": device_result,
            "battery": {"level": battery, **battery_info},
            "cpu": cpu_info,
            "memory": memory_info,
            "storage": storage_info,
            "network": network_info,
            "clone": {"is_clone": is_clone, "reasons": clone_reasons},
            "diagnosis": {
                "issue_type": diag.issue_type.value,
                "summary": diag.summary,
                "evidence": diag.evidence,
                "sw_actions": diag.sw_actions,
                "hw_guide": diag.hw_guide,
            },
            "problems": problems,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


# ============================================================
# API - History (Full)
# ============================================================

@app.route("/api/history-full")
@login_required
def api_history_full():
    try:
        email = session.get("email", "")
        users = load_users()
        user_data = users.get(email, {})

        scanner = BoardScanner()
        scans = scanner.list_scans(limit=100)

        total = len(scans)
        fixed = 0
        not_fixed = 0
        pending = 0

        for s in scans:
            notes = (s.get("notes") or "").lower()
            if "success" in notes or "fixed" in notes:
                fixed += 1
            elif "fail" in notes or "not fixed" in notes:
                not_fixed += 1
            else:
                pending += 1

        all_users = []
        if is_admin(email):
            for u_email, u in users.items():
                all_users.append({
                    "email": u_email,
                    "verified": u.get("verified", False),
                    "scans_count": u.get("scans_count", 0),
                    "last_login": u.get("last_login", ""),
                    "created_at": u.get("created_at", ""),
                    "ip_address": u.get("ip_address", ""),
                    "last_ip": u.get("last_ip", ""),
                })
            all_users.sort(key=lambda x: x.get("scans_count", 0), reverse=True)

        return jsonify({
            "ok": True,
            "user": {
                "email": email,
                "scans_count": user_data.get("scans_count", 0),
                "created_at": user_data.get("created_at", ""),
                "last_login": user_data.get("last_login", ""),
                "is_admin": is_admin(email),
            },
            "scans": scans,
            "stats": {
                "total_scans": total,
                "fixed": fixed,
                "not_fixed": not_fixed,
                "pending": pending,
            },
            "all_users": all_users,
        })
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


# ============================================================
# API - Admin
# ============================================================

@app.route("/api/admin/users")
@admin_required
def api_admin_users():
    try:
        users = load_users()
        result = []
        for email, u in users.items():
            result.append({
                "email": email,
                "verified": u.get("verified", False),
                "scans_count": u.get("scans_count", 0),
                "created_at": u.get("created_at", ""),
                "last_login": u.get("last_login", ""),
                "ip_address": u.get("ip_address", ""),
                "last_ip": u.get("last_ip", ""),
                "is_admin": is_admin(email),
            })
        result.sort(key=lambda x: x.get("last_login", ""), reverse=True)
        return jsonify({"ok": True, "users": result})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


@app.route("/api/admin/delete-user", methods=["POST"])
@admin_required
def api_admin_delete_user():
    try:
        data = request.json or {}
        email = data.get("email", "").lower()

        if not email:
            return jsonify({"ok": False, "message": "Email dite hobe"})

        if email == ADMIN_EMAIL.lower():
            return jsonify({"ok": False, "message": "Admin nijeke delete korte pare na"})

        users = load_users()
        if email not in users:
            return jsonify({"ok": False, "message": "User paowa jayni"})

        del users[email]
        save_users(users)

        return jsonify({"ok": True, "message": f"{email} deleted"})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


# ============================================================
# API - Settings
# ============================================================

@app.route("/api/settings/info")
@login_required
def api_settings_info():
    try:
        total = db.total_count()
        clones = db.clone_count()
        ver = db.get_meta("db_version", "?")
        last = db.get_meta("last_update", "?")

        import platform
        import socket

        hostname = socket.gethostname()
        local_ip = "127.0.0.1"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            pass

        uptime_seconds = time.time() - START_TIME
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)

        return jsonify({
            "ok": True,
            "db": {
                "total_devices": total,
                "clones": clones,
                "version": ver,
                "last_update": last,
            },
            "system": {
                "platform": platform.system(),
                "python": platform.python_version(),
                "hostname": hostname,
                "local_ip": local_ip,
                "uptime": f"{hours}h {minutes}m",
                "uptime_seconds": int(uptime_seconds),
            },
            "user": {
                "email": session.get("email"),
                "is_admin": is_admin(session.get("email")),
            },
        })
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


@app.route("/api/settings/update-check")
@login_required
def api_update_check():
    try:
        from core.updater import check_and_update, get_update_url

        url = get_update_url()

        if not url:
            return jsonify({
                "ok": False,
                "message": "Update URL set kora nei",
                "has_url": False,
            })

        result = check_and_update(verbose=False)

        return jsonify({
            "ok": result.get("ok", False),
            "message": result.get("message", ""),
            "added": result.get("added", 0),
            "version": result.get("version", ""),
            "has_url": True,
        })
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


@app.route("/api/settings/set-update-url", methods=["POST"])
@admin_required
def api_set_update_url():
    try:
        data = request.json or {}
        url = (data.get("url") or "").strip()

        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return jsonify({"ok": False, "message": "Sothik URL dao"})

        from core.updater import set_update_url
        set_update_url(url)

        return jsonify({"ok": True, "message": "URL save hoyeche"})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


# ============================================================
# API - Model Search + Add (Dashboard Search Bar)
# ============================================================

@app.route("/api/search-model")
@login_required
def api_search_model():
    try:
        brand = (request.args.get("brand") or "").strip()
        model = (request.args.get("model") or "").strip()

        if not brand and not model:
            return jsonify({"ok": False, "message": "Brand ya Model likhun"})

        if brand and model:
            exact = db.find_device(brand, model)
            if exact:
                return jsonify({
                    "ok": True,
                    "found": True,
                    "model": exact,
                    "message": f"✅ {brand} {model} — database-e ache",
                })

        query = f"{brand} {model}".strip()
        results = db.search_devices(query, limit=20)

        if results:
            return jsonify({
                "ok": True,
                "found": True,
                "results": results,
                "message": f"✅ {len(results)} ta match paowa geche",
            })

        return jsonify({
            "ok": True,
            "found": False,
            "brand": brand,
            "model": model,
            "message": f"❌ {brand} {model} — database-e nei",
        })

    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


@app.route("/api/add-model", methods=["POST"])
@login_required
def api_add_model():
    try:
        data = request.json or {}
        brand = (data.get("brand") or "").strip()
        model = (data.get("model") or "").strip()

        if not brand or not model:
            return jsonify({"ok": False, "message": "Brand & Model dite hobe"})

        existing = db.find_device(brand, model)
        if existing:
            return jsonify({
                "ok": False,
                "message": f"⚠️ {brand} {model} already exists",
                "existing": existing,
            })

        ok = db.add_device(
            brand=brand,
            model=model,
            codename=(data.get("codename") or "").strip(),
            chipset=(data.get("chipset") or "").strip(),
            android_ver=(data.get("android") or "").strip(),
            release_year=int(data.get("year", 0) or 0),
            common_issues=data.get("issues", ["Unknown - user added"]),
            hw_guide_path=f"guides/{brand.lower()}/{model.lower()}.md",
        )

        if ok:
            total = db.total_count()
            return jsonify({
                "ok": True,
                "message": f"✅ {brand} {model} add hoyeche (Total: {total})",
                "total": total,
            })
        return jsonify({"ok": False, "message": "Add fail hoyeche"})

    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


@app.route("/api/db-stats")
@login_required
def api_db_stats():
    try:
        total = db.total_count()
        clones = db.clone_count()
        brands = db.list_brands()
        return jsonify({
            "ok": True,
            "total_models": total,
            "clones": clones,
            "brands": brands,
        })
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)})


# ============================================================
# Network Info + QR
# ============================================================

@app.route("/network-info")
def network_info():
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    return jsonify({
        "ok": True,
        "local_ip": local_ip,
        "url": f"http://{local_ip}:5000",
        "port": 5000,
    })


# ============================================================
# Health Check (legacy)
# ============================================================

@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    })


# ═════════════════════════════════════════════════════════
# NEW: METER PHOTO UPLOAD & ANALYSIS
# ═════════════════════════════════════════════════════════

@app.route("/api/upload-meter-photos", methods=["POST"])
@login_required
def api_upload_meter_photos():
    """৪টি ছবি আপলোড + analysis start"""
    job_id = str(uuid.uuid4())
    job_folder = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_folder, exist_ok=True)

    slots = ["analogue_meter", "multimeter", "dc_supply", "extra"]
    photo_paths = {}

    for slot in slots:
        file = request.files.get(slot)
        if file and file.filename and _allowed(file.filename):
            fname = f"{slot}_{secure_filename(file.filename)}"
            path = os.path.join(job_folder, fname)
            file.save(path)
            photo_paths[slot] = path

    if not photo_paths:
        return jsonify({"ok": False, "message": "কোনো বৈধ ছবি নেই"}), 400

    # Manual values (optional)
    manual_values = {}
    for slot in slots:
        mv = request.form.get(f"manual_{slot}")
        if mv:
            try:
                manual_values[slot] = float(mv)
            except ValueError:
                pass

    # Run analysis
    analysis = analyze_meter_photos(photo_paths, manual_values)
    analysis["job_id"] = job_id

    # Save to DB
    db.save_meter_job(
        job_id=job_id,
        user_email=session.get("email"),
        photos_json=json.dumps(photo_paths),
        brand=analysis.get("brand", ""),
    )
    db.update_meter_job(
        job_id=job_id,
        status="done",
        confidence=analysis.get("overall_confidence", 0),
        diagnosis_json=json.dumps(analysis.get("diagnosis", {})),
        result_json=json.dumps(analysis),
    )

    return jsonify({
        "ok": True,
        "job_id": job_id,
        "brand": analysis.get("brand"),
        "brand_confidence": analysis.get("brand_confidence"),
        "overall_confidence": analysis.get("overall_confidence"),
        "diagnosis": analysis.get("diagnosis"),
        "readings": analysis.get("readings"),
        "requires_remeasure": analysis.get("requires_remeasure"),
        "suggestions": analysis.get("suggestions"),
        "anomalies": analysis.get("anomalies"),
    })


@app.route("/api/meter-job/<job_id>")
@login_required
def api_meter_job(job_id):
    """Job result fetch"""
    job = db.get_meter_job(job_id)
    if not job:
        return jsonify({"ok": False, "message": "Job পাওয়া যায়নি"}), 404

    result = {}
    if job.get("result_json"):
        try:
            result = json.loads(job["result_json"])
        except Exception:
            result = {}

    return jsonify({
        "ok": True,
        "job": job,
        "result": result,
    })


@app.route("/api/meter-jobs")
@login_required
def api_meter_jobs():
    email = session.get("email")
    jobs = db.list_meter_jobs(user_email=email, limit=50)
    return jsonify({"ok": True, "jobs": jobs})


# ═════════════════════════════════════════════════════════
# NEW: COMMENTS
# ═════════════════════════════════════════════════════════

@app.route("/api/comment", methods=["POST"])
@login_required
def api_comment():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    job_id = (data.get("job_id") or "").strip()

    if not text:
        return jsonify({"ok": False, "message": "খালি কমেন্ট"}), 400

    classification = classify_comment(text)
    reply = generate_reply(classification)
    review = 1 if needs_admin_review(classification) else 0

    db.save_comment(
        user_email=session.get("email"),
        text=text,
        intent=",".join(classification["intents"]),
        auto_reply=reply,
        needs_review=review,
        job_id=job_id,
    )

    log_comment({
        "user": session.get("email"),
        "text": text,
        "intents": classification["intents"],
        "sentiment": classification["sentiment"],
        "brand": classification.get("brand"),
    })

    return jsonify({
        "ok": True,
        "reply": reply,
        "intents": classification["intents"],
        "sentiment": classification["sentiment"],
        "needs_review": bool(review),
    })


@app.route("/api/comments")
@login_required
def api_comments():
    return jsonify({
        "ok": True,
        "comments": db.list_comments(limit=100),
    })


# ═════════════════════════════════════════════════════════
# NEW: ADMIN — COMMENTS + METER JOBS
# ═════════════════════════════════════════════════════════

@app.route("/api/admin/comments")
@admin_required
def api_admin_comments():
    return jsonify({
        "ok": True,
        "all": db.list_comments(limit=200),
        "unmatched": db.list_unmatched_comments(limit=50),
    })


@app.route("/api/admin/meter-jobs")
@admin_required
def api_admin_meter_jobs():
    return jsonify({
        "ok": True,
        "jobs": db.list_meter_jobs(limit=200),
    })


# ═════════════════════════════════════════════════════════
# NEW: SUBSCRIPTION
# ═════════════════════════════════════════════════════════

@app.route("/api/subscription/status")
@login_required
def api_subscription_status():
    email = session.get("email")
    if not email:
        return jsonify({"ok": False}), 401
    status = check_sub(email)
    return jsonify({"ok": True, "subscription": status})


# ═════════════════════════════════════════════════════════
# NEW: HEALTH CHECK (for UptimeRobot)
# ═════════════════════════════════════════════════════════

@app.route("/healthz")
def healthz():
    return jsonify({
        "ok": True,
        "status": "running",
        "version": "3.1.0",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })


# ============================================================
# Background Task
# ============================================================

START_TIME = time.time()


def keep_alive_task():
    while True:
        time.sleep(3600)
        try:
            pass
        except Exception:
            pass


keep_alive_thread = threading.Thread(target=keep_alive_task, daemon=True)
keep_alive_thread.start()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    print()
    print("=" * 62)
    print("   Mobile Service Master - Full Web App v3.1")
    print("=" * 62)
    print()
    print(f"   Admin: {ADMIN_EMAIL}")
    print("   Local: http://127.0.0.1:5000")
    print("   OTP terminal-e print hobe")
    print("   Bondho korte: Ctrl + C")
    print()
    print("=" * 62)
    print()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)