"""Consent Manager — JSONL log"""

import json
import hashlib
import os
from datetime import datetime


class ConsentManager:
    def __init__(self, logfile="logs/consent.jsonl"):
        root = os.path.dirname(os.path.dirname(__file__))
        self.logfile = os.path.join(root, logfile)
        os.makedirs(os.path.dirname(self.logfile), exist_ok=True)

    def request_programmatic(self, action, details,
                             client_name="", client_phone="",
                             granted=False):
        self._log(action, details, client_name, client_phone, granted)
        return granted

    def _log(self, action, details,
             client_name, client_phone, granted):
        ts = datetime.now()
        signature = hashlib.sha256(
            f"{client_phone}|{ts.isoformat()}|{action}|{granted}".encode()
        ).hexdigest()[:16]

        record = {
            "ts": ts.isoformat(),
            "client": client_name,
            "phone": client_phone,
            "action": action,
            "details": details,
            "granted": granted,
            "signature": signature,
        }

        try:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Consent log fail: {e}")

    def get_log(self, limit=100):
        if not os.path.exists(self.logfile):
            return []
        records = []
        with open(self.logfile, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records[-limit:]

    def count(self):
        return len(self.get_log(limit=999999))