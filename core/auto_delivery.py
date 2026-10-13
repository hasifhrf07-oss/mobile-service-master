"""
Auto Delivery System
- প্রতি ৩ মাসে auto EXE তৈরি + WhatsApp/Email-এ পাঠায়
- Admin settings থেকে configure করা যায়
"""
import os
import json
import smtplib
import subprocess
import urllib.parse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
DELIVERY_FILE = os.path.join(DATA_DIR, "delivery_config.json")
DELIVERY_LOG = os.path.join(DATA_DIR, "delivery_log.json")


def _load(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, "r", encoding="utf-8"))
        except Exception:
            return default
    return default


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    "enabled": False,
    "interval_days": 90,
    "last_build": None,
    "next_build": None,
    "delivery_methods": {
        "whatsapp": {
            "enabled": False,
            "number": "",
        },
        "email": {
            "enabled": False,
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": "",
        }
    }
}


def get_config():
    cfg = _load(DELIVERY_FILE, DEFAULT_CONFIG.copy())
    # Merge defaults
    for k, v in DEFAULT_CONFIG.items():
        if k not in cfg:
            cfg[k] = v
    return cfg


def save_config(cfg):
    _save(DELIVERY_FILE, cfg)
    return cfg


def set_interval(days):
    cfg = get_config()
    cfg["interval_days"] = int(days)
    save_config(cfg)
    return cfg


# ═══════════════════════════════════════════════════════════
# BUILD EXE
# ═══════════════════════════════════════════════════════════

def build_client_exe():
    """Build Client EXE via PyInstaller"""
    try:
        os.chdir(ROOT)
        result = subprocess.run(
            ["pyinstaller", "client.spec", "--clean", "--noconfirm"],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode == 0:
            exe_path = os.path.join(ROOT, "dist", "MobileServiceMaster_Client.exe")
            if os.path.exists(exe_path):
                return True, exe_path
        return False, result.stderr[-500:]
    except Exception as e:
        return False, str(e)


def build_admin_exe():
    """Build Admin EXE"""
    try:
        os.chdir(ROOT)
        result = subprocess.run(
            ["pyinstaller", "admin.spec", "--clean", "--noconfirm"],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode == 0:
            exe_path = os.path.join(ROOT, "dist", "MobileServiceMaster_Admin.exe")
            if os.path.exists(exe_path):
                return True, exe_path
        return False, result.stderr[-500:]
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════
# DELIVERY: EMAIL
# ═══════════════════════════════════════════════════════════

def send_email_with_attachment(subject, body, attachment_path):
    cfg = get_config()
    email_cfg = cfg.get("delivery_methods", {}).get("email", {})

    if not email_cfg.get("enabled"):
        return False, "Email delivery disabled"

    sender = email_cfg.get("sender_email")
    password = email_cfg.get("sender_password")
    recipient = email_cfg.get("recipient_email")

    if not sender or not password or not recipient:
        return False, "Email config incomplete"

    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Attach file
        if os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(attachment_path)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                msg.attach(part)

        server = smtplib.SMTP(email_cfg.get("smtp_host", "smtp.gmail.com"),
                              email_cfg.get("smtp_port", 587))
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        return True, "Email sent"
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════
# DELIVERY: WHATSAPP (via wa.me link — for manual send)
# ═══════════════════════════════════════════════════════════

def get_whatsapp_link(message=""):
    """Generate WhatsApp share link (opens in browser)"""
    cfg = get_config()
    number = cfg.get("delivery_methods", {}).get("whatsapp", {}).get("number", "")

    if not number:
        return None

    # Remove +, spaces
    clean_number = number.replace("+", "").replace(" ", "").replace("-", "")

    text = urllib.parse.quote(message or "New Mobile Service Master EXE build ready!")
    return f"https://wa.me/{clean_number}?text={text}"


# ═══════════════════════════════════════════════════════════
# MAIN AUTO DELIVERY
# ═══════════════════════════════════════════════════════════

def should_auto_deliver():
    """Check if 3 months passed since last build"""
    cfg = get_config()
    if not cfg.get("enabled"):
        return False, "Auto delivery disabled"

    last = cfg.get("last_build")
    if not last:
        return True, "Never built before"

    try:
        last_dt = datetime.fromisoformat(last)
        days_since = (datetime.now() - last_dt).days
        interval = cfg.get("interval_days", 90)
        if days_since >= interval:
            return True, f"{days_since} days since last build"
        return False, f"Last build {days_since} days ago"
    except Exception:
        return True, "Invalid date"


def run_auto_delivery():
    """Full auto-delivery: build EXE + send"""
    result = {
        "ok": False,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "actions": [],
    }

    # Check timing
    should_run, reason = should_auto_deliver()
    result["reason"] = reason

    if not should_run:
        result["message"] = f"Skipped: {reason}"
        result["ok"] = True
        return result

    # Step 1: Build Client EXE
    result["actions"].append("Building Client EXE...")
    ok, path_or_err = build_client_exe()

    if not ok:
        result["message"] = f"Build failed: {path_or_err[:200]}"
        return result

    result["actions"].append(f"✅ Client EXE: {path_or_err}")
    result["client_exe"] = path_or_err

    # Step 2: Send via Email
    cfg = get_config()
    email_cfg = cfg.get("delivery_methods", {}).get("email", {})

    if email_cfg.get("enabled"):
        subject = f"Mobile Service Master — New Build ({datetime.now().strftime('%Y-%m-%d')})"
        body = f"""
আপনার Mobile Service Master এর নতুন EXE build প্রস্তুত!

📅 Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📦 File: Client EXE
📁 Path: {path_or_err}

Latest version সহ technician-দের share করুন।

Features:
✅ 10,000+ mobile models
✅ Multi-diagnosis tool
✅ Meter photo analysis
✅ Free 6 months trial

Cloud URL: https://mobile-service-master.onrender.com

—
Mobile Service Master System
"""
        ok, msg = send_email_with_attachment(subject, body, path_or_err)
        result["actions"].append(f"Email: {msg}")
        result["email_sent"] = ok

    # Step 3: WhatsApp link
    wa_link = get_whatsapp_link(
        f"🚀 New Mobile Service Master Build Ready!\n\n"
        f"File: {os.path.basename(path_or_err)}\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"Download from: https://mobile-service-master.onrender.com"
    )
    if wa_link:
        result["whatsapp_link"] = wa_link
        result["actions"].append(f"WhatsApp link generated")

    # Step 4: Update config
    cfg["last_build"] = datetime.now().isoformat(timespec="seconds")
    cfg["next_build"] = (datetime.now() + timedelta(days=cfg.get("interval_days", 90))).isoformat(timespec="seconds")
    save_config(cfg)

    # Log
    logs = _load(DELIVERY_LOG, [])
    logs.append(result)
    logs = logs[-50:]  # Keep last 50
    _save(DELIVERY_LOG, logs)

    result["ok"] = True
    result["message"] = "Auto-delivery complete"
    return result


def get_delivery_status():
    cfg = get_config()
    logs = _load(DELIVERY_LOG, [])
    return {
        "enabled": cfg.get("enabled", False),
        "interval_days": cfg.get("interval_days", 90),
        "last_build": cfg.get("last_build"),
        "next_build": cfg.get("next_build"),
        "email_enabled": cfg.get("delivery_methods", {}).get("email", {}).get("enabled", False),
        "whatsapp_enabled": cfg.get("delivery_methods", {}).get("whatsapp", {}).get("enabled", False),
        "recent_logs": logs[-5:],
    }
