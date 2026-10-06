"""Verify database tables"""
import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), "database", "devices.db")

conn = sqlite3.connect(DB)
tables = [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
)]
conn.close()

print("=" * 55)
print("📊 Database Tables")
print("=" * 55)
for t in tables:
    print(f"   • {t}")

print("=" * 55)
expected = ["devices", "devices_fts", "history", "meta",
            "update_log", "boardview_files", "board_scans",
            "scan_history"]

missing = [t for t in expected if t not in tables]

if missing:
    print(f"❌ Missing: {missing}")
else:
    print(f"✅ সব {len(expected)} টা table আছে!")
print("=" * 55)