"""
Auto-Connect Engine
- Photo → Analysis → Auto-add to detector DB → Connected status
- Mobile-এর সাথে app link করে (session + admin tracking)
"""
import os
import json
import sqlite3
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(ROOT, "database", "devices.db")
CONNECTED_FILE = os.path.join(ROOT, "data", "connected_devices.json")


def _load_connected():
    if os.path.exists(CONNECTED_FILE):
        try:
            return json.load(open(CONNECTED_FILE, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_connected(data):
    os.makedirs(os.path.dirname(CONNECTED_FILE), exist_ok=True)
    json.dump(data, open(CONNECTED_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════
# AUTO-ADD TO DETECTOR DB
# ═══════════════════════════════════════════════════════════

def auto_add_to_detector(brand, model, **kwargs):
    """
    Photo-থেকে পাওয়া brand/model auto database-এ যোগ করে।
    Returns: (added: bool, existed: bool, model_data: dict)
    """
    if not brand or not model:
        return False, False, {}

    brand = brand.strip()
    model = model.strip()

    try:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Check existing
        existing = cur.execute(
            "SELECT * FROM devices WHERE brand=? AND model=?",
            (brand, model)
        ).fetchone()

        if existing:
            conn.close()
            return False, True, dict(existing)

        # Insert new
        cur.execute("""
            INSERT INTO devices
            (brand, model, codename, chipset, android_ver,
             release_year, is_clone, common_issues, hw_guide_path, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            brand, model,
            kwargs.get("codename", ""),
            kwargs.get("chipset", ""),
            kwargs.get("android_ver", ""),
            int(kwargs.get("release_year", 0)),
            int(kwargs.get("is_clone", 0)),
            json.dumps(kwargs.get("common_issues", ["User-photo-added"])),
            kwargs.get("hw_guide_path", ""),
        ))

        conn.commit()

        # Get inserted row
        inserted = cur.execute(
            "SELECT * FROM devices WHERE brand=? AND model=?",
            (brand, model)
        ).fetchone()

        conn.close()
        return True, False, dict(inserted) if inserted else {}

    except Exception as e:
        print(f"[AUTO-ADD ERROR] {e}")
        return False, False, {}


# ═══════════════════════════════════════════════════════════
# CONNECT DEVICE — Link mobile with app
# ═══════════════════════════════════════════════════════════

def connect_device(user_email, photo_paths, analysis_result):
    """
    Photo analysis-এর result দিয়ে device-কে app-এ connect করে।
    
    Returns:
    {
        "connected": bool,
        "session_id": str,
        "device": {...},
        "message": str,
    }
    """
    session_id = f"msm_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_email.split('@')[0]}"

    # Extract device info from analysis
    brand = analysis_result.get("brand") or analysis_result.get("brand_detected") or ""
    model = analysis_result.get("model") or ""
    chipset = analysis_result.get("chipset", "")

    # Auto-add to detector
    added = False
    existed = False
    model_data = {}

    if brand and model:
        added, existed, model_data = auto_add_to_detector(
            brand=brand,
            model=model,
            chipset=chipset,
            common_issues=["Auto-added from photo analysis"],
        )

    # Save connection
    connected = _load_connected()
    connected[session_id] = {
        "session_id": session_id,
        "user_email": user_email,
        "connected_at": datetime.now().isoformat(timespec="seconds"),
        "status": "connected",
        "device": {
            "brand": brand,
            "model": model,
            "chipset": chipset,
        },
        "photos": list(photo_paths.keys()),
        "confidence": analysis_result.get("confidence", 0),
        "auto_added": added,
        "already_existed": existed,
    }
    _save_connected(connected)

    return {
        "connected": True,
        "session_id": session_id,
        "device": model_data or {"brand": brand, "model": model},
        "auto_added": added,
        "already_existed": existed,
        "message": f"✅ Mobile Connected — Session: {session_id}",
    }


def disconnect_device(session_id):
    """Disconnect mobile from app"""
    connected = _load_connected()
    if session_id in connected:
        connected[session_id]["status"] = "disconnected"
        connected[session_id]["disconnected_at"] = datetime.now().isoformat(timespec="seconds")
        _save_connected(connected)
        return True
    return False


def get_connected_devices():
    """All currently connected devices"""
    connected = _load_connected()
    active = [v for v in connected.values() if v.get("status") == "connected"]
    active.sort(key=lambda x: x.get("connected_at", ""), reverse=True)
    return active


def get_session_details(session_id):
    """Details of one session"""
    connected = _load_connected()
    return connected.get(session_id)
