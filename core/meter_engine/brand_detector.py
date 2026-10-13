"""Meter Brand Detector"""
METER_BRANDS = {
    "Fluke": {"keywords": ["fluke", "87v", "117", "179"], "accuracy_pct": 0.05, "tier": "High-Precision"},
    "Kyoritsu": {"keywords": ["kyoritsu", "kew"], "accuracy_pct": 0.30, "tier": "Industrial-Grade"},
    "HTC": {"keywords": ["htc"], "accuracy_pct": 0.50, "tier": "Standard"},
    "UNI-T": {"keywords": ["uni-t", "unit", "ut61"], "accuracy_pct": 0.80, "tier": "Budget"},
}

def detect_meter_brand(text):
    if not text:
        return {"brand": "Unknown", "confidence": 0, "matched_keyword": ""}
    t = text.lower()
    best = {"brand": "Unknown", "confidence": 0, "matched_keyword": ""}
    for brand, info in METER_BRANDS.items():
        for kw in info["keywords"]:
            if kw in t:
                conf = min(95, 60 + len(kw) * 5)
                if conf > best["confidence"]:
                    best = {"brand": brand, "confidence": conf, "matched_keyword": kw}
    return best

def get_meter_info(brand):
    return METER_BRANDS.get(brand, {"accuracy_pct": 5.0, "tier": "Unknown"})
