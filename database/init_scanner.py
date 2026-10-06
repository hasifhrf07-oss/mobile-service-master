"""
Init Scanner — Scanner-specific tables setup (standalone).
init_db.py-র সাথে complementary।
চালাও: python database/init_scanner.py
"""

import sqlite3
import os
from datetime import datetime


DB = os.path.join(os.path.dirname(__file__), "devices.db")


SCANNER_SCHEMA = """
-- ═══════════════════════════════════════════════════════
-- BoardView Files Registry
-- ═══════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS boardview_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    board_number TEXT,
    file_path TEXT UNIQUE,
    file_type TEXT,
    file_size INTEGER DEFAULT 0,
    source TEXT DEFAULT 'manual',
    license_status TEXT DEFAULT 'personal',
    verified INTEGER DEFAULT 0,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bv_brand
    ON boardview_files(brand);
CREATE INDEX IF NOT EXISTS idx_bv_model
    ON boardview_files(model);
CREATE INDEX IF NOT EXISTS idx_bv_board
    ON boardview_files(board_number);

-- ═══════════════════════════════════════════════════════
-- Board Scans (Motherboard State)
-- ═══════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS board_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id TEXT UNIQUE,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    brand TEXT,
    model TEXT,
    chipset TEXT,
    phone_serial TEXT,
    board_serial TEXT,
    technician TEXT,
    client_name TEXT,
    client_phone TEXT,
    readings TEXT,
    current_draw REAL DEFAULT 0,
    symptoms TEXT,
    diagnosis TEXT,
    suspect_ics TEXT,
    photos TEXT,
    boardview_file TEXT,
    schematic_file TEXT,
    reference_scan_id TEXT,
    deviation_score REAL DEFAULT 0,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_scan_id
    ON board_scans(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_model
    ON board_scans(brand, model);
CREATE INDEX IF NOT EXISTS idx_scan_ts
    ON board_scans(ts);

-- ═══════════════════════════════════════════════════════
-- Scan History Log
-- ═══════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_id TEXT,
    action TEXT,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_sh_scan
    ON scan_history(scan_id);
CREATE INDEX IF NOT EXISTS idx_sh_ts
    ON scan_history(ts);
"""


def init_scanner_tables():
    """Scanner tables তৈরি করো (safe — যদি থাকে skip)"""
    if not os.path.exists(DB):
        print(f"❌ Database not found: {DB}")
        print("   Run 'python database/init_db.py' first.")
        return False

    conn = sqlite3.connect(DB)
    conn.executescript(SCANNER_SCHEMA)
    conn.commit()

    # Verify
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )]
    conn.close()

    scanner_tables = ["boardview_files", "board_scans", "scan_history"]
    missing = [t for t in scanner_tables if t not in tables]

    print("=" * 55)
    print("Scanner Tables Setup")
    print("=" * 55)

    for t in scanner_tables:
        if t in tables:
            print(f"   ✅ {t}")
        else:
            print(f"   ❌ {t} — MISSING")

    print("=" * 55)

    if missing:
        print(f"❌ Failed: {missing}")
        return False

    print("✅ Scanner tables ready")
    print(f"   DB: {DB}")
    print("=" * 55)
    return True


def verify_scanner_tables():
    """Only verify — কোনো change করবে না"""
    if not os.path.exists(DB):
        print(f"❌ DB not found: {DB}")
        return False

    conn = sqlite3.connect(DB)
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )]

    counts = {}
    for t in ("board_scans", "boardview_files", "scan_history"):
        if t in tables:
            counts[t] = conn.execute(
                f"SELECT COUNT(*) FROM {t}"
            ).fetchone()[0]
        else:
            counts[t] = None

    conn.close()

    print("=" * 55)
    print("Scanner Tables Verification")
    print("=" * 55)

    all_ok = True
    for t, cnt in counts.items():
        if cnt is None:
            print(f"   ❌ {t} — TABLE MISSING")
            all_ok = False
        else:
            print(f"   ✅ {t} — {cnt} rows")

    print("=" * 55)
    if all_ok:
        print("✅ All scanner tables verified")
    else:
        print("❌ Some tables missing — run init_scanner_tables()")
    print("=" * 55)
    return all_ok


if __name__ == "__main__":
    print()
    print("▶ Running scanner table setup...")
    print()
    init_scanner_tables()
    print()
    print("▶ Verifying...")
    print()
    verify_scanner_tables()