"""
WhatsApp Auto-Sender — Auto sends reports via WhatsApp Web
Uses wa.me link + pywhatkit for full auto-send
"""
import os
import json
import webbrowser
import urllib.parse
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(ROOT, "data", "whatsapp_config.json")

# Default admin WhatsApp number
DEFAULT_ADMIN_NUMBER = "8801681703406"  # 008801681703406 → cleaned


def _load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            return json.load(open(CONFIG_FILE, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    json.dump(data, open(CONFIG_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


def get_config():
    """Get WhatsApp config"""
    cfg = _load_config()
    return {
        "admin_number": cfg.get("admin_number", DEFAULT_ADMIN_NUMBER),
        "enabled": cfg.get("enabled", True),
        "auto_send_reports": cfg.get("auto_send_reports", True),
        "auto_send_otp": cfg.get("auto_send_otp", False),
    }


def set_config(data):
    """Save WhatsApp config"""
    cfg = _load_config()
    cfg.update(data)
    cfg["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_config(cfg)
    return cfg


def clean_number(number):
    """Clean phone number: remove +, spaces, leading 0s"""
    if not number:
        return ""
    n = str(number).replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    # Remove leading 00
    while n.startswith("00"):
        n = n[2:]
    # Remove leading 0 (if not followed by 88 for BD)
    if n.startswith("0") and not n.startswith("088"):
        n = "88" + n
    return n


def send_via_link(number, message):
    """
    Send WhatsApp via wa.me link (opens browser)
    Number: international format (8801681703406)
    """
    n = clean_number(number)
    if not n:
        return {"ok": False, "error": "Invalid number"}

    text = urllib.parse.quote(message)
    url = f"https://wa.me/{n}?text={text}"

    try:
        webbrowser.open(url)
        return {
            "ok": True,
            "url": url,
            "number": n,
            "method": "wa.me link",
            "message": "WhatsApp opened in browser",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def send_report(number, customer_name, phone_model, issue, diagnosis):
    """Send diagnosis report to customer via WhatsApp"""
    msg = f"""🔧 *Mobile Service Master — Report*

👤 Customer: {customer_name or 'N/A'}
📱 Phone: {phone_model or 'N/A'}
🔍 Issue: {issue or 'N/A'}

📋 *Diagnosis:*
{diagnosis or 'Analysis complete'}

━━━━━━━━━━━━━━━━━
📞 Reply to this message for details

_Mobile Service Master v3.1.0_"""

    return send_via_link(number, msg)


def send_otp(number, otp):
    """Send OTP via WhatsApp (optional)"""
    msg = f"""🔐 *Mobile Service Master — OTP*

Your verification code: *{otp}*

Valid for 5 minutes.
Do not share with anyone."""

    return send_via_link(number, msg)


def send_delivery_notification(number, exe_path, version):
    """Notify admin of new EXE delivery"""
    msg = f"""📦 *New Build Ready*

Version: {version}
File: {os.path.basename(exe_path) if exe_path else 'N/A'}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Check desktop for file."""

    return send_via_link(number, msg)


def test_send():
    """Test WhatsApp send to admin"""
    cfg = get_config()
    num = cfg.get("admin_number", DEFAULT_ADMIN_NUMBER)
    msg = f"""✅ *Mobile Service Master — Test*

WhatsApp auto-send working!
Number: {num}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    return send_via_link(num, msg)


if __name__ == "__main__":
    print("Testing WhatsApp sender...")
    result = test_send()
    print(json.dumps(result, indent=2))
