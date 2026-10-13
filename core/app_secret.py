"""App Secret Manager"""
import os, hmac, hashlib, secrets, json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

ROOT = os.path.dirname(os.path.dirname(__file__))
SECRET_DIR = os.path.join(ROOT, "data", "secrets")
os.makedirs(SECRET_DIR, exist_ok=True)

APP_KEY_FILE = os.path.join(SECRET_DIR, "app.key")
APP_SECRET_FILE = os.path.join(SECRET_DIR, "app_secret.json")
DEVICE_KEYS_FILE = os.path.join(SECRET_DIR, "device_keys.json")


def get_app_cipher():
    if os.path.exists(APP_KEY_FILE):
        with open(APP_KEY_FILE, "rb") as f: key = f.read()
    else:
        key = Fernet.generate_key()
        with open(APP_KEY_FILE, "wb") as f: f.write(key)
    return Fernet(key)


def get_app_id():
    if os.path.exists(APP_SECRET_FILE):
        try: return json.load(open(APP_SECRET_FILE, "r", encoding="utf-8"))
        except Exception: pass
    data = {"app_id": secrets.token_hex(16), "app_name": "Mobile Service Master",
            "version": "3.1.0", "created_at": datetime.now().isoformat(timespec="seconds"),
            "installation_id": secrets.token_hex(8)}
    json.dump(data, open(APP_SECRET_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return data


def encrypt_data(plaintext):
    cipher = get_app_cipher()
    if isinstance(plaintext, dict): plaintext = json.dumps(plaintext, ensure_ascii=False)
    return cipher.encrypt(plaintext.encode()).decode()


def decrypt_data(token):
    try: return get_app_cipher().decrypt(token.encode()).decode()
    except Exception: return None


def generate_device_fingerprint(device_info):
    parts = [str(device_info.get(k, "")) for k in ["serial", "brand", "model", "chipset", "android"]]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def _load_devices():
    if os.path.exists(DEVICE_KEYS_FILE):
        try: return json.load(open(DEVICE_KEYS_FILE, "r", encoding="utf-8"))
        except Exception: return {}
    return {}


def _save_devices(d):
    json.dump(d, open(DEVICE_KEYS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def generate_device_secret(device_info):
    fp = generate_device_fingerprint(device_info)
    devices = _load_devices()
    if fp in devices:
        return {"ok": True, "existing": True, "fingerprint": fp,
                "secret": devices[fp]["secret"], "token": devices[fp]["token"]}
    secret = secrets.token_hex(32)
    token = secrets.token_hex(16)
    devices[fp] = {"secret": secret, "token": token, "device_info": device_info,
                   "created_at": datetime.now().isoformat(timespec="seconds"),
                   "last_used": datetime.now().isoformat(timespec="seconds"), "use_count": 1}
    _save_devices(devices)
    return {"ok": True, "existing": False, "fingerprint": fp, "secret": secret, "token": token}


def verify_device_secret(fp, secret):
    devices = _load_devices()
    if fp not in devices: return {"ok": False, "reason": "Unknown device"}
    if not hmac.compare_digest(devices[fp]["secret"], secret):
        return {"ok": False, "reason": "Invalid secret"}
    devices[fp]["last_used"] = datetime.now().isoformat(timespec="seconds")
    devices[fp]["use_count"] += 1
    _save_devices(devices)
    return {"ok": True, "device_info": devices[fp]["device_info"]}


def list_known_devices():
    return [{"fingerprint": fp, **{k: v for k, v in d.items() if k != "secret"}} for fp, d in _load_devices().items()]


def revoke_device(fp):
    devices = _load_devices()
    if fp in devices:
        del devices[fp]
        _save_devices(devices)
        return {"ok": True, "message": "Revoked"}
    return {"ok": False}


def generate_session_token(user_email, device_fp="", expiry_hours=24):
    app = get_app_id()
    payload = {"user": user_email, "device": device_fp,
               "issued": datetime.now().isoformat(timespec="seconds"),
               "expires": (datetime.now() + timedelta(hours=expiry_hours)).isoformat(timespec="seconds"),
               "nonce": secrets.token_hex(8)}
    pj = json.dumps(payload, sort_keys=True)
    sig = hmac.new(app["app_id"].encode(), pj.encode(), hashlib.sha256).hexdigest()
    import base64
    return base64.urlsafe_b64encode(json.dumps({"payload": payload, "signature": sig}).encode()).decode()


def verify_session_token(token):
    try:
        import base64
        td = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
    except Exception:
        return {"ok": False, "reason": "Malformed"}
    payload = td.get("payload", {})
    sig = td.get("signature", "")
    try:
        if datetime.fromisoformat(payload["expires"]) < datetime.now():
            return {"ok": False, "reason": "Expired"}
    except Exception:
        return {"ok": False, "reason": "Bad expiry"}
    app = get_app_id()
    expected = hmac.new(app["app_id"].encode(), json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig): return {"ok": False, "reason": "Bad sig"}
    return {"ok": True, "payload": payload}


def get_security_status():
    app = get_app_id()
    return {"app_id": app["app_id"][:8] + "...", "app_name": app["app_name"],
            "version": app["version"], "known_devices": len(list_known_devices()),
            "encryption": "Fernet AES-128", "signing": "HMAC-SHA256"}


if __name__ == "__main__":
    print("App:", get_app_id()["app_id"][:16])
    print("Status:", get_security_status())
