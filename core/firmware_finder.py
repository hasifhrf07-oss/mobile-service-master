"""Firmware Finder — Official sources by brand"""
FIRMWARE_SOURCES = {
    "Samsung": {"official": "https://www.samsung.com/support/", "firmware": "https://www.sammobile.com/firmwares/", "tool": "Odin3"},
    "Xiaomi": {"official": "https://www.mi.com/global/support/", "firmware": "https://xiaomifirmwareupdater.com/", "tool": "Mi Flash Tool"},
    "Oppo": {"official": "https://www.oppo.com/en/support/", "firmware": "https://oppofirmware.com/", "tool": "MSM Download Tool"},
    "Vivo": {"official": "https://www.vivo.com/en/support/", "firmware": "https://vivofirmware.com/", "tool": "AFTool"},
    "Realme": {"official": "https://www.realme.com/in/support", "firmware": "https://realmeupdater.com/", "tool": "Realme Flash Tool"},
    "OnePlus": {"official": "https://www.oneplus.com/support", "firmware": "https://oxygenos.oneplus.net/", "tool": "MSM Download Tool"},
    "Google Pixel": {"official": "https://developers.google.com/android/images", "firmware": "https://developers.google.com/android/images", "tool": "Android Flash Tool"},
    "Huawei": {"official": "https://consumer.huawei.com/en/support/", "firmware": "https://consumer.huawei.com/en/support/hisuite/", "tool": "HiSuite"},
    "Infinix": {"official": "https://www.infinixmobility.com/support/", "firmware": "https://infinixfirmware.com/", "tool": "SP Flash Tool"},
    "Tecno": {"official": "https://www.tecno-mobile.com/support/", "firmware": "https://tecnofirmware.com/", "tool": "SP Flash Tool"},
    "itel": {"official": "https://www.itel-mobile.com/support/", "firmware": "https://itelfirmware.com/", "tool": "SP Flash Tool"},
    "Symphony": {"official": "https://www.symphony-mobile.com/", "firmware": "https://symphony-mobile.com/service-center/", "tool": "SP Flash Tool"},
    "Walton": {"official": "https://waltonbd.com/", "firmware": "https://waltonbd.com/service-center/", "tool": "SP Flash Tool"},
    "Nokia": {"official": "https://www.nokia.com/phones/en_int/support", "firmware": "https://www.nokia.com/phones/en_int/support", "tool": "Recovery Tool"},
    "Motorola": {"official": "https://www.motorola.com/we/rescue-and-smart-assistant", "firmware": "https://www.motorola.com/we/rescue-and-smart-assistant", "tool": "RSA"},
    "Sony": {"official": "https://www.sony.com/electronics/support", "firmware": "https://www.sony.com/electronics/support", "tool": "Xperia Companion"},
    "Asus": {"official": "https://www.asus.com/support/", "firmware": "https://www.asus.com/support/", "tool": "ASUS Flash Tool"},
}


def get_firmware_info(brand, model):
    for k, v in FIRMWARE_SOURCES.items():
        if k.lower() == brand.lower():
            return {"ok": True, "brand": k, "model": model, **v}
    return {"ok": False, "message": f"{brand} not found"}


def get_all_brands():
    return list(FIRMWARE_SOURCES.keys())


def get_download_steps(brand, model, mode="fastboot"):
    steps = {
        "samsung": ["Download firmware from SamMobile", "Extract → .tar.md5", "Open Odin3", "Phone → Download Mode", "Load BL/AP/CP/CSC", "Click Start"],
        "xiaomi": ["Download Fastboot ROM", "Extract .tgz", "Install Mi Flash Tool", "Phone → Fastboot", "Select folder → Refresh", "Click Flash"],
        "mtk": ["Download firmware", "Open SP Flash Tool", "Load scatter file", "Click Download", "Connect phone (BROM)", "Wait for green circle"],
        "qualcomm": ["Download firmware", "Open QFIL", "Load programmer", "Load rawprogram/patch", "Phone → EDL", "Click Download"],
    }
    k = "samsung" if "samsung" in brand.lower() else ("xiaomi" if "xiaomi" in brand.lower() else ("mtk" if "mtk" in mode.lower() else "qualcomm"))
    return {"ok": True, "brand": brand, "model": model, "steps": steps.get(k, [])}
