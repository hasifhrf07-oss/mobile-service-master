"""
Tool Token Reminder
- Track paid tool tokens (UnlockTool, Chimera, etc.)
- Remind admin before expiry
- Show purchase links
"""
import os, json
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(__file__))
TOKENS_FILE = os.path.join(ROOT, "data", "tool_tokens.json")

# Tool purchase links (affiliate-ready)
TOOL_LINKS = {
    "UnlockTool": {"url": "https://unlocktool.net/", "price": "$25/year", "type": "FRP+Flash"},
    "Chimera": {"url": "https://chimeratool.com/", "price": "$50/year", "type": "Multi-brand"},
    "GSM Flasher": {"url": "https://gsmflasher.com/", "price": "$40/year", "type": "Flash+IMEI"},
    "ZC Flash": {"url": "https://zcflashtool.com/", "price": "$30/year", "type": "MTK+Qualcomm"},
    "Odin3": {"url": "https://odindownload.com/", "price": "Free", "type": "Samsung"},
    "SP Flash Tool": {"url": "https://spflashtool.com/", "price": "Free", "type": "MTK"},
    "QFIL": {"url": "https://qpsttool.com/", "price": "Free", "type": "Qualcomm"},
    "Mi Flash Tool": {"url": "https://xiaomiflash.com/", "price": "Free", "type": "Xiaomi"},
}


def _load():
    if os.path.exists(TOKENS_FILE):
        try: return json.load(open(TOKENS_FILE, "r", encoding="utf-8"))
        except Exception: return {}
    return {}


def _save(data):
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
    json.dump(data, open(TOKENS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def add_token(tool_name, expiry_date, notes=""):
    """Add a tool token"""
    data = _load()
    data[tool_name] = {
        "tool": tool_name,
        "expiry": expiry_date,
        "notes": notes,
        "added_at": datetime.now().isoformat(timespec="seconds"),
    }
    _save(data)
    return {"ok": True, "message": f"{tool_name} token added"}


def remove_token(tool_name):
    data = _load()
    if tool_name in data:
        del data[tool_name]
        _save(data)
        return {"ok": True}
    return {"ok": False, "message": "Token not found"}


def list_tokens():
    """List all tokens with days remaining"""
    data = _load()
    result = []
    for tool, info in data.items():
        try:
            expiry = datetime.fromisoformat(info["expiry"])
            days = (expiry - datetime.now()).days
        except Exception:
            days = -999

        result.append({
            "tool": tool,
            "expiry": info["expiry"],
            "days_left": days,
            "expired": days < 0,
            "expiring_soon": 0 <= days <= 7,
            "notes": info.get("notes", ""),
            "link": TOOL_LINKS.get(tool, {}).get("url", ""),
            "price": TOOL_LINKS.get(tool, {}).get("price", ""),
        })
    return sorted(result, key=lambda x: x["days_left"])


def get_reminders():
    """Get tokens that need attention"""
    reminders = []
    for t in list_tokens():
        if t["expired"]:
            reminders.append({"level": "critical", "tool": t["tool"], "message": f"{t['tool']} expired {abs(t['days_left'])} days ago", "link": t["link"]})
        elif t["expiring_soon"]:
            reminders.append({"level": "warning", "tool": t["tool"], "message": f"{t['tool']} expires in {t['days_left']} days", "link": t["link"]})
    return reminders


def get_all_tool_links():
    return TOOL_LINKS
