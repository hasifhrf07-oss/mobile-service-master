"""Anomaly Detector — Re-measure suggestions"""
from datetime import datetime


def detect_anomalies(validation, ocr_results):
    anomalies = []
    suggestions = []
    for slot, ocr in ocr_results.items():
        if ocr.get("confidence", 0) < 70 and ocr.get("value") is not None:
            anomalies.append({
                "type": "low_confidence", "slot": slot,
                "confidence": ocr.get("confidence"),
                "message": f"{slot}: low confidence",
            })
            suggestions.append(f"{slot} ছবি আবার তুলুন")
    for slot, ocr in ocr_results.items():
        if not ocr.get("ok") or ocr.get("value") is None:
            anomalies.append({"type": "ocr_failed", "slot": slot, "message": f"{slot}: OCR failed"})
            suggestions.append(f"{slot}: manually value লিখুন")
    for v in validation.get("validated", []):
        if v.get("severity") == "CRITICAL":
            anomalies.append({
                "type": "critical_rail", "rail": v.get("rail"),
                "value": v.get("value"),
                "message": f"{v.get('rail_label')}: {v.get('value')}V",
            })
    values = [v.get("value") for v in validation.get("validated", []) if v.get("value") is not None]
    if len(values) >= 3:
        from collections import Counter
        counts = Counter([round(x, 2) for x in values])
        for val, cnt in counts.items():
            if cnt >= 3:
                anomalies.append({"type": "duplicate_values", "value": val, "count": cnt,
                                  "message": f"{cnt} rail same value ({val}V)"})
                suggestions.append("Test point verify করুন")
    if validation.get("overall_confidence", 100) < 60:
        anomalies.append({"type": "low_overall_confidence",
                          "confidence": validation.get("overall_confidence"),
                          "message": "Overall confidence কম"})
    return {
        "anomalies": anomalies,
        "requires_remeasure": len(anomalies) > 0,
        "suggestions": list(set(suggestions)),
        "checked_at": datetime.now().isoformat(timespec="seconds"),
    }
