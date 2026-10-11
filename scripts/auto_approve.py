"""Auto-Approve Pending Users — 24h delay"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import db

AUTO_APPROVE_HOURS = 24


def auto_approve_pending(hours=None):
    """
    Pending user গুলো check করো।
    যদি registration-এর পর ২৪ ঘন্টা পার হয়ে যায় → auto-approve।
    """
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
            # 24h পার হয়েছে → approve
            ok = db.approve_user(
                email=email,
                approver_email="system-auto",
                role="technician",
            )
            if ok:
                db.log_activity(
                    user_email=email,
                    action="auto_approved",
                    details=f"Auto-approved after {hours}h",
                    ip="system",
                )
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
    """Pending + approved stats"""
    all_users = db.list_all_users()
    pending = [u for u in all_users if u.get("status") == "pending"]
    approved = [u for u in all_users if u.get("status") == "approved"]
    rejected = [u for u in all_users if u.get("status") == "rejected"]

    return {
        "total": len(all_users),
        "pending": len(pending),
        "approved": len(approved),
        "rejected": len(rejected),
        "auto_approve_hours": AUTO_APPROVE_HOURS,
    }


if __name__ == "__main__":
    result = auto_approve_pending()
    print("=" * 50)
    print("AUTO-APPROVE RESULT")
    print("=" * 50)
    print(f"  Approved  : {result['approved']}")
    print(f"  Pending   : {result['pending']}")
    print(f"  Total     : {result['total']}")
    print(f"  Cutoff    : {result['cutoff']}")
    print(f"  Ran at    : {result['ran_at']}")
    print("=" * 50)

    print()
    print("STATS:")
    s = stats()
    print(f"  Total users     : {s['total']}")
    print(f"  Pending         : {s['pending']}")
    print(f"  Approved        : {s['approved']}")
    print(f"  Rejected        : {s['rejected']}")
    print(f"  Auto-approve    : {s['auto_approve_hours']}h delay")
    print("=" * 50)