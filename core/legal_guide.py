"""Legal Usage Guide — What's allowed, what's not"""

LEGAL_DO = [
    {"task": "Firmware flash (own device)", "ok": True, "why": "Device owner consent"},
    {"task": "Firmware flash (customer consent)", "ok": True, "why": "Customer authorized"},
    {"task": "Diagnosis via ADB", "ok": True, "why": "Owner enabled USB debugging"},
    {"task": "Report generation", "ok": True, "why": "Documentation"},
    {"task": "Battery replacement", "ok": True, "why": "Hardware repair"},
    {"task": "Screen replacement", "ok": True, "why": "Hardware repair"},
    {"task": "Software reset (with consent)", "ok": True, "why": "Owner authorized"},
]

LEGAL_DONT = [
    {"task": "FRP bypass without owner proof", "ok": False, "why": "Unauthorized access — illegal in 100+ countries", "alternative": "Ask for Google account credentials"},
    {"task": "iCloud unlock", "ok": False, "why": "Felony in US/EU", "alternative": "Original owner via Apple Support"},
    {"task": "IMEI change", "ok": False, "why": "Fraud in most countries", "alternative": "None — illegal"},
    {"task": "Network unlock without carrier", "ok": False, "why": "Contract violation", "alternative": "Carrier unlock request"},
    {"task": "Stolen phone repair", "ok": False, "why": "Criminal offense", "alternative": "Report to police"},
    {"task": "Data extraction without consent", "ok": False, "why": "Privacy violation", "alternative": "Get written consent"},
]

RISK_ZONES = {
    "green": "Safe — Legal everywhere",
    "yellow": "Caution — Legal with consent",
    "red": "Danger — Illegal — Jail risk",
}


def get_allowed_tasks():
    return LEGAL_DO


def get_forbidden_tasks():
    return LEGAL_DONT


def check_task(task_query):
    """Check if a task is legal"""
    t = task_query.lower()
    for task in LEGAL_DONT:
        if any(k in t for k in task["task"].lower().split()):
            return {"ok": False, "reason": task["why"], "alternative": task["alternative"]}
    return {"ok": True, "message": "Legal — proceed"}


def get_legal_summary():
    return {
        "allowed": len(LEGAL_DO),
        "forbidden": len(LEGAL_DONT),
        "zones": RISK_ZONES,
    }
