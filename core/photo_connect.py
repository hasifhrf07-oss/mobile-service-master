"""Photo Connect Engine"""
import os
from datetime import datetime

EXPECTED_RAILS = {
    "vbat":     {"min": 3.5, "max": 4.3, "typical": 3.8, "label": "VBAT"},
    "vph_pwr":  {"min": 3.5, "max": 4.3, "typical": 3.75, "label": "VPH_PWR"},
    "vdd_cpu":  {"min": 0.85, "max": 1.35, "typical": 1.10, "label": "VDD_CPU"},
    "vdd_mem":  {"min": 1.05, "max": 1.25, "typical": 1.12, "label": "VDD_MEM"},
    "vcc_io":   {"min": 1.70, "max": 1.90, "typical": 1.80, "label": "VCC_IO"},
    "emmc_vcc": {"min": 3.0, "max": 3.5, "typical": 3.3, "label": "eMMC_VCC"},
    "vcc_usb":  {"min": 4.75, "max": 5.25, "typical": 5.0, "label": "VCC_USB"},
}


def get_connect_status():
    return {
        "enabled": True,
        "method": "OCR + Database Matching",
        "confidence_threshold": 80,
        "supported_photos": ["analogue_meter", "multimeter", "dc_supply", "extra"],
        "chipsets": ["exynos", "snapdragon", "mediatek", "generic"],
    }


def detect_chipset_from_text(text):
    t = (text or "").lower()
    if any(k in t for k in ["exynos", "samsung"]):
        return "exynos"
    if any(k in t for k in ["snapdragon", "qualcomm", "sdm"]):
        return "snapdragon"
    if any(k in t for k in ["mediatek", "mtk", "helio", "dimensity"]):
        return "mediatek"
    return "generic"


def photo_connect(photo_paths, brand_text=""):
    started = datetime.now()

    try:
        from core.meter_engine.engine import analyze_meter_photos
        analysis = analyze_meter_photos(photo_paths)
    except Exception:
        analysis = {"ok": True, "readings": []}

    readings = analysis.get("readings", [])
    if isinstance(readings, dict):
        readings = list(readings.values())

    chipset = detect_chipset_from_text(brand_text or analysis.get("brand", ""))

    matches, mismatches = [], []
    for r in readings:
        if not isinstance(r, dict):
            continue
        rail = (r.get("rail") or "").lower()
        v = r.get("value")
        if not rail or v is None:
            continue
        if rail in EXPECTED_RAILS:
            info = EXPECTED_RAILS[rail]
            if info["min"] <= v <= info["max"]:
                matches.append({"rail": rail, "value": v, "status": "match"})
            else:
                mismatches.append({"rail": rail, "value": v, "status": "mismatch"})

    total = len(matches) + len(mismatches)
    score = int((len(matches) / total) * 100) if total else 0
    status = "CONNECTED" if score >= 80 else ("PARTIAL" if score >= 50 else "FAILED")

    return {
        "ok": True,
        "connected": score >= 80,
        "status": status,
        "confidence": score,
        "chipset": chipset,
        "matches": matches,
        "mismatches": mismatches,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "message": f"{'OK' if score >= 80 else status} ({score}%)",
    }
