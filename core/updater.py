import json
import os
import sqlite3
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(ROOT, "database", "devices.db")
URL_FILE = os.path.join(ROOT, "database", "update_url.txt")


def get_update_url():
    if os.path.exists(URL_FILE):
        with open(URL_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def set_update_url(url):
    os.makedirs(os.path.dirname(URL_FILE), exist_ok=True)
    with open(URL_FILE, "w", encoding="utf-8") as f:
        f.write(url.strip())
    return True


def check_and_update(verbose=True):
    result = {"ok": False, "message": "", "added": 0, "version": ""}
    url = get_update_url()
    if not url:
        result["message"] = "⚠️ Update URL সেট করা নেই"
        if verbose:
            print(result["message"])
        return result

    try:
        if verbose:
            print(f"🔄 Fetching: {url}")

        req = urllib.request.Request(url, headers={"User-Agent": "MSM/3.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))

        new_version = str(data.get("version", "0"))
        new_devices = data.get("devices", [])

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        row = cur.execute(
            "SELECT v FROM meta WHERE k='db_version'"
        ).fetchone()
        current = row[0] if row else "0"

        if new_version == current and not new_devices:
            result["ok"] = True
            result["message"] = f"✅ আপ-টু-ডেট (v{current})"
            result["version"] = current
            conn.close()
            if verbose:
                print(result["message"])
            return result

        added = 0
        for d in new_devices:
            try:
                cur.execute("""
                    INSERT OR REPLACE INTO devices
                    (brand, model, codename, chipset, android_ver,
                     release_year, is_clone, common_issues,
                     hw_guide_path, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    d.get("brand", ""), d.get("model", ""),
                    d.get("codename", ""), d.get("chipset", ""),
                    d.get("android_ver", ""),
                    int(d.get("release_year", 0)),
                    int(d.get("is_clone", 0)),
                    json.dumps(d.get("common_issues", []), ensure_ascii=False),
                    d.get("hw_guide_path", "")
                ))
                added += 1
            except Exception as e:
                if verbose:
                    print(f"Skip {d.get('model')}: {e}")

        cur.execute("INSERT OR REPLACE INTO meta VALUES ('db_version', ?)",
                    (new_version,))
        cur.execute("INSERT OR REPLACE INTO meta VALUES ('last_update', ?)",
                    (datetime.now().isoformat(),))
        cur.execute("INSERT INTO update_log (version, added) VALUES (?, ?)",
                    (new_version, added))

        conn.commit()
        conn.close()

        result["ok"] = True
        result["added"] = added
        result["version"] = new_version
        result["message"] = (
            f"✅ আপডেট সফল: v{current} → v{new_version}, {added} মডেল"
        )
        if verbose:
            print(result["message"])
        return result

    except Exception as e:
        result["message"] = f"❌ আপডেট ব্যর্থ: {e}"
        if verbose:
            print(result["message"])
        return result 