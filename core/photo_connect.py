"""Photo Connect Engine — Photo → Analysis → Connection Status"""
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
    """Photo connect feature status"""
    return {
        "enabled": True,
        "method": "OCR + Database Matching",
        "confidence_threshold": 80,
        "supported_photos": ["analogue_meter", "multimeter", "dc_supply", "extra"],
        "chipsets": ["exynos", "snapdragon", "mediatek", "generic"],
    }


def extract_readings_from_photos(photo_paths):
    """Extract readings from 4 photos"""
    try:
        from core.meter_engine.engine import analyze_meter_photos
        analysis = analyze_meter_photos(photo_paths)
        return analysis
    except ImportError:
        return {"ok": True, "readings": list(photo_paths.keys())}


def detect_chipset_from_text(text):
    """Detect chipset family"""
    t = (text or "").lower()
    if any(k in t for k in ["exynos", "samsung"]):
        return "exynos"
    if any(k in t for k in ["snapdragon", "qualcomm", "sdm"]):
        return "snapdragon"
    if any(k in t for k in ["mediatek", "mtk", "helio", "dimensity"]):
        return "mediatek"
    return "generic"


def photo_connect(photo_paths, brand_text=""):
    """
    Main photo-connect function.
    Returns connected status + confidence + matches
    """
    started = datetime.now()

    # Analyze photos
    analysis = extract_readings_from_photos(photo_paths)

    # Extract readings
    readings = analysis.get("readings", [])
    if isinstance(readings, dict):
        readings = [v for v in readings.values() if isinstance(v, dict)]

    # Detect chipset
    chipset = detect_chipset_from_text(brand_text)
    if chipset == "generic":
        brand = analysis.get("brand", "")
        chipset = detect_chipset_from_text(brand)

    # Match readings
    matches = []
    mismatches = []
    for r in readings:
        rail = (r.get("rail") or "").lower()
        v = r.get("value")
        if not rail or v is None:
            continue
        if rail in EXPECTED_RAILS:
            info = EXPECTED_RAILS[rail]
            if info["min"] <= v <= info["max"]:
                matches.append({"rail": rail, "value": v, "expected": f"{info['min']}-{info['max']}V", "status": "match"})
            else:
                mismatches.append({"rail": rail, "value": v, "expected": f"{info['min']}-{info['max']}V", "status": "mismatch"})

    total = len(matches) + len(mismatches)
    score = int((len(matches) / total) * 100) if total else 0

    if score >= 80:
        status, connected = "CONNECTED", True
    elif score >= 50:
        status, connected = "PARTIAL", False
    else:
        status, connected = "FAILED", False

    return {
        "ok": True,
        "connected": connected,
        "status": status,
        "confidence": score,
        "chipset": chipset,
        "matches": matches,
        "mismatches": mismatches,
        "raw_analysis": analysis,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "message": f"{'✅ Connected' if connected else '⚠️ ' + status} (Confidence: {score}%)",
    }
