"""
Digital Liability Waiver System
"""
import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "local_data", "database", "devices.db"
)
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "devices.db")


WAIVER_TEXT = """
════════════════════════════════════════════════════════════════
                DIGITAL LIABILITY WAIVER
════════════════════════════════════════════════════════════════

I, the undersigned user of Mobile Service Master, hereby acknowledge
and agree to the following:

1. I am a professional mobile repair technician, or I am acting
   under the supervision of one.

2. I understand that unlocking, flashing, or modifying mobile
   devices may void manufacturer warranties.

3. I understand that improper use may cause permanent hardware
   damage. Mobile Service Master is NOT responsible for any damage
   caused by misuse.

4. I will use this software in compliance with all applicable
   local, national, and international laws.

5. I will NOT use this software for illegal activities including
   but not limited to: device theft, fraud, or unauthorized
   surveillance.

6. I understand that paid tool API usage is billed by third-party
   providers, and Mobile Service Master does not control pricing.

7. This waiver is binding and legally enforceable.

════════════════════════════════════════════════════════════════
"""


def init_waiver_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS waivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            signature TEXT NOT NULL,
            signed_at TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            waiver_hash TEXT
        )
    """)
    conn.commit()
    conn.close()


def has_signed(email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT 1 FROM waivers WHERE email = ?", (email,))
        result = c.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


def sign_waiver(email, signature, ip="", user_agent=""):
    init_waiver_table()
    waiver_hash = hashlib.sha256((email + signature + WAIVER_TEXT).encode()).hexdigest()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO waivers
            (email, signature, signed_at, ip_address, user_agent, waiver_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (email, signature, datetime.now().isoformat(), ip, user_agent, waiver_hash))
        conn.commit()
        conn.close()
        return {"ok": True, "hash": waiver_hash}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_waiver(email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM waivers WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()
        return row
    except Exception:
        return None
