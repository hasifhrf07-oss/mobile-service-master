"""User Onboarding — Link-based access + welcome flow"""
import os
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
ONBOARD_FILE = os.path.join(ROOT, "data", "onboarding.json")


def _load():
    if os.path.exists(ONBOARD_FILE):
        try:
            return json.load(open(ONBOARD_FILE, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data):
    os.makedirs(os.path.dirname(ONBOARD_FILE), exist_ok=True)
    json.dump(data, open(ONBOARD_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def mark_onboarded(email):
    """Mark user as onboarded"""
    data = _load()
    data[email.lower()] = {
        "onboarded": True,
        "at": datetime.now().isoformat(timespec="seconds"),
    }
    _save(data)


def is_onboarded(email):
    """Check if user is onboarded"""
    data = _load()
    return data.get(email.lower(), {}).get("onboarded", False)


def get_greeting(lang="en"):
    """Get greeting text based on language"""
    greetings = {
        "en": {
            "welcome": "Welcome to Mobile Service Master",
            "subtitle": "Professional Technician App",
            "step1": "Register with your email",
            "step2": "Verify OTP",
            "step3": "Admin approval",
            "step4": "Start using",
        },
        "bn": {
            "welcome": "Mobile Service Master-এ স্বাগতম",
            "subtitle": "পেশাদার টেকনিশিয়ান অ্যাপ",
            "step1": "আপনার ইমেইল দিয়ে রেজিস্টার করুন",
            "step2": "OTP যাচাই করুন",
            "step3": "অ্যাডমিন অনুমোদন",
            "step4": "ব্যবহার শুরু করুন",
        },
        "hi": {
            "welcome": "Mobile Service Master में आपका स्वागत है",
            "subtitle": "पेशेवर तकनीशियन ऐप",
            "step1": "अपना ईमेल दर्ज करें",
            "step2": "OTP सत्यापित करें",
            "step3": "व्यवस्थापक अनुमोदन",
            "step4": "उपयोग शुरू करें",
        },
        "ar": {
            "welcome": "مرحبًا بك في Mobile Service Master",
            "subtitle": "تطبيق الفني المحترف",
            "step1": "سجل بالبريد الإلكتروني",
            "step2": "تحقق من OTP",
            "step3": "موافقة المسؤول",
            "step4": "ابدأ الاستخدام",
        },
    }
    return greetings.get(lang, greetings["en"])


def get_stats():
    """Onboarding stats"""
    data = _load()
    total = len(data)
    onboarded = sum(1 for u in data.values() if u.get("onboarded"))
    return {"total": total, "onboarded": onboarded}
