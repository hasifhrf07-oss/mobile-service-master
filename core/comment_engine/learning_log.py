import os, json
from datetime import datetime
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG = os.path.join(ROOT, "data", "comment_learning.jsonl")

def log_comment(entry):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    entry["logged_at"] = datetime.now().isoformat(timespec="seconds")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_stats():
    if not os.path.exists(LOG): return {"total": 0}
    c = 0
    with open(LOG, "r", encoding="utf-8") as f:
        for _ in f: c += 1
    return {"total": c, "last_trained": None}

def retrain():
    if not os.path.exists(LOG): return {"ok": False}
    counter = Counter()
    with open(LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
                for w in e.get("text", "").lower().split():
                    w = w.strip(".,!?।")
                    if len(w) >= 3: counter[w] += 1
            except: continue
    return {"ok": True, "top": list(counter.most_common(20))}
