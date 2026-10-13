"""Real Tools Manager"""
import os, json

ROOT = os.path.dirname(os.path.dirname(__file__))
FIRMWARE_FILE = os.path.join(ROOT, "data", "real_firmware.json")

PAID_TOOLS = {
    "UnlockTool": {"url": "https://unlocktool.net/", "price": "$25/year", "features": ["FRP bypass", "IMEI repair", "Firmware flash"]},
    "Chimera Tool": {"url": "https://chimeratool.com/", "price": "$50/year", "features": ["Samsung", "Huawei", "Qualcomm", "MTK"]},
    "GSM Flasher": {"url": "https://gsmflasher.com/", "price": "$40/year", "features": ["Firmware flash", "IMEI", "FRP"]},
    "ZC Flash Tool": {"url": "https://zcflashtool.com/", "price": "$30/year", "features": ["MTK", "Qualcomm"]},
}

FREE_TOOLS = {
    "Odin3": {"url": "https://odindownload.com/", "for": "Samsung"},
    "SP Flash Tool": {"url": "https://spflashtool.com/", "for": "MediaTek"},
    "QFIL": {"url": "https://qpsttool.com/", "for": "Qualcomm"},
    "Mi Flash Tool": {"url": "https://xiaomiflash.com/", "for": "Xiaomi"},
    "Frija Tool": {"url": "https://github.com/SlackingVeteran/frija", "for": "Samsung"},
    "Heimdall": {"url": "https://glassechidna.com.au/heimdall/", "for": "Samsung"},
    "Android Flash Tool": {"url": "https://flash.android.com/", "for": "Google"},
}


def _load():
    if os.path.exists(FIRMWARE_FILE):
        try: return json.load(open(FIRMWARE_FILE, "r", encoding="utf-8"))
        except Exception: return {}
    return {}


def list_all_brands():
    return list(_load().get("brands", {}).keys())


def get_brand_info(brand):
    for k, v in _load().get("brands", {}).items():
        if k.lower() == brand.lower():
            return {"ok": True, "brand": k, **v}
    return {"ok": False, "message": f"{brand} not found"}


def get_flash_guide(brand, model=""):
    info = get_brand_info(brand)
    if not info.get("ok"): return info
    return {"ok": True, "brand": info["brand"], "model": model,
            "firmware_sources": info.get("firmware_sources", []),
            "flash_tools": info.get("flash_tools", []),
            "common_issues": info.get("common_issues", [])}


def get_free_tools(): return FREE_TOOLS
def get_paid_tools(): return PAID_TOOLS


def get_tools_for_brand(brand):
    info = get_brand_info(brand)
    if not info.get("ok"): return info
    free = [{"name": k, **FREE_TOOLS[k]} for k in FREE_TOOLS if FREE_TOOLS[k].get("for", "").lower() in brand.lower()]
    paid = [{"name": k, **PAID_TOOLS[k]} for k in PAID_TOOLS]
    return {"ok": True, "brand": info["brand"], "free_tools": free, "paid_tools": paid}


def get_full_service_guide(brand, model, issue_type="boot_loop"):
    guide = get_flash_guide(brand, model)
    if not guide.get("ok"): return guide
    recs = {
        "boot_loop": ["Recovery → Wipe Cache", "Factory Reset", "Reflash firmware"],
        "dead_boot": ["Check battery 3.7V", "Try EDL/BROM", "Flash stock ROM"],
        "frp_lock": ["Owner verification", "Use UnlockTool (paid)", "Service center"],
        "pattern_lock": ["Find My Device", "Factory Reset"],
    }.get(issue_type, ["Diagnosis needed"])
    return {"ok": True, "brand": guide["brand"], "model": model, "issue_type": issue_type,
            "recommendations": recs, "firmware_sources": guide["firmware_sources"],
            "flash_tools": guide["flash_tools"]}


if __name__ == "__main__":
    print("Brands:", len(list_all_brands()))
    print("Free tools:", len(get_free_tools()))
    print("Paid tools:", len(get_paid_tools()))
