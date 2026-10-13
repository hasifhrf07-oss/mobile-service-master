"""Cross Validator"""
from datetime import datetime
from .accuracy_map import is_reading_reliable
from .rail_extractor import extract_rail_from_reading, _get_rails

def cross_validate_readings(readings, meter_brand="Unknown"):
    validated = []
    warnings = []
    scores = []
    rails = _get_rails()
    for r in readings:
        v = r.get("value")
        if v is None:
            validated.append({**r, "valid": False})
            continue
        rail = extract_rail_from_reading(v, r.get("unit", "V"))
        if not rail.get("rail"):
            validated.append({**r, "valid": False})
            continue
        info = rails.get(rail["rail"], {})
        sev = "CRITICAL" if v < 0.1 else ("LOW" if v < info.get("min", 0) else ("HIGH" if v > info.get("max", 10) else "OK"))
        validated.append({**r, "valid": True, "rail": rail["rail"],
                         "rail_label": rail.get("label"), "severity": sev})
        scores.append(1 if sev == "OK" else 0.5)
    overall = int(sum(scores)/len(scores)*100) if scores else 0
    return {"ok": True, "validated": validated, "warnings": warnings,
            "overall_confidence": overall, "total_readings": len(readings),
            "validated_at": datetime.now().isoformat(timespec="seconds")}
