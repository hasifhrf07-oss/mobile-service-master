"""Auto-Approve Pending Users — 24h delay"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import db

AUTO_APPROVE_HOURS = 24


def auto_approve_pending(hours=None):
    hours = hours or AUTO_APPROVE_HOURS
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat(timespec="seconds")
    pending = db.list_pending_users()
    approved_count = 0
    skipped = []
    for user in pending:
        created = user.get("created_at", "")
        email = user.get("email", "")
        if not created:
            skipped.append(email)
            continue
        if created <= cutoff:
            ok = db.approve_user(email, "system-auto", role="technician")
            if ok:
                db.log_activity(email, "auto_approved", f"Auto-approved after {hours}h", "system")
                approved_count += 1
        else:
            skipped.append(email)
    return {
        "ok": True,
        "approved": approved_count,
        "pending": len(skipped),
        "total": len(pending),
        "cutoff": cutoff,
        "ran_at": datetime.now().isoformat(timespec="seconds"),
    }


def stats():
    all_users = db.list_all_users()
    return {
        "total": len(all_users),
        "pending": len([u for u in all_users if u.get("status") == "pending"]),
        "approved": len([u for u in all_users if u.get("status") == "approved"]),
        "rejected": len([u for u in all_users if u.get("status") == "rejected"]),
        "auto_approve_hours": AUTO_APPROVE_HOURS,
    }


if __name__ == "__main__":
    result = auto_approve_pending()
    print(f"Approved: {result['approved']}, Pending: {result['pending']}")
    print(f"Stats: {stats()}")
