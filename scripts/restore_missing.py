"""
MASTER RESTORE SCRIPT
Auto-creates all missing .py files with complete content
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════
# ALL MISSING FILES + THEIR CONTENT
# ═══════════════════════════════════════════════════════════

FILES = {

    "core/photo_connect.py": '''"""Photo Connect Engine"""
import os
from datetime import datetime

EXPECTED_RAILS = {
    "vbat":     {"min": 3.5, "max": 4.3, "typical": 3.8, "label": "VBAT"},
    "vph_pwr":  {"min": 3.5, "max": 4.3, "typical": 3.75, "label": "VPH_PWR"},
    "vdd_cpu":  {"min": 0.85, "max": 1.35, "typical": 1.10, "label": "VDD_CPU"},
    "vdd_mem":  {"min": 1.05, "max": 1.25, "typical": 1.12, "label": "VDD_MEM"},
    "vcc_io":   {"min": 1.70, "max": 1.90, "typical": 1.80, "label": "VCC_IO"},
    "emmc_vcc": {"min": 3.0, "max": 3.5, "typical": 3.3, "label": "eMMC_VCC"},
    "vcc_usb":  {"min": 4.75, "max": 5.25, "typical": 5.0, "label": "VCC_USB"},
}


def get_connect_status():
    return {
        "enabled": True,
        "method": "OCR + Database Matching",
        "confidence_threshold": 80,
        "supported_photos": ["analogue_meter", "multimeter", "dc_supply", "extra"],
        "chipsets": ["exynos", "snapdragon", "mediatek", "generic"],
    }


def detect_chipset_from_text(text):
    t = (text or "").lower()
    if any(k in t for k in ["exynos", "samsung"]):
        return "exynos"
    if any(k in t for k in ["snapdragon", "qualcomm", "sdm"]):
        return "snapdragon"
    if any(k in t for k in ["mediatek", "mtk", "helio", "dimensity"]):
        return "mediatek"
    return "generic"


def photo_connect(photo_paths, brand_text=""):
    started = datetime.now()

    try:
        from core.meter_engine.engine import analyze_meter_photos
        analysis = analyze_meter_photos(photo_paths)
    except Exception:
        analysis = {"ok": True, "readings": []}

    readings = analysis.get("readings", [])
    if isinstance(readings, dict):
        readings = list(readings.values())

    chipset = detect_chipset_from_text(brand_text or analysis.get("brand", ""))

    matches, mismatches = [], []
    for r in readings:
        if not isinstance(r, dict):
            continue
        rail = (r.get("rail") or "").lower()
        v = r.get("value")
        if not rail or v is None:
            continue
        if rail in EXPECTED_RAILS:
            info = EXPECTED_RAILS[rail]
            if info["min"] <= v <= info["max"]:
                matches.append({"rail": rail, "value": v, "status": "match"})
            else:
                mismatches.append({"rail": rail, "value": v, "status": "mismatch"})

    total = len(matches) + len(mismatches)
    score = int((len(matches) / total) * 100) if total else 0
    status = "CONNECTED" if score >= 80 else ("PARTIAL" if score >= 50 else "FAILED")

    return {
        "ok": True,
        "connected": score >= 80,
        "status": status,
        "confidence": score,
        "chipset": chipset,
        "matches": matches,
        "mismatches": mismatches,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "message": f"{'OK' if score >= 80 else status} ({score}%)",
    }
''',

    "core/deep_analyzer.py": '''"""Deep Analyzer"""
import os
from datetime import datetime

EXPECTED_RAILS = {
    "vbat":     {"min": 3.5, "max": 4.3, "label": "VBAT"},
    "vph_pwr":  {"min": 3.5, "max": 4.3, "label": "VPH_PWR"},
    "vdd_cpu":  {"min": 0.85, "max": 1.35, "label": "VDD_CPU"},
    "vdd_mem":  {"min": 1.05, "max": 1.25, "label": "VDD_MEM"},
    "vcc_io":   {"min": 1.70, "max": 1.90, "label": "VCC_IO"},
    "emmc_vcc": {"min": 3.0, "max": 3.5, "label": "eMMC_VCC"},
    "vcc_usb":  {"min": 4.75, "max": 5.25, "label": "VCC_USB"},
}


def guess_rail_from_value(value, unit="V"):
    if unit not in ("V", ""):
        return None, None
    for k, info in EXPECTED_RAILS.items():
        if info["min"] <= value <= info["max"]:
            return k, info
    return None, None


def classify_reading(rail_key, value):
    info = EXPECTED_RAILS.get(rail_key)
    if not info or value is None:
        return {"status": "UNKNOWN", "message": "No ref"}
    if value < 0.1:
        return {"status": "CRITICAL", "message": f"{info['label']}: 0V"}
    if value < info["min"]:
        return {"status": "LOW", "message": f"{info['label']}: {value}V low"}
    if value > info["max"]:
        return {"status": "HIGH", "message": f"{info['label']}: {value}V high"}
    return {"status": "OK", "message": f"{info['label']}: {value}V OK"}


def analyze_photo_by_type(path, ptype):
    r = {"type": ptype, "path": path, "analysis": "", "reading": None, "unit": "V", "confidence": 0}
    if not path or not os.path.exists(path):
        r["analysis"] = "Photo not found"
        return r
    try:
        from core.meter_engine.ocr_reader import read_meter_photo
        ocr = read_meter_photo(path, meter_type=ptype)
        r["ocr_raw"] = ocr.get("raw_text", "")[:200]
        r["reading"] = ocr.get("value")
        r["unit"] = ocr.get("unit", "V")
        r["confidence"] = ocr.get("confidence", 0)
        r["analysis"] = f"Reading: {ocr.get('value')}V" if ocr.get("value") else "Manual needed"
    except Exception as e:
        r["analysis"] = f"Error: {str(e)[:80]}"
    return r


def deep_analyze(photo_paths, manual_values=None):
    manual_values = manual_values or {}
    started = datetime.now()
    report = {"ok": True, "photos": {}, "readings": [], "classified": [], "diagnosis": {}, "connected": False, "confidence": 0}

    for slot in ["analogue_meter", "multimeter", "dc_supply", "extra"]:
        if slot in photo_paths and photo_paths[slot]:
            report["photos"][slot] = analyze_photo_by_type(photo_paths[slot], slot)

    all_readings = []
    for slot, pdata in report["photos"].items():
        if slot == "extra":
            continue
        manual = manual_values.get(slot)
        ocr_val = pdata.get("reading")
        value = manual if manual is not None else ocr_val
        if value is not None:
            rail, info = guess_rail_from_value(value, pdata.get("unit", "V"))
            all_readings.append({
                "slot": slot, "value": value, "unit": pdata.get("unit", "V"),
                "rail": rail or "unknown", "rail_label": info["label"] if info else "Unknown",
                "source": "manual" if manual is not None else "ocr",
                "confidence": pdata.get("confidence", 0),
            })
    report["readings"] = all_readings

    classified = [{**r, **classify_reading(r["rail"], r["value"])} for r in all_readings]
    report["classified"] = classified

    critical = [c for c in classified if c["status"] == "CRITICAL"]
    warnings = [c for c in classified if c["status"] in ("LOW", "HIGH")]
    oks = [c for c in classified if c["status"] == "OK"]

    if critical:
        verdict, connected = "CRITICAL", False
    elif warnings:
        verdict, connected = "WARNING", False
    elif oks:
        verdict, connected = "OK", True
    else:
        verdict, connected = "UNKNOWN", False

    report["diagnosis"] = {
        "verdict": verdict,
        "summary": f"{len(critical)} critical, {len(warnings)} warning, {len(oks)} OK",
        "critical_count": len(critical), "warning_count": len(warnings), "ok_count": len(oks),
        "critical_items": [c["message"] for c in critical],
        "warning_items": [c["message"] for c in warnings],
    }
    report["connected"] = connected
    report["confidence"] = int((len(oks) / len(classified)) * 100) if classified else 0
    report["started_at"] = started.isoformat(timespec="seconds")
    report["finished_at"] = datetime.now().isoformat(timespec="seconds")
    report["message"] = f"{verdict} - {report['confidence']}%"
    return report
''',

    "scripts/auto_update_models.py": '''"""Auto Model Update — 15-day cycle"""
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
''',
}


def main():
    print()
    print("=" * 60)
    print("   MASTER RESTORE — Creating Missing Files")
    print("=" * 60)
    print()

    created = 0
    updated = 0

    for rel_path, content in FILES.items():
        full_path = os.path.join(ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        existed = os.path.exists(full_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        size = os.path.getsize(full_path)
        status = "Updated" if existed else "Created"
        if existed:
            updated += 1
        else:
            created += 1

        print(f"  {status}: {rel_path} ({size} bytes)")

    print()
    print("-" * 60)
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Total:   {len(FILES)}")
    print("=" * 60)

    # Verify
    print()
    print("Verifying imports...")
    print()

    sys.path.insert(0, ROOT)
    ok = 0
    fail = 0

    for rel_path in FILES.keys():
        module = rel_path.replace("/", ".").replace(".py", "")
        try:
            __import__(module)
            print(f"  OK   {module}")
            ok += 1
        except Exception as e:
            print(f"  FAIL {module} - {str(e)[:80]}")
            fail += 1

    print()
    print("=" * 60)
    print(f"  Import OK: {ok}")
    print(f"  Import FAIL: {fail}")
    print("=" * 60)

    if fail == 0:
        print()
        print("  ALL FILES RESTORED SUCCESSFULLY!")
    else:
        print()
        print(f"  {fail} file(s) still failing - check errors above")

    print()


if __name__ == "__main__":
    main()
