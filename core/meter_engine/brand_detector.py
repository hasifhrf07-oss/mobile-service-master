"""Meter Brand Detector — Fluke / Kyoritsu / HTC / UNI-T"""

METER_BRANDS = {
    "Fluke": {
        "keywords": ["fluke", "87v", "117", "179", "f44", "fluke corp"],
        "accuracy_pct": 0.05,
        "tier": "High-Precision Industrial",
        "common_models": ["87V", "117", "179", "1587", "289"],
    },
    "Kyoritsu": {
        "keywords": ["kyoritsu", "kew", "kewtech", "kew 2"],
        "accuracy_pct": 0.30,
        "tier": "Industrial-Grade",
        "common_models": ["2000", "2200", "3005A", "4105A"],
    },
    "HTC": {
        "keywords": ["htc", "htc instrument", "htc meters"],
        "accuracy_pct": 0.50,
        "tier": "Standard Professional",
        "common_models": ["DM-97", "DM-830", "DM-2000"],
    },
    "UNI-T": {
        "keywords": ["uni-t", "unit", "ut61", "ut89", "ut-"],
        "accuracy_pct": 0.80,
        "tier": "Reliable Budget",
        "common_models": ["UT61E", "UT89X", "UT181A"],
    },
    "Analogue": {
        "keywords": ["analogue", "analog", "needle", "scale"],
        "accuracy_pct": 2.0,
        "tier": "Analog (Needle)",
        "common_models": ["Generic"],
    },
}


def detect_meter_brand(text: str) -> dict:
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


def get_meter_info(brand: str) -> dict:
    return METER_BRANDS.get(brand, {
        "accuracy_pct": 5.0,
        "tier": "Unknown",
        "common_models": [],
    })
