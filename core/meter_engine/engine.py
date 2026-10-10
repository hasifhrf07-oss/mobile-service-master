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
    combined_text = ""
    for slot, path in photo_paths.items():
        if not path:
            continue
        ocr = read_meter_photo(path, meter_type=slot)
        ocr_results[slot] = ocr
        combined_text += " " + ocr.get("raw_text", "")
    brand_info = detect_meter_brand(combined_text)
    meter_brand = brand_info["brand"]
    readings = []
    for slot, ocr in ocr_results.items():
        value = manual_values.get(slot, ocr.get("value"))
        unit = ocr.get("unit", "V")
        if value is not None:
            readings.append({
                "slot": slot, "value": value, "unit": unit,
                "source": "manual" if slot in manual_values else "ocr",
                "confidence": ocr.get("confidence", 0),
            })
    validation = cross_validate_readings(readings, meter_brand)
    anomalies = detect_anomalies(validation, ocr_results)
    diagnosis = _build_diagnosis(validation, meter_brand, anomalies)
    return {
        "ok": True, "job_started_at": started,
        "job_finished_at": datetime.now().isoformat(timespec="seconds"),
        "brand": meter_brand, "brand_confidence": brand_info["confidence"],
        "brand_tier": get_meter_info(meter_brand).get("tier", "Unknown"),
        "accuracy_pct": get_meter_info(meter_brand).get("accuracy_pct", 5.0),
        "ocr_results": ocr_results,
        "readings": validation.get("validated", []),
        "overall_confidence": validation.get("overall_confidence", 0),
        "anomalies": anomalies.get("anomalies", []),
        "requires_remeasure": anomalies.get("requires_remeasure", False),
        "suggestions": anomalies.get("suggestions", []),
        "diagnosis": diagnosis,
        "extra_text": combined_text[:2000],
    }


def _build_diagnosis(validation, meter_brand, anomalies):
    validated = validation.get("validated", [])
    critical = [v for v in validated if v.get("severity") == "CRITICAL"]
    low = [v for v in validated if v.get("severity") == "LOW"]
    high = [v for v in validated if v.get("severity") == "HIGH"]
    ok = [v for v in validated if v.get("severity") == "OK"]
    if critical:
        verdict = "CRITICAL"
        summary = f"{len(critical)} rail critical"
    elif low or high:
        verdict = "WARNING"
        summary = f"{len(low)} low, {len(high)} high"
    elif ok:
        verdict = "OK"
        summary = f"All {len(ok)} rails normal"
    else:
        verdict = "UNKNOWN"
        summary = "No readings"
    return {
        "verdict": verdict, "summary": summary,
        "critical_count": len(critical),
        "warning_count": len(low) + len(high),
        "ok_count": len(ok),
        "critical_rails": [{"rail": v.get("rail"), "value": v.get("value")} for v in critical],
        "meter_brand": meter_brand,
    }
