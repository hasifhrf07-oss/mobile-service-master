"""Subscription Manager — 6-month trial + warning"""
import os
import json
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(__file__))
SUBS_FILE = os.path.join(ROOT, "data", "subscriptions.json")
TRIAL_DAYS = int(os.getenv("TRIAL_DAYS", "180"))
WARNING_DAYS = int(os.getenv("WARNING_DAYS_BEFORE_EXPIRY", "60"))


def _load():
    if os.path.exists(SUBS_FILE):
        try:
            return json.load(open(SUBS_FILE, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data):
    os.makedirs(os.path.dirname(SUBS_FILE), exist_ok=True)
    json.dump(data, open(SUBS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def register_trial(email):
    data = _load()
    if email in data:
        return data[email]
    now = datetime.now()
    sub = {
        "email": email,
        "plan": "trial",
        "started_at": now.isoformat(timespec="seconds"),
        "expires_at": (now + timedelta(days=TRIAL_DAYS)).isoformat(timespec="seconds"),
        "warning_shown": False,
    }
    data[email] = sub
    _save(data)
    return sub


def check_status(email):
    data = _load()
    sub = data.get(email)
    if not sub:
        sub = register_trial(email)
    try:
        expires = datetime.fromisoformat(sub["expires_at"])
        days_left = (expires - datetime.now()).days
    except Exception:
        days_left = 0
    status = "active"
    if days_left < 0:
        status = "expired"
    elif days_left <= WARNING_DAYS:
        status = "warning"
    return {
        "email": email,
        "plan": sub.get("plan", "trial"),
        "days_left": days_left,
        "status": status,
        "show_warning": status in ("warning", "expired"),
        "expires_at": sub.get("expires_at"),
        "trial_days": TRIAL_DAYS,
    }


def upgrade_plan(email, plan="paid"):
    data = _load()
    if email not in data:
        return False
    data[email]["plan"] = plan
    data[email]["upgraded_at"] = datetime.now().isoformat(timespec="seconds")
    _save(data)
    return True
