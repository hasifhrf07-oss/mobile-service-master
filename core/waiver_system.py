"""Digital Waiver System"""
import os, json, hashlib
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
WAIVER_FILE = os.path.join(ROOT, "data", "waivers.json")
WAIVER_LOG = os.path.join(ROOT, "data", "waiver_acceptances.jsonl")

WAIVER_TEMPLATE = """
MOBILE SERVICE MASTER — LIABILITY WAIVER

I, the undersigned technician, agree:

1. I am a trained mobile service technician.
2. I will use this app ONLY for authorized repair work.
3. I will NOT use it for:
   - FRP bypass without owner consent
   - IMEI manipulation
   - Network unlocking without carrier permission
4. I am solely responsible for my actions.
5. Mobile Service Master provides tools "as is".
6. Company is not liable for legal issues from my use.

User: {user_email}
Date: {date}
IP: {ip}
Platform: {platform}
Signature: {signature}
"""


def _load():
    if os.path.exists(WAIVER_FILE):
        try: return json.load(open(WAIVER_FILE, "r", encoding="utf-8"))
        except Exception: return {}
    return {}


def _save(data):
    os.makedirs(os.path.dirname(WAIVER_FILE), exist_ok=True)
    json.dump(data, open(WAIVER_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def get_waiver_text(user_email="", ip="", platform="Web"):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sig = hashlib.sha256(f"{user_email}|{date}|{ip}".encode()).hexdigest()[:32]
    return WAIVER_TEMPLATE.format(
        user_email=user_email or "Anonymous", date=date,
        ip=ip or "unknown", platform=platform, signature=sig)


def accept_waiver(user_email, ip="", platform="Web"):
    date = datetime.now().isoformat(timespec="seconds")
    sig = hashlib.sha256(f"{user_email}|{date}|{ip}".encode()).hexdigest()[:32]
    record = {"user": user_email, "accepted_at": date, "ip": ip,
              "platform": platform, "signature": sig, "version": "3.1.0"}
    data = _load()
    data[user_email] = record
    _save(data)
    os.makedirs(os.path.dirname(WAIVER_LOG), exist_ok=True)
    with open(WAIVER_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"ok": True, "signature": sig, "record": record}


def has_accepted(user_email):
    return user_email in _load()


def get_acceptance(user_email):
    return _load().get(user_email)


def list_all():
    return list(_load().values())
