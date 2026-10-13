"""Auto Model Update — 15-day cycle"""
import os
import sys
import json
import sqlite3
import urllib.request
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DB = os.path.join(ROOT, "database", "devices.db")
META = os.path.join(ROOT, "data", "update_meta.json")
URL = "https://raw.githubusercontent.com/hasifhrf07-oss/mobile-service-master/main/data/new_models.json"
INTERVAL = 15


def _load_meta():
    if os.path.exists(META):
        try:
            return json.load(open(META, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_meta(d):
    os.makedirs(os.path.dirname(META), exist_ok=True)
    json.dump(d, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def needs_update():
    last = _load_meta().get("last_update")
    if not last:
        return True, "Never updated"
    try:
        days = (datetime.now() - datetime.fromisoformat(last)).days
        return (days >= INTERVAL), f"{days} days since last update"
    except Exception:
        return True, "Invalid timestamp"


def fetch_new_models():
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "MSM/3.1"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8")).get("models", [])
    except Exception as e:
        return {"error": str(e)[:100]}


def add_models(models):
    if not isinstance(models, list):
        return 0, "Invalid data"
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    added = 0
    for m in models:
        try:
            b, mo = m.get("brand", "").strip(), m.get("model", "").strip()
            if not b or not mo:
                continue
            if cur.execute("SELECT id FROM devices WHERE brand=? AND model=?", (b, mo)).fetchone():
                continue
            cur.execute("""INSERT INTO devices
                (brand, model, codename, chipset, android_ver, release_year, is_clone, common_issues, hw_guide_path, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (b, mo, m.get("codename", ""), m.get("chipset", ""), m.get("android_ver", ""),
                 int(m.get("release_year", 0)), int(m.get("is_clone", 0)),
                 json.dumps(m.get("common_issues", [])), m.get("hw_guide_path", "")))
            added += 1
        except Exception:
            pass
    conn.commit()
    conn.close()
    return added, f"Added {added}"


def run_update():
    result = {"ok": False, "checked_at": datetime.now().isoformat(timespec="seconds"), "action": "none", "message": ""}
    needed, reason = needs_update()
    result["update_needed"] = needed
    result["reason"] = reason
    if not needed:
        result["ok"] = True
        result["message"] = f"No update needed - {reason}"
        return result
    models = fetch_new_models()
    if isinstance(models, dict) and models.get("error"):
        result["message"] = f"Fetch failed: {models['error']}"
        return result
    if not models:
        result["ok"] = True
        result["message"] = "No new models"
        _save_meta({"last_update": datetime.now().isoformat(timespec="seconds"), "last_count": 0})
        return result
    added, msg = add_models(models)
    _save_meta({"last_update": datetime.now().isoformat(timespec="seconds"), "last_count": added})
    result["ok"] = True
    result["action"] = "added"
    result["added"] = added
    result["message"] = msg
    return result


def get_status():
    m = _load_meta()
    needed, reason = needs_update()
    return {
        "last_update": m.get("last_update", "Never"),
        "last_count": m.get("last_count", 0),
        "interval_days": INTERVAL,
        "needs_update": needed,
        "reason": reason,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("AUTO MODEL UPDATE")
    print("=" * 60)
    for k, v in get_status().items():
        print(f"  {k}: {v}")
    print()
    for k, v in run_update().items():
        print(f"  {k}: {v}")
