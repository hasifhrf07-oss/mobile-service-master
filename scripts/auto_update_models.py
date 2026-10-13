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
META_FILE = os.path.join(ROOT, "data", "update_meta.json")

UPDATE_URL = "https://raw.githubusercontent.com/hasifhrf07-oss/mobile-service-master/main/data/new_models.json"
UPDATE_INTERVAL_DAYS = 15


def _load_meta():
    if os.path.exists(META_FILE):
        try:
            return json.load(open(META_FILE, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_meta(data):
    os.makedirs(os.path.dirname(META_FILE), exist_ok=True)
    json.dump(data, open(META_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def needs_update():
    """Check if 15 days passed"""
    meta = _load_meta()
    last = meta.get("last_update")
    if not last:
        return True, "Never updated"
    try:
        last_dt = datetime.fromisoformat(last)
        days = (datetime.now() - last_dt).days
        if days >= UPDATE_INTERVAL_DAYS:
            return True, f"{days} days since last update"
        return False, f"Last update {days} days ago"
    except Exception:
        return True, "Invalid timestamp"


def fetch_new_models():
    """Download new models from GitHub"""
    try:
        req = urllib.request.Request(UPDATE_URL, headers={"User-Agent": "MSM/3.1"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("models", [])
    except Exception as e:
        return {"error": str(e)[:100]}


def add_models(models):
    """Add models to DB"""
    if not isinstance(models, list):
        return 0, "Invalid data"

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    added = 0
    skipped = 0

    for m in models:
        try:
            brand = m.get("brand", "").strip()
            model = m.get("model", "").strip()
            if not brand or not model:
                skipped += 1
                continue
            existing = cur.execute(
                "SELECT id FROM devices WHERE brand=? AND model=?",
                (brand, model)
            ).fetchone()
            if existing:
                skipped += 1
                continue
            cur.execute("""
                INSERT INTO devices
                (brand, model, codename, chipset, android_ver,
                 release_year, is_clone, common_issues, hw_guide_path, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                brand, model,
                m.get("codename", ""),
                m.get("chipset", ""),
                m.get("android_ver", ""),
                int(m.get("release_year", 0)),
                int(m.get("is_clone", 0)),
                json.dumps(m.get("common_issues", [])),
                m.get("hw_guide_path", ""),
            ))
            added += 1
        except Exception:
            skipped += 1

    conn.commit()
    conn.close()
    return added, f"Added {added}, skipped {skipped}"


def run_update():
    """Main entry point"""
    result = {
        "ok": False,
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "action": "none",
        "message": "",
    }

    needed, reason = needs_update()
    result["update_needed"] = needed
    result["reason"] = reason

    if not needed:
        result["ok"] = True
        result["message"] = f"No update needed — {reason}"
        return result

    models = fetch_new_models()
    if isinstance(models, dict) and models.get("error"):
        result["message"] = f"Fetch failed: {models['error']}"
        return result

    if not models:
        result["ok"] = True
        result["message"] = "No new models available"
        _save_meta({"last_update": datetime.now().isoformat(timespec="seconds"), "last_count": 0})
        return result

    added, msg = add_models(models)
    _save_meta({
        "last_update": datetime.now().isoformat(timespec="seconds"),
        "last_count": added,
    })

    result["ok"] = True
    result["action"] = "added"
    result["added"] = added
    result["message"] = msg
    return result


def get_status():
    """Current update status"""
    meta = _load_meta()
    needed, reason = needs_update()
    return {
        "last_update": meta.get("last_update", "Never"),
        "last_count": meta.get("last_count", 0),
        "interval_days": UPDATE_INTERVAL_DAYS,
        "needs_update": needed,
        "reason": reason,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("AUTO MODEL UPDATE")
    print("=" * 60)
    status = get_status()
    for k, v in status.items():
        print(f"  {k}: {v}")
    print()
    print("Running update check...")
    result = run_update()
    for k, v in result.items():
        print(f"  {k}: {v}")
