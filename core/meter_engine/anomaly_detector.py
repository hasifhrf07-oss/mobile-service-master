"""Anomaly Detector"""
from datetime import datetime

def detect_anomalies(validation, ocr_results):
    anomalies = []
    suggestions = []
    for slot, ocr in ocr_results.items():
        if ocr.get("confidence", 0) < 70 and ocr.get("value") is not None:
            anomalies.append({"type": "low_confidence", "slot": slot, "message": f"{slot} low confidence"})
            suggestions.append(f"{slot} ছবি আবার তুলুন")
        if not ocr.get("ok") or ocr.get("value") is None:
            anomalies.append({"type": "ocr_failed", "slot": slot})
            suggestions.append(f"{slot} manually value লিখুন")
    for v in validation.get("validated", []):
        if v.get("severity") == "CRITICAL":
            anomalies.append({"type": "critical", "rail": v.get("rail")})
    return {"anomalies": anomalies, "requires_remeasure": len(anomalies) > 0,
            "suggestions": list(set(suggestions)),
            "checked_at": datetime.now().isoformat(timespec="seconds")}
