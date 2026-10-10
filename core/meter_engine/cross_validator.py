"""Cross Validator — Multi-layer validation"""
from datetime import datetime
from .accuracy_map import is_reading_reliable
from .rail_extractor import extract_rail_from_reading, _get_rails


def cross_validate_readings(readings, meter_brand="Unknown"):
    validated = []
    warnings = []
    layer_scores = []
    rails = _get_rails()
    for r in readings:
        value = r.get("value")
        unit = r.get("unit", "V")
        if value is None:
            validated.append({**r, "valid": False, "reason": "No value"})
            continue
        rail = extract_rail_from_reading(value, unit, r.get("meter_type"))
        if not rail.get("rail"):
            validated.append({**r, "valid": False, "reason": "No matching rail", "rail_info": rail})
            warnings.append(f"{value}{unit} unknown rail")
            continue
        rail_info = rails.get(rail["rail"])
        if rail_info:
            acc = is_reading_reliable(meter_brand, value, rail_info["min"], rail_info["max"])
        else:
            acc = {"reliable": True, "accuracy_pct": 5.0}
        severity = _severity(value, rail_info)
        validated.append({
            **r, "valid": True, "rail": rail["rail"],
            "rail_label": rail.get("label"),
            "expected_range": rail.get("expected"),
            "typical": rail.get("typical"),
            "accuracy": acc, "severity": severity,
        })
        layer_scores.append(1 if severity == "OK" else 0.5)
    overall_conf = int(sum(layer_scores) / len(layer_scores) * 100) if layer_scores else 0
    return {
        "ok": True, "validated": validated, "warnings": warnings,
        "overall_confidence": overall_conf,
        "total_readings": len(readings),
        "valid_readings": sum(1 for v in validated if v.get("valid")),
        "validated_at": datetime.now().isoformat(timespec="seconds"),
    }


def _severity(value, rail_info):
    if not rail_info:
        return "UNKNOWN"
    if value < 0.1:
        return "CRITICAL"
    if value < rail_info["min"]:
        return "LOW"
    if value > rail_info["max"]:
        return "HIGH"
    return "OK"
