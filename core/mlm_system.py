"""
MLM System — Multi-Level Marketing
3 emails login — 3 months free after 3 people join
"""
import os
import json
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(__file__))
MLM_FILE = os.path.join(ROOT, "data", "mlm_data.json")

# Configuration
MLM_CONFIG = {
    "team_size_required": 3,
    "free_months_after_team": 3,
    "trial_days_default": 30,
    "commission_percent": 20,
}


def _load():
    if os.path.exists(MLM_FILE):
        try:
            return json.load(open(MLM_FILE, "r", encoding="utf-8"))
        except Exception:
            return {"users": {}, "teams": {}}
    return {"users": {}, "teams": {}}


def _save(data):
    os.makedirs(os.path.dirname(MLM_FILE), exist_ok=True)
    json.dump(data, open(MLM_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


def register_user(email, referrer_email=None):
    """
    Register user in MLM system.
    referrer_email: who invited them
    """
    data = _load()
    email = email.lower().strip()

    if email in data["users"]:
        return {"ok": False, "message": "User already exists"}

    now = datetime.now()
    user = {
        "email": email,
        "referrer": (referrer_email or "").lower().strip(),
        "team_members": [],
        "joined_at": now.isoformat(timespec="seconds"),
        "trial_ends_at": (now + timedelta(days=MLM_CONFIG["trial_days_default"])).isoformat(timespec="seconds"),
        "free_until": None,
        "status": "trial",
        "earnings": 0,
    }

    data["users"][email] = user

    # Add to referrer's team
    if referrer_email:
        ref = referrer_email.lower().strip()
        if ref in data["users"]:
            data["users"][ref]["team_members"].append(email)
            # Check if referrer team complete
            if len(data["users"][ref]["team_members"]) >= MLM_CONFIG["team_size_required"]:
                # Grant 3 months free
                free_until = (datetime.now() + timedelta(days=MLM_CONFIG["free_months_after_team"] * 30)).isoformat(timespec="seconds")
                data["users"][ref]["free_until"] = free_until
                data["users"][ref]["status"] = "free_reward"

    _save(data)

    return {
        "ok": True,
        "user": user,
        "team_count": len(user["team_members"]),
        "required": MLM_CONFIG["team_size_required"],
        "message": f"Registered! Team: {len(user['team_members'])}/{MLM_CONFIG['team_size_required']}",
    }


def add_team_member(user_email, member_email):
    """Manually add team member (admin)"""
    data = _load()
    user_email = user_email.lower().strip()
    member_email = member_email.lower().strip()

    if user_email not in data["users"]:
        return {"ok": False, "message": "User not found"}

    if member_email not in data["users"][user_email]["team_members"]:
        data["users"][user_email]["team_members"].append(member_email)

    # Check reward
    user = data["users"][user_email]
    reward_given = False
    if len(user["team_members"]) >= MLM_CONFIG["team_size_required"] and not user.get("free_until"):
        free_until = (datetime.now() + timedelta(days=MLM_CONFIG["free_months_after_team"] * 30)).isoformat(timespec="seconds")
        user["free_until"] = free_until
        user["status"] = "free_reward"
        reward_given = True

    _save(data)

    return {
        "ok": True,
        "team_count": len(user["team_members"]),
        "required": MLM_CONFIG["team_size_required"],
        "reward_given": reward_given,
        "free_until": user.get("free_until"),
        "message": f"Team: {len(user['team_members'])}/{MLM_CONFIG['team_size_required']}"
    }


def get_user_status(email):
    """Get MLM status for user"""
    data = _load()
    email = email.lower().strip()
    user = data["users"].get(email)
    if not user:
        return {"ok": False, "message": "User not found"}

    now = datetime.now()
    team_count = len(user["team_members"])
    required = MLM_CONFIG["team_size_required"]

    # Calculate days left in trial
    days_left = 0
    if user.get("free_until"):
        try:
            free_until = datetime.fromisoformat(user["free_until"])
            days_left = (free_until - now).days
        except Exception:
            pass
    elif user.get("trial_ends_at"):
        try:
            trial_end = datetime.fromisoformat(user["trial_ends_at"])
            days_left = (trial_end - now).days
        except Exception:
            pass

    return {
        "ok": True,
        "email": email,
        "status": user.get("status"),
        "team_count": team_count,
        "team_required": required,
        "team_remaining": max(0, required - team_count),
        "team_members": user.get("team_members", []),
        "referrer": user.get("referrer", ""),
        "trial_ends_at": user.get("trial_ends_at"),
        "free_until": user.get("free_until"),
        "days_left": max(0, days_left),
        "earnings": user.get("earnings", 0),
    }


def get_stats():
    """Overall MLM stats"""
    data = _load()
    users = data["users"]
    total = len(users)
    with_teams = sum(1 for u in users.values() if u.get("team_members"))
    with_reward = sum(1 for u in users.values() if u.get("free_until"))
    return {
        "total_users": total,
        "users_with_teams": with_teams,
        "users_with_reward": with_reward,
        "config": MLM_CONFIG,
    }


def process_daily():
    """Daily check — grant rewards for complete teams"""
    data = _load()
    granted = 0
    required = MLM_CONFIG["team_size_required"]

    for email, user in data["users"].items():
        if len(user.get("team_members", [])) >= required and not user.get("free_until"):
            free_until = (datetime.now() + timedelta(days=MLM_CONFIG["free_months_after_team"] * 30)).isoformat(timespec="seconds")
            user["free_until"] = free_until
            user["status"] = "free_reward"
            granted += 1

    if granted:
        _save(data)

    return {"ok": True, "granted": granted, "checked_at": datetime.now().isoformat(timespec="seconds")}


if __name__ == "__main__":
    print(json.dumps(get_stats(), indent=2))
