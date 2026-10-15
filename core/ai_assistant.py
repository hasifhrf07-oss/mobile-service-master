"""
Admin AI Assistant
- Admin provides API key
- AI works on behalf of admin
- Answers technician questions
- Guides diagnosis + tools
- NO autonomy — only assistant
"""
import os
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
AI_CONFIG = os.path.join(ROOT, "data", "ai_config.json")
USAGE_LOG = os.path.join(ROOT, "data", "ai_usage.jsonl")


# ═══════════════════════════════════════════════════════════
# SYSTEM PROMPT (Admin's voice)
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are the official assistant for "Mobile Service Master" — a professional mobile service application.

Your role:
- Answer technician questions about mobile repair
- Guide firmware flashing for Samsung, Xiaomi, Oppo, Vivo, Realme, etc.
- Suggest official tools (Odin, SP Flash Tool, QFIL, Mi Flash, Heimdall)
- Explain diagnosis steps for boot loop, dead phone, battery issues
- Keep answers professional, short, and actionable
- Use Bangla if user writes in Bangla, English otherwise
- NEVER suggest illegal activities (FRP bypass without owner consent, IMEI change)
- For locked phones, recommend owner verification
- For legal tool purchases, mention UnlockTool / Chimera with disclaimer

Your tone: Helpful, professional, ethical, never aggressive."""


def _load_config():
    if os.path.exists(AI_CONFIG):
        try:
            return json.load(open(AI_CONFIG, "r", encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_config(data):
    os.makedirs(os.path.dirname(AI_CONFIG), exist_ok=True)
    json.dump(data, open(AI_CONFIG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _log_usage(entry):
    os.makedirs(os.path.dirname(USAGE_LOG), exist_ok=True)
    entry["at"] = datetime.now().isoformat(timespec="seconds")
    with open(USAGE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

def get_ai_config():
    """Get AI config (without exposing API key)"""
    cfg = _load_config()
    return {
        "enabled": cfg.get("enabled", False),
        "provider": cfg.get("provider", "rule-based"),
        "model": cfg.get("model", "gpt-4o-mini"),
        "api_key_set": bool(cfg.get("api_key", "")),
        "activated_at": cfg.get("activated_at"),
        "admin_email": cfg.get("admin_email", ""),
    }


def activate_ai(api_key, provider="openai", model="gpt-4o-mini", admin_email=""):
    """Admin activates AI with own API key"""
    cfg = _load_config()
    cfg.update({
        "enabled": True,
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "admin_email": admin_email,
        "activated_at": datetime.now().isoformat(timespec="seconds"),
    })
    _save_config(cfg)
    return {"ok": True, "message": "AI activated", "config": get_ai_config()}


def deactivate_ai():
    """Disable AI"""
    cfg = _load_config()
    cfg["enabled"] = False
    _save_config(cfg)
    return {"ok": True, "message": "AI deactivated"}


# ═══════════════════════════════════════════════════════════
# ASK (Main function)
# ═══════════════════════════════════════════════════════════

def ask(question, user_email="guest", context=""):
    """
    Technician asks a question.
    AI answers on behalf of admin.
    """
    cfg = _load_config()

    if not cfg.get("enabled") or not cfg.get("api_key"):
        # Fallback: rule-based reply
        return _rule_reply(question, user_email, reason="ai_not_activated")

    provider = cfg.get("provider", "openai")
    api_key = cfg["api_key"]
    model = cfg.get("model", "gpt-4o-mini")

    full_question = question
    if context:
        full_question = f"Context: {context}\n\nQuestion: {question}"

    try:
        if provider == "openai":
            answer = _ask_openai(api_key, model, full_question)
        elif provider == "gemini":
            answer = _ask_gemini(api_key, model, full_question)
        elif provider == "claude":
            answer = _ask_claude(api_key, model, full_question)
        else:
            return _rule_reply(question, user_email, reason=f"unknown_provider_{provider}")

        _log_usage({
            "user": user_email,
            "provider": provider,
            "model": model,
            "question": question[:200],
            "answer_length": len(answer),
            "status": "success",
        })

        return {
            "ok": True,
            "source": provider,
            "model": model,
            "answer": answer,
        }

    except Exception as e:
        _log_usage({
            "user": user_email,
            "provider": provider,
            "status": "error",
            "error": str(e)[:200],
        })
        # Fallback
        return _rule_reply(question, user_email, reason=f"api_error: {str(e)[:80]}")


# ═══════════════════════════════════════════════════════════
# PROVIDER IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════

def _ask_openai(api_key, model, question):
    """OpenAI API call"""
    import urllib.request
    url = "https://api.openai.com/v1/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "max_tokens": 400,
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode())
        return data["choices"][0]["message"]["content"]


def _ask_gemini(api_key, model, question):
    """Google Gemini API call"""
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {
        "contents": [{
            "parts": [
                {"text": SYSTEM_PROMPT},
                {"text": question},
            ]
        }]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"]


def _ask_claude(api_key, model, question):
    """Anthropic Claude API call"""
    import urllib.request
    url = "https://api.anthropic.com/v1/messages"
    body = {
        "model": model or "claude-3-5-sonnet-20241022",
        "max_tokens": 400,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": question}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode())
        return data["content"][0]["text"]


# ═══════════════════════════════════════════════════════════
# RULE-BASED FALLBACK (when AI not activated)
# ═══════════════════════════════════════════════════════════

RULE_REPLIES = {
    "samsung": "📱 Samsung: Firmware = SamMobile, Tool = Odin3, Download Mode = Vol Down + Home + Power",
    "xiaomi": "📱 Xiaomi: Firmware = XiaomiFirmwareUpdater, Tool = Mi Flash Tool, Fastboot = Vol Down + Power",
    "oppo": "📱 Oppo: Firmware = OppoFirmware, Tool = MSM Download Tool",
    "vivo": "📱 Vivo: Firmware = VivoFirmware, Tool = AFTool",
    "realme": "📱 Realme: Firmware = RealmeUpdater, Tool = Realme Flash Tool",
    "boot_loop": "🔄 Boot Loop: Recovery → Wipe Cache → Factory Reset → Firmware Reflash",
    "dead": "💀 Dead Phone: Battery check (3.7V) → EDL/BROM → Stock Firmware",
    "battery": "🔋 Battery: Volt check → Terminal clean → 9V replace",
    "frp": "🔒 FRP: ⚠️ Owner verification required (legal). Paid tool: UnlockTool",
    "flash": "⚡ Flash Steps: 1) Download firmware 2) Boot to special mode 3) Connect USB 4) Run tool",
    "report": "📊 Report: Diagnosis complete. Say 'generate report' for PDF.",
    "help": "🔧 আমি জিজ্ঞেস করতে পারি:\n- Samsung/Xiaomi/Oppo fix\n- Boot loop\n- Dead phone\n- FRP\n- Flash steps",
}


def _rule_reply(question, user_email, reason=""):
    """Rule-based fallback"""
    q = question.lower()
    for key, reply in RULE_REPLIES.items():
        if key in q:
            return {
                "ok": True,
                "source": "rule-based",
                "reason": reason,
                "answer": reply + "\n\n_(AI key দিলে detailed answer পাবেন)_",
            }
    return {
        "ok": True,
        "source": "rule-based",
        "reason": reason,
        "answer": "🤔 প্রশ্নটি পরিষ্কার নয়।\n\nআপনি জিজ্ঞেস করতে পারেন:\n- Samsung/Xiaomi/Oppo flash\n- Boot loop\n- Dead phone\n- FRP lock\n- Battery issue\n\n(Admin AI key activate করলে আরো ভালো উত্তর পাবেন)"
    }


# ═══════════════════════════════════════════════════════════
# USAGE STATS
# ═══════════════════════════════════════════════════════════

def get_usage_stats():
    """AI usage statistics"""
    if not os.path.exists(USAGE_LOG):
        return {"total": 0, "by_user": {}, "by_provider": {}}

    total = 0
    by_user = {}
    by_provider = {}

    try:
        with open(USAGE_LOG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    total += 1
                    u = d.get("user", "unknown")
                    by_user[u] = by_user.get(u, 0) + 1
                    p = d.get("provider", "unknown")
                    by_provider[p] = by_provider.get(p, 0) + 1
                except Exception:
                    pass
    except Exception:
        pass

    return {
        "total": total,
        "by_user": by_user,
        "by_provider": by_provider,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("ADMIN AI ASSISTANT")
    print("=" * 60)
    print()
    print("Current config:", get_ai_config())
    print()
    print("Test (rule-based):")
    print(ask("samsung")["answer"][:200])
