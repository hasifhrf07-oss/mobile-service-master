"""Deep Analyzer"""
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
