"""Rail Extractor"""
DEFAULT_RAILS = {
    "vbat": {"label": "VBAT (Battery)", "min": 3.5, "max": 4.3, "typical": 3.8, "priority": 1},
    "vph_pwr": {"label": "VPH_PWR", "min": 3.5, "max": 4.3, "typical": 3.75, "priority": 2},
    "vdd_cpu": {"label": "VDD_CPU", "min": 0.85, "max": 1.35, "typical": 1.10, "priority": 3},
    "vdd_mem": {"label": "VDD_MEM", "min": 1.05, "max": 1.25, "typical": 1.12, "priority": 4},
    "vcc_io": {"label": "VCC_IO", "min": 1.70, "max": 1.90, "typical": 1.80, "priority": 5},
    "emmc_vcc": {"label": "eMMC VCC", "min": 3.0, "max": 3.5, "typical": 3.3, "priority": 6},
    "vcc_usb": {"label": "VCC_USB", "min": 4.75, "max": 5.25, "typical": 5.0, "priority": 7},
}

def _get_rails():
    try:
        from core.multimeter.rail_database import COMMON_RAILS
        return COMMON_RAILS
    except:
        return DEFAULT_RAILS

def extract_rail_from_reading(value, unit="V", meter_type="multimeter"):
    if value is None:
        return {"ok": False, "error": "No value"}
    if unit in ("mA", "A"):
        return {"ok": True, "rail": "current_draw", "type": "current", "value": value, "unit": unit}
    rails = _get_rails()
    matches = []
    for k, info in rails.items():
        if info["min"] <= value <= info["max"]:
            matches.append({"rail": k, "label": info["label"], "priority": info.get("priority", 999)})
    matches.sort(key=lambda x: x["priority"])
    if not matches:
        return {"ok": True, "rail": None, "message": f"{value}V unknown"}
    return {"ok": True, "rail": matches[0]["rail"], "label": matches[0]["label"]}
