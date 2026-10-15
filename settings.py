PAID_TOOLS = {
    "unlocktool": {"name": "UnlockTool", "api_key": "", "api_url": "https://api.unlocktool.net/v1/", "enabled": False, "description": "Samsung, Xiaomi, Oppo, Vivo unlock"},
    "chimera": {"name": "Chimera Tool", "api_key": "", "api_url": "https://api.chimeratool.com/v1/", "enabled": False, "description": "iOS, Android unlock & flash"},
    "dftpro": {"name": "DFT Pro", "api_key": "", "api_url": "https://api.dftpro.com/v1/", "enabled": False, "description": "Qualcomm, MTK flash"},
    "atf": {"name": "ATF Box", "api_key": "", "api_url": "https://api.atfbox.com/v1/", "enabled": False, "description": "Nokia, Samsung unlock"},
    "medusa": {"name": "Medusa Box", "api_key": "", "api_url": "https://api.medusabox.com/v1/", "enabled": False, "description": "JTAG, eMMC repair"}
}

def add_api_key(tool_name, api_key):
    if tool_name in PAID_TOOLS:
        PAID_TOOLS[tool_name]["api_key"] = api_key
        PAID_TOOLS[tool_name]["enabled"] = True
        return True
    return False

def get_api_key(tool_name):
    if tool_name in PAID_TOOLS:
        return PAID_TOOLS[tool_name]["api_key"]
    return None

def is_tool_enabled(tool_name):
    if tool_name in PAID_TOOLS:
        return PAID_TOOLS[tool_name]["enabled"]
    return False
