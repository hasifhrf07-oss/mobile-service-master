"""Intent Classifier — rule-based comment classification"""

INTENTS = {
    "brand_question":  ["fluke", "kyoritsu", "htc", "uni-t", "unit", "brand", "মডেল", "model"],
    "fault_report":    ["fault", "problem", "নষ্ট", "কাজ করে না", "error", "broken", "dead"],
    "battery":         ["battery", "ব্যাটারি", "charge", "চার্জ"],
    "display":         ["display", "lcd", "ডিসপ্লে", "স্ক্রিন"],
    "calibration":     ["calibration", "ক্যালিব্রেশন", "accuracy", "সঠিক"],
    "update_request":  ["update", "আপডেট", "নতুন ফিচার", "feature", "add", "version"],
    "feature_request": ["chai", "চাই", "lagbe", "লাগবে", "want", "need", "please add"],
    "praise":          ["ধন্যবাদ", "thanks", "ভালো", "great", "awesome", "সুন্দর"],
    "complaint":       ["খারাপ", "bad", "slow", "problem", "issue"],
}

SENTIMENT_POS = ["ভালো", "সুন্দর", "ধন্যবাদ", "great", "good", "awesome", "love", "perfect"]
SENTIMENT_NEG = ["খারাপ", "bad", "slow", "problem", "issue", "broken", "নষ্ট", "hate"]


def classify_comment(text):
    if not text:
        return {"intents": ["general"], "sentiment": "neutral", "brand": ""}

    t = text.lower()

    intents = [i for i, keys in INTENTS.items() if any(k in t for k in keys)]
    if not intents:
        intents = ["general"]

    pos = sum(1 for w in SENTIMENT_POS if w in t)
    neg = sum(1 for w in SENTIMENT_NEG if w in t)
    if pos > neg:
        sentiment = "positive"
    elif neg > pos:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    brand = ""
    tl = t.replace("-", "")
    for b in ["fluke", "kyoritsu", "htc", "unit"]:
        if b in tl:
            brand = b.title()
            break

    return {
        "intents": intents,
        "sentiment": sentiment,
        "brand": brand,
    }
