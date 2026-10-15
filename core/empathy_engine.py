"""Empathy Engine — Rule-based user support"""
import os, json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
LOG = os.path.join(ROOT, "data", "empathy_log.jsonl")

MESSAGES = {
    "first_login": "🎉 স্বাগতম! Mobile Service Master-এ আপনার প্রথম পদক্ষেপ। সাহায্য দরকার হলে বলুন।",
    "milestone_50": "🎊 আপনি ৫০টি job সম্পন্ন করেছেন — অসাধারণ! Pro level-এ এগিয়ে চলেছেন।",
    "milestone_100": "🏆 ১০০টি job! আপনি এখন একজন expert technician।",
    "inactive_7d": "💙 ৭ দিন ধরে আপনি আসেননি। কেমন আছেন? নতুন ফিচার যোগ হয়েছে।",
    "one_refer_left": "🎯 আর মাত্র ১টি referral বাকি — ৩ মাস free পাবেন!",
    "waiver_needed": "📝 আপনার liability waiver accept করা দরকার। Settings-এ যান।",
    "battery_low": "🔋 দীর্ঘ সময় কাজ করছেন। একটু বিশ্রাম নিন।",
}


def _log(data):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"at": datetime.now().isoformat(timespec="seconds"), **data}, ensure_ascii=False) + "\n")


def check_events(user_email, stats):
    """Check user events → return messages"""
    messages = []

    if stats.get("login_count") == 1:
        messages.append({"type": "first_login", "text": MESSAGES["first_login"]})
    if stats.get("jobs_completed") == 50:
        messages.append({"type": "milestone_50", "text": MESSAGES["milestone_50"]})
    if stats.get("jobs_completed") == 100:
        messages.append({"type": "milestone_100", "text": MESSAGES["milestone_100"]})
    if stats.get("inactive_days", 0) >= 7:
        messages.append({"type": "inactive_7d", "text": MESSAGES["inactive_7d"]})
    if stats.get("referrals_count") == 2 and stats.get("referrals_required") == 3:
        messages.append({"type": "one_refer_left", "text": MESSAGES["one_refer_left"]})
    if not stats.get("waiver_accepted", True):
        messages.append({"type": "waiver_needed", "text": MESSAGES["waiver_needed"]})

    for m in messages:
        _log({"user": user_email, **m})

    return messages


def get_recent(limit=50):
    if not os.path.exists(LOG):
        return []
    try:
        with open(LOG, "r", encoding="utf-8") as f:
            return [json.loads(l) for l in f.readlines()[-limit:] if l.strip()]
    except Exception:
        return []
