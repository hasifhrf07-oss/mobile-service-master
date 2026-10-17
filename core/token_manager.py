"""
AI Token Manager
Monitors B2B tool balances and uses AI to generate status reports/alerts.
"""
from settings import PAID_TOOLS
from core.ai_engine import ask_ai
import datetime

# Mock balances (In real world, you fetch this via B2B API)
TOKEN_BALANCES = {
    "unlocktool": 150,  # Credits
    "chimera": 50,
    "dftpro": 0,        # Out of credits
    "atf": 200,
    "medusa": 10
}

def check_tokens():
    """Check all tokens and generate AI alert if low"""
    alerts = []
    status_report = []
    
    for tool, balance in TOKEN_BALANCES.items():
        tool_name = PAID_TOOLS.get(tool, {}).get("name", tool.title())
        status_report.append(f"{tool_name}: {balance} credits left")
        
        if balance <= 0:
            alerts.append(f"❌ {tool_name} is OUT OF CREDITS! Operations will fail.")
        elif balance < 20:
            alerts.append(f"⚠️ {tool_name} is running low ({balance} left). Top up soon.")
            
    ai_message = ""
    if alerts:
        prompt = f"You are a system AI. Generate a short, urgent but polite notification for the admin based on these alerts:\n" + "\n".join(alerts)
        res = ask_ai(prompt)
        if res.get("ok"):
            ai_message = res.get("answer")
            
    return {
        "ok": True,
        "balances": TOKEN_BALANCES,
        "report": status_report,
        "alerts": alerts,
        "ai_summary": ai_message,
        "checked_at": datetime.datetime.now().isoformat()
    }
