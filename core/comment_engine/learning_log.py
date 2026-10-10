"""Learning Log — JSONL + retrain"""
import os
import json
from datetime import datetime
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_FILE = os.path.join(ROOT, "data", "comment_learning.jsonl")
LEARNED_FILE = os.path.join(ROOT, "data", "learned_keywords.json")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log_comment(entry):
    entry["logged_at"] = datetime.now().isoformat(timespec="seconds")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_stats():
    if not os.path.exists(LOG_FILE):
        return {"total": 0, "last_trained": None}

    total = 0
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for _ in f:
            total += 1

    trained = None
    if os.path.exists(LEARNED_FILE):
        try:
            trained = json.load(open(LEARNED_FILE, "r", encoding="utf-8")).get("trained_at")
        except Exception:
            pass

    return {"total": total, "last_trained": trained}


def retrain():
    if not os.path.exists(LOG_FILE):
        return {"ok": False, "message": "No logs to train"}

    counter = Counter()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                text = entry.get("text", "").lower()
                for w in text.split():
                    w = w.strip(".,!?।\"'()-")
                    if len(w) >= 3:
                        counter[w] += 1
            except Exception:
                continue

    learned = {
        "keywords": dict(counter.most_common(200)),
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "total_comments": sum(counter.values()),
    }

    with open(LEARNED_FILE, "w", encoding="utf-8") as f:
        json.dump(learned, f, ensure_ascii=False, indent=2)

    return {"ok": True, "top_keywords": list(learned["keywords"].items())[:20]}
