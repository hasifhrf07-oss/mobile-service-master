"""
AI Engine - OpenAI + Gemini Integration
"""
import os
import json
import requests

# ── AI Configuration ──
AI_CONFIG = {
    "openai": {
        "api_key": "",
        "model": "gpt-4o-mini",
        "api_url": "https://api.openai.com/v1/chat/completions",
        "enabled": False,
    },
    "gemini": {
        "api_key": "",
        "model": "gemini-1.5-flash",
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "enabled": False,
    },
    "default_provider": "gemini",  # free tier available
}


def set_ai_key(provider, api_key):
    """Admin AI API key add koro"""
    if provider in AI_CONFIG:
        AI_CONFIG[provider]["api_key"] = api_key
        AI_CONFIG[provider]["enabled"] = True
        return True
    return False


def get_ai_status():
    """AI status check"""
    return {
        "openai": {
            "enabled": AI_CONFIG["openai"]["enabled"],
            "has_key": bool(AI_CONFIG["openai"]["api_key"]),
        },
        "gemini": {
            "enabled": AI_CONFIG["gemini"]["enabled"],
            "has_key": bool(AI_CONFIG["gemini"]["api_key"]),
        },
        "default": AI_CONFIG["default_provider"],
    }


def ask_ai(prompt, system_prompt="You are Mobile Service Master AI, a helpful assistant for mobile repair technicians."):
    """AI ke proshno koro"""
    provider = AI_CONFIG["default_provider"]

    # OpenAI
    if provider == "openai" and AI_CONFIG["openai"]["enabled"]:
        try:
            headers = {
                "Authorization": f"Bearer {AI_CONFIG['openai']['api_key']}",
                "Content-Type": "application/json",
            }
            body = {
                "model": AI_CONFIG["openai"]["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            }
            r = requests.post(AI_CONFIG["openai"]["api_url"], json=body, headers=headers, timeout=30)
            return {"ok": True, "answer": r.json()["choices"][0]["message"]["content"], "provider": "openai"}
        except Exception as e:
            return {"ok": False, "error": str(e), "provider": "openai"}

    # Gemini
    if provider == "gemini" and AI_CONFIG["gemini"]["enabled"]:
        try:
            url = f"{AI_CONFIG['gemini']['api_url']}/{AI_CONFIG['gemini']['model']}:generateContent?key={AI_CONFIG['gemini']['api_key']}"
            body = {
                "contents": [{"parts": [{"text": system_prompt + "\n\n" + prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500},
            }
            r = requests.post(url, json=body, timeout=30)
            answer = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return {"ok": True, "answer": answer, "provider": "gemini"}
        except Exception as e:
            return {"ok": False, "error": str(e), "provider": "gemini"}

    return {"ok": False, "error": "No AI provider enabled. Admin settings e API key add koro.", "provider": None}
