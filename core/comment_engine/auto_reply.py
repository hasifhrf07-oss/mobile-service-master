"""Auto Reply Generator"""

REPLY_LIBRARY = {
    "brand_question": (
        "আপনি {brand} নিয়ে জিজ্ঞাসা করেছেন।\n"
        "এটি {tier} গ্রেডের ইনস্ট্রুমেন্ট।\n"
        "প্রতি ১২ মাসে Calibration করান।\n"
        "Meter-এর ছবি Dashboard-এ আপলোড করলে আমরা বিশ্লেষণ করব।"
    ),
    "fault_report": (
        "সমস্যার জন্য:\n"
        "১) ৪টি মিটার ছবি Dashboard-এ আপলোড করুন\n"
        "২) Meter brand সিলেক্ট করুন\n"
        "৩) রিপোর্ট পাবেন সাথে সাথে"
    ),
    "battery": (
        "ব্যাটারি সমস্যার জন্য:\n"
        "- Volt চেক করুন (সাধারণত 9V)\n"
        "- Terminal ক্লিন করুন\n"
        "- 6LR61 / 9V ব্যাটারি লাগান"
    ),
    "display": (
        "ডিসপ্লে সমস্যা:\n"
        "- কনট্রাস্ট নব ঘুরান\n"
        "- Battery fresh কিনা যাচাই করুন\n"
        "- LCD solder joint চেক করুন"
    ),
    "calibration": "Calibration-এর জন্য আমাদের সার্ভিসে যোগাযোগ করুন। ২৪-৪৮ ঘন্টায় সম্পন্ন হয়।",
    "update_request": "আপনার আপডেট রিকোয়েস্ট Admin Dashboard-এ পাঠানো হয়েছে। ধন্যবাদ!",
    "feature_request": "চমৎকার আইডিয়া! Admin Review-তে রেখেছি।",
    "praise": "আপনার প্রশংসার জন্য অনেক ধন্যবাদ!",
    "complaint": "অসুবিধার জন্য দুঃখিত। বিস্তারিত জানালে দ্রুত সমাধান করব।",
    "general": "আপনার কমেন্ট আমরা পেয়েছি। টেকনিশিয়ান দল দ্রুত যোগাযোগ করবে।",
}

BRAND_TIER = {
    "Fluke": "High-Precision Industrial",
    "Kyoritsu": "Industrial-Grade",
    "Htc": "Standard Professional",
    "Unit": "Reliable Budget",
}


def generate_reply(classification):
    intents = classification.get("intents", ["general"])
    brand = classification.get("brand", "")

    primary = intents[0]
    tmpl = REPLY_LIBRARY.get(primary, REPLY_LIBRARY["general"])
    tier = BRAND_TIER.get(brand, "Standard")

    try:
        return tmpl.format(brand=brand or "আপনার", tier=tier)
    except Exception:
        return tmpl
