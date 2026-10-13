"""Deep Analyzer — Full 4-photo analysis with diagnosis"""
import os
from datetime import datetime


EXPECTED_RAILS = {
    "vbat":     {"min": 3.5, "max": 4.3, "typical": 3.8, "label": "VBAT (Battery)"},
    "vph_pwr":  {"min": 3.5, "max": 4.3, "typical": 3.75, "label": "VPH_PWR"},
    "vdd_cpu":  {"min": 0.85, "max": 1.35, "typical": 1.10, "label": "VDD_CPU"},
    "vdd_mem":  {"min": 1.05, "max": 1.25, "typical": 1.12, "label": "VDD_MEM"},
    "vcc_io":   {"min": 1.70, "max": 1.90, "typical": 1.80, "label": "VCC_IO"},
    "emmc_vcc": {"min": 3.0, "max": 3.5, "typical": 3.3, "label": "eMMC VCC"},
    "vcc_usb":  {"min": 4.75, "max": 5.25, "typical": 5.0, "label": "VCC_USB"},
}


def guess_rail_from_value(value, unit="V"):
    """Guess which rail a value belongs to"""
    if unit not in ("V", ""):
        return None, None
    for rail_key, info in EXPECTED_RAILS.items():
        if info["min"] <= value <= info["max"]:
            return rail_key, info
    return None, None


def classify_reading(rail_key, value):
    """Classify one reading"""
    info = EXPECTED_RAILS.get(rail_key)
    if not info or value is None:
        return {"status": "UNKNOWN", "message": "No reference"}
    vmin, vmax = info["min"], info["max"]
    if value < 0.1:
        return {"status": "CRITICAL", "message": f"❌ {info['label']}: 0V — Dead rail"}
    if value < vmin:
        return {"status": "LOW", "message": f"⚠️ {info['label']}: {value}V — Low"}
    if value > vmax:
        return {"status": "HIGH", "message": f"⚠️ {info['label']}: {value}V — High"}
    return {"status": "OK", "message": f"✅ {info['label']}: {value}V — Normal"}


def analyze_photo_by_type(photo_path, photo_type):
    """Analyze a single photo"""
    result = {
        "type": photo_type,
        "path": photo_path,
        "analysis": "",
        "reading": None,
        "unit": "V",
        "confidence": 0,
    }
    if not photo_path or not os.path.exists(photo_path):
        result["analysis"] = "❌ ছবি পাওয়া যায়নি"
        return result
    try:
        from core.meter_engine.ocr_reader import read_meter_photo
        ocr = read_meter_photo(photo_path, meter_type=photo_type)
        result["ocr_raw"] = ocr.get("raw_text", "")[:200]
        result["reading"] = ocr.get("value")
        result["unit"] = ocr.get("unit", "V")
        result["confidence"] = ocr.get("confidence", 0)
        if ocr.get("value") is not None:
            result["analysis"] = f"📊 Reading: {ocr['value']}{ocr.get('unit', 'V')} ({ocr['confidence']}%)"
        else:
            result["analysis"] = "⚠️ Manual reading needed"
    except Exception as e:
        result["analysis"] = f"❌ Error: {str(e)[:80]}"
    return result


def deep_analyze(photo_paths, manual_values=None):
    """
    Full deep analysis of 4 photos.
    Returns complete report with diagnosis.
    """
    manual_values = manual_values or {}
    started = datetime.now()

    report = {
        "ok": True,
        "started_at": started.isoformat(timespec="seconds"),
        "photos": {},
        "readings": [],
        "classified": [],
        "diagnosis": {},
        "connected": False,
        "confidence": 0,
    }

    # Analyze each photo
    for slot in ["analogue_meter", "multimeter", "dc_supply", "extra"]:
        if slot in photo_paths and photo_paths[slot]:
            report["photos"][slot] = analyze_photo_by_type(photo_paths[slot], slot)

    # Collect readings
    all_readings = []
    for slot, photo_data in report["photos"].items():
        if slot == "extra":
            continue
        manual = manual_values.get(slot)
        ocr_value = photo_data.get("reading")
        value = manual if manual is not None else ocr_value
        unit = photo_data.get("unit", "V")
        if value is not None:
            rail_key, rail_info = guess_rail_from_value(value, unit)
            all_readings.append({
                "slot": slot,
                "value": value,
                "unit": unit,
                "rail": rail_key or "unknown",
                "rail_label": rail_info["label"] if rail_info else "Unknown",
                "source": "manual" if manual is not None else "ocr",
                "confidence": photo_data.get("confidence", 0),
            })

    report["readings"] = all_readings

    # Classify
    classified = []
    for r in all_readings:
        cls = classify_reading(r["rail"], r["value"])
        classified.append({**r, **cls})
    report["classified"] = classified

    # Diagnosis
    critical = [c for c in classified if c["status"] == "CRITICAL"]
    warnings = [c for c in classified if c["status"] in ("LOW", "HIGH")]
    oks = [c for c in classified if c["status"] == "OK"]

    if critical:
        verdict, summary, connected = "CRITICAL", f"{len(critical)} critical rail(s) — hardware fault", False
    elif warnings:
        verdict, summary, connected = "WARNING", f"{len(warnings)} rail(s) deviate", False
    elif oks:
        verdict, summary, connected = "OK", f"All {len(oks)} rails normal", True
    else:
        verdict, summary, connected = "UNKNOWN", "No readings to analyze", False

    report["diagnosis"] = {
        "verdict": verdict,
        "summary": summary,
        "critical_count": len(critical),
        "warning_count": len(warnings),
        "ok_count": len(oks),
        "critical_items": [c["message"] for c in critical],
        "warning_items": [c["message"] for c in warnings],
    }

    report["connected"] = connected
    report["confidence"] = int((len(oks) / len(classified)) * 100) if classified else 0
    report["finished_at"] = datetime.now().isoformat(timespec="seconds")

    if connected:
        report["message"] = f"✅ MOBILE CONNECTED — {report['confidence']}% confidence"
    elif critical:
        report["message"] = f"❌ HARDWARE FAULT — {len(critical)} critical rail(s)"
    else:
        report["message"] = f"⚠️ ANALYSIS COMPLETE — {report['confidence']}% confidence"

    return report
