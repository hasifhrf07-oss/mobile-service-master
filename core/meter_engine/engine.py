"""Meter Engine — Main orchestrator"""
from datetime import datetime
from .brand_detector import detect_meter_brand, get_meter_info
from .ocr_reader import read_meter_photo
from .cross_validator import cross_validate_readings
from .anomaly_detector import detect_anomalies

def analyze_meter_photos(photo_paths, manual_values=None):
    manual_values = manual_values or {}
    started = datetime.now().isoformat(timespec="seconds")
    ocr_results = {}
    combined = ""
    for slot, path in photo_paths.items():
        if not path: continue
        ocr = read_meter_photo(path, slot)
        ocr_results[slot] = ocr
        combined += " " + ocr.get("raw_text", "")
    brand_info = detect_meter_brand(combined)
    readings = []
    for slot, ocr in ocr_results.items():
        v = manual_values.get(slot, ocr.get("value"))
        if v is not None:
            readings.append({"slot": slot, "value": v, "unit": ocr.get("unit", "V"),
                            "source": "manual" if slot in manual_values else "ocr",
                            "confidence": ocr.get("confidence", 0)})
    validation = cross_validate_readings(readings, brand_info["brand"])
    anomalies = detect_anomalies(validation, ocr_results)
    validated = validation.get("validated", [])
    critical = [v for v in validated if v.get("severity") == "CRITICAL"]
    ok = [v for v in validated if v.get("severity") == "OK"]
    if critical:
        verdict, summary = "CRITICAL", f"{len(critical)} critical rail(s)"
    elif ok:
        verdict, summary = "OK", f"All {len(ok)} rails normal"
    else:
        verdict, summary = "UNKNOWN", "No readings"
    return {"ok": True, "brand": brand_info["brand"], "brand_confidence": brand_info["confidence"],
            "readings": validated, "overall_confidence": validation.get("overall_confidence", 0),
            "anomalies": anomalies["anomalies"], "requires_remeasure": anomalies["requires_remeasure"],
            "suggestions": anomalies["suggestions"],
            "diagnosis": {"verdict": verdict, "summary": summary},
            "job_started_at": started, "job_finished_at": datetime.now().isoformat(timespec="seconds")}
