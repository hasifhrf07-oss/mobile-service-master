REPLY = {
    "brand_question": "আপনার {brand} নিয়ে জানতে চাওয়ার জন্য ধন্যবাদ। Calibration প্রতি ১২ মাসে করান।",
    "fault_report": "🔧 সমস্যা জানানোর জন্য ধন্যবাদ। Dashboard-এ ৪টা ছবি আপলোড করুন।",
    "battery": "🔋 ব্যাটারি: Volt চেক করুন, Terminal ক্লিন করুন।",
    "display": "🖥️ ডিসপ্লে: Contrast ঘুরান, Battery fresh কিনা দেখুন।",
    "update_request": "🚀 আপনার আপডেট রিকোয়েস্ট Admin Dashboard-এ পাঠানো হয়েছে।",
    "praise": "🙏 ধন্যবাদ!",
    "general": "📩 কমেন্ট পেয়েছি। টেকনিশিয়ান দল যোগাযোগ করবে।",
}

def generate_reply(classification):
    intents = classification.get("intents", ["general"])
    brand = classification.get("brand", "")
    tmpl = REPLY.get(intents[0], REPLY["general"])
    try: return tmpl.format(brand=brand or "আপনার")
    except: return tmpl
