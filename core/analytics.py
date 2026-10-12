"""
User Analytics — Track live users, sessions, activity
"""
import os
import json
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
ANALYTICS_FILE = os.path.join(DATA_DIR, "analytics.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")

os.makedirs(DATA_DIR, exist_ok=True)

LIVE_WINDOW_MINUTES = 5  # active if pinged in last 5 min


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
# SESSION TRACKING
# ═══════════════════════════════════════════════════════════

def ping_user(email, ip="", device=""):
    """Record user activity (called on page load)"""
    sessions = _load(SESSIONS_FILE, {})
    now = datetime.now().isoformat(timespec="seconds")

    if email not in sessions:
        sessions[email] = {
            "email": email,
            "first_seen": now,
            "last_seen": now,
            "ping_count": 1,
            "ip": ip,
            "device": device,
        }
    else:
        sessions[email]["last_seen"] = now
        sessions[email]["ping_count"] = sessions[email].get("ping_count", 0) + 1
        if ip:
            sessions[email]["ip"] = ip
        if device:
            sessions[email]["device"] = device

    _save(SESSIONS_FILE, sessions)
    return sessions[email]


def get_live_users():
    """Users active in last 5 minutes"""
    sessions = _load(SESSIONS_FILE, {})
    cutoff = (datetime.now() - timedelta(minutes=LIVE_WINDOW_MINUTES)).isoformat(timespec="seconds")

    live = []
    for email, data in sessions.items():
        if data.get("last_seen", "") >= cutoff:
            live.append({
                "email": email,
                "last_seen": data.get("last_seen"),
                "ip": data.get("ip", ""),
                "device": data.get("device", ""),
                "ping_count": data.get("ping_count", 0),
            })

    live.sort(key=lambda x: x["last_seen"], reverse=True)
    return live


def get_all_users_stats():
    """Complete user statistics"""
    sessions = _load(SESSIONS_FILE, {})

    # Time buckets
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()

    live_count = 0
    today_count = 0
    week_count = 0
    month_count = 0

    for data in sessions.values():
        last = data.get("last_seen", "")
        if last >= (now - timedelta(minutes=LIVE_WINDOW_MINUTES)).isoformat(timespec="seconds"):
            live_count += 1
        if last.startswith(today):
            today_count += 1
        if last >= week_ago:
            week_count += 1
        if last >= month_ago:
            month_count += 1

    return {
        "total_users": len(sessions),
        "live_now": live_count,
        "active_today": today_count,
        "active_this_week": week_count,
        "active_this_month": month_count,
        "live_window_minutes": LIVE_WINDOW_MINUTES,
        "checked_at": now.isoformat(timespec="seconds"),
    }


def get_user_details(email):
    """Details of one user"""
    sessions = _load(SESSIONS_FILE, {})
    return sessions.get(email)


# ═══════════════════════════════════════════════════════════
# ACTIVITY LOG
# ═══════════════════════════════════════════════════════════

def log_event(email, event_type, details=""):
    """Log a specific event"""
    data = _load(ANALYTICS_FILE, {"events": []})

    data["events"].append({
        "email": email,
        "type": event_type,
        "details": details,
        "at": datetime.now().isoformat(timespec="seconds"),
    })

    # Keep only last 1000 events
    if len(data["events"]) > 1000:
        data["events"] = data["events"][-1000:]

    _save(ANALYTICS_FILE, data)


def get_recent_events(limit=50):
    """Recent activity events"""
    data = _load(ANALYTICS_FILE, {"events": []})
    events = data.get("events", [])
    return list(reversed(events))[:limit]
