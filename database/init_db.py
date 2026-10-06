"""Database schema initialization — extended"""

import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), "devices.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    codename TEXT,
    chipset TEXT,
    android_ver TEXT,
    release_year INTEGER,
    is_clone INTEGER DEFAULT 0,
    common_issues TEXT,
    hw_guide_path TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand, model)
);
CREATE INDEX IF NOT EXISTS idx_brand ON devices(brand);
CREATE INDEX IF NOT EXISTS idx_model ON devices(model);
CREATE INDEX IF NOT EXISTS idx_chipset ON devices(chipset);

CREATE VIRTUAL TABLE IF NOT EXISTS devices_fts USING fts5(
    brand, model, chipset,
    content='devices',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS devices_ai AFTER INSERT ON devices BEGIN
    INSERT INTO devices_fts(rowid, brand, model, chipset)
    VALUES (new.id, new.brand, new.model, new.chipset);
END;

CREATE TABLE IF NOT EXISTS meta (
    k TEXT PRIMARY KEY,
    v TEXT
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    brand TEXT,
    model TEXT,
    issue_type TEXT,
    summary TEXT,
    action TEXT,
    notes TEXT,
    client_name TEXT,
    client_phone TEXT
);

CREATE TABLE IF NOT EXISTS update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT,
    added INTEGER,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════
-- NEW: BoardView Files Registry
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
CREATE INDEX IF NOT EXISTS idx_bv_brand ON boardview_files(brand);
CREATE INDEX IF NOT EXISTS idx_bv_model ON boardview_files(model);
CREATE INDEX IF NOT EXISTS idx_bv_board ON boardview_files(board_number);

-- ═══════════════════════════════════════════════════════
-- NEW: Board Scans (Motherboard State)
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
CREATE INDEX IF NOT EXISTS idx_scan_id ON board_scans(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_model ON board_scans(brand, model);
CREATE INDEX IF NOT EXISTS idx_scan_ts ON board_scans(ts);

-- ═══════════════════════════════════════════════════════
-- NEW: Scan History Log
-- ═══════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_id TEXT,
    action TEXT,
    details TEXT
);
CREATE INDEX IF NOT EXISTS idx_sh_scan ON scan_history(scan_id);
"""


def init():
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('db_version', '3.1')")
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('last_update', 'initial')")
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    conn.close()
    print("=" * 55)
    print("Database created successfully")
    print("=" * 55)
    print(f"Path    : {DB}")
    print(f"Devices : {total}")
    print("=" * 55)


if __name__ == "__main__":
    init()