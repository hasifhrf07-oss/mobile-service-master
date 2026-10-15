"""Deals Engine"""
DEAL_RULES = [
    {"id": "ref_3_free", "cond": {"referrals": 3}, "offer": "3 months free", "discount": 100},
    {"id": "jobs_100", "cond": {"jobs": 100}, "offer": "1 month 50% off", "discount": 50},
    {"id": "trial_7d", "cond": {"trial_days_left_less_than": 7}, "offer": "20% off", "discount": 20},
    {"id": "inactive_30", "cond": {"inactive_days": 30}, "offer": "Come back 30% off", "discount": 30},
]


def get_active_deals(user_email, stats):
    deals = []
    for r in DEAL_RULES:
        c = r["cond"]
        ok = True
        if "referrals" in c and stats.get("referrals_count", 0) < c["referrals"]:
            ok = False
        if "jobs" in c and stats.get("jobs_completed", 0) < c["jobs"]:
            ok = False
        if "trial_days_left_less_than" in c and stats.get("trial_days_left", 999) > c["trial_days_left_less_than"]:
            ok = False
        if "inactive_days" in c and stats.get("inactive_days", 0) < c["inactive_days"]:
            ok = False
        if ok:
            deals.append({"id": r["id"], "offer": r["offer"], "discount_percent": r["discount"], "user": user_email})
    return deals


def get_all_deals():
    return DEAL_RULES
