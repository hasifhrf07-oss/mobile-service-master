"""Accuracy Map"""
from .brand_detector import get_meter_info

def get_accuracy_margin(brand, value):
    info = get_meter_info(brand)
    acc = info.get("accuracy_pct", 5.0)
    margin = abs(value) * acc / 100
    return {"brand": brand, "accuracy_pct": acc, "value": value,
            "margin_v": round(margin, 4), "range_min": round(value-margin,4),
            "range_max": round(value+margin,4), "tier": info.get("tier","Unknown")}

def is_reading_reliable(brand, value, exp_min, exp_max):
    m = get_accuracy_margin(brand, value)
    reliable = not (m["range_max"] < exp_min or m["range_min"] > exp_max)
    return {"reliable": reliable, "value": value, "meter_brand": brand}
