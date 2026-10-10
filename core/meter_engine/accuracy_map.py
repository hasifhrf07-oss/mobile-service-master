"""Accuracy Map — Brand-wise meter error margins"""
from .brand_detector import get_meter_info


def get_accuracy_margin(brand, value):
    info = get_meter_info(brand)
    accuracy_pct = info.get("accuracy_pct", 5.0)
    margin_v = abs(value) * accuracy_pct / 100
    return {
        "brand": brand, "accuracy_pct": accuracy_pct, "value": value,
        "margin_v": round(margin_v, 4),
        "range_min": round(value - margin_v, 4),
        "range_max": round(value + margin_v, 4),
        "tier": info.get("tier", "Unknown"),
    }


def is_reading_reliable(brand, value, expected_min, expected_max):
    margin = get_accuracy_margin(brand, value)
    effective_min = margin["range_min"]
    effective_max = margin["range_max"]
    reliable = not (effective_max < expected_min or effective_min > expected_max)
    return {
        "reliable": reliable, "value": value,
        "reading_range": [effective_min, effective_max],
        "expected_range": [expected_min, expected_max],
        "meter_brand": brand,
        "accuracy_pct": margin["accuracy_pct"],
    }
