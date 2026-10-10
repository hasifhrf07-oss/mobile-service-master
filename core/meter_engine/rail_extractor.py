"""Rail Extractor — Reading value থেকে rail guess"""

DEFAULT_RAILS = {
    "vbat": {"label": "VBAT (Battery)", "min": 3.5, "max": 4.3, "typical": 3.8, "priority": 1},
    "vph_pwr": {"label": "VPH_PWR (PMIC)", "min": 3.5, "max": 4.3, "typical": 3.75, "priority": 2},
    "vdd_cpu": {"label": "VDD_CPU (CPU)", "min": 0.85, "max": 1.35, "typical": 1.10, "priority": 3},
    "vdd_mem": {"label": "VDD_MEM (RAM)", "min": 1.05, "max": 1.25, "typical": 1.12, "priority": 4},
    "vcc_io": {"label": "VCC_IO (I/O)", "min": 1.70, "max": 1.90, "typical": 1.80, "priority": 5},
    "emmc_vcc": {"label": "eMMC VCC", "min": 3.0, "max": 3.5, "typical": 3.3, "priority": 6},
    "vcc_usb": {"label": "VCC_USB (VBUS)", "min": 4.75, "max": 5.25, "typical": 5.0, "priority": 7},
    "vdd_gpu": {"label": "VDD_GPU", "min": 0.7, "max": 1.0, "typical": 0.85, "priority": 10},
}


def _get_rails():
    try:
        from core.multimeter.rail_database import COMMON_RAILS
        return COMMON_RAILS
    except Exception:
        return DEFAULT_RAILS


def extract_rail_from_reading(value, unit="V", meter_type="multimeter"):
    if value is None:
        return {"ok": False, "error": "No value"}
    if unit in ("mA", "A"):
        return {"ok": True, "rail": "current_draw", "type": "current", "value": value, "unit": unit}
    rails = _get_rails()
    matches = []
    for rail_key, info in rails.items():
        if info["min"] <= value <= info["max"]:
            matches.append({
                "rail": rail_key, "label": info["label"],
                "expected": f"{info['min']}-{info['max']}V",
                "typical": info.get("typical"),
                "priority": info.get("priority", 999),
            })
    matches.sort(key=lambda x: x["priority"])
    if not matches:
        return {"ok": True, "rail": None, "message": f"{value}V unknown rail", "matches": []}
    return {
        "ok": True, "rail": matches[0]["rail"], "label": matches[0]["label"],
        "expected": matches[0]["expected"], "typical": matches[0]["typical"],
        "alternatives": matches[1:4],
    }
