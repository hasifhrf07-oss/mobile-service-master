"""Secure Connect Protocol"""
import os, json, hmac, hashlib, secrets
from datetime import datetime
from core.app_secret import (generate_device_fingerprint, generate_device_secret,
                              verify_device_secret, generate_session_token,
                              verify_session_token, _load_devices)

ROOT = os.path.dirname(os.path.dirname(__file__))
LOG = os.path.join(ROOT, "data", "connect_log.jsonl")


def _log(d):
    entry = {"at": datetime.now().isoformat(timespec="seconds"), **d}
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def initiate_handshake(device_info, user_email):
    fp = generate_device_fingerprint(device_info)
    ds = generate_device_secret(device_info)
    challenge = secrets.token_hex(16)
    _log({"action": "init", "user": user_email, "fp": fp})
    return {"ok": True, "fingerprint": fp, "challenge": challenge,
            "existing_device": ds.get("existing", False),
            "session_token": generate_session_token(user_email, fp)}


def complete_handshake(fp, challenge_response, session_token):
    tc = verify_session_token(session_token)
    if not tc["ok"]:
        _log({"action": "fail", "reason": "bad_token", "fp": fp})
        return {"ok": False, "reason": "Invalid session"}
    devices = _load_devices()
    if fp not in devices:
        _log({"action": "fail", "reason": "unknown", "fp": fp})
        return {"ok": False, "reason": "Unknown device"}
    stored = devices[fp]["secret"]
    expected = hmac.new(stored.encode(), challenge_response.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected[:16], challenge_response[-16:]):
        _log({"action": "fail", "reason": "bad_challenge", "fp": fp})
        return {"ok": False, "reason": "Bad challenge"}
    _log({"action": "ok", "fp": fp, "user": tc["payload"]["user"]})
    return {"ok": True, "fingerprint": fp, "user": tc["payload"]["user"],
            "message": "Secure connection established"}


def get_connect_status():
    devices = _load_devices()
    recent_ok = recent_fail = 0
    if os.path.exists(LOG):
        try:
            with open(LOG, "r", encoding="utf-8") as f:
                for line in f.readlines()[-100:]:
                    if '"action": "ok"' in line: recent_ok += 1
                    elif '"action": "fail"' in line: recent_fail += 1
        except Exception: pass
    return {"known_devices": len(devices), "recent_successful": recent_ok, "recent_failed": recent_fail}


def get_recent_attempts(limit=20):
    if not os.path.exists(LOG): return []
    try:
        with open(LOG, "r", encoding="utf-8") as f:
            return [json.loads(l) for l in f.readlines()[-limit:] if l.strip()]
    except Exception: return []
