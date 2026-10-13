INTENTS = {
    "brand_question": ["fluke", "kyoritsu", "htc", "uni-t", "brand"],
    "fault_report": ["fault", "problem", "নষ্ট", "broken", "dead"],
    "battery": ["battery", "ব্যাটারি", "charge"],
    "display": ["display", "lcd", "ডিসপ্লে"],
    "update_request": ["update", "আপডেট", "feature"],
    "praise": ["ধন্যবাদ", "thanks", "great"],
}
POS = ["ভালো", "thanks", "great", "awesome"]
NEG = ["খারাপ", "bad", "problem", "broken"]

def classify_comment(text):
    if not text: return {"intents": ["general"], "sentiment": "neutral", "brand": ""}
    t = text.lower()
    intents = [i for i, keys in INTENTS.items() if any(k in t for k in keys)] or ["general"]
    p = sum(1 for w in POS if w in t)
    n = sum(1 for w in NEG if w in t)
    sentiment = "positive" if p > n else ("negative" if n > p else "neutral")
    brand = ""
    for b in ["fluke", "kyoritsu", "htc", "unit"]:
        if b in t.replace("-", ""): brand = b.title(); break
    return {"intents": intents, "sentiment": sentiment, "brand": brand}
