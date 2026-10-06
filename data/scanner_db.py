"""
Scanner DB Helper — scanner-specific queries সহজ করার জন্য।
Main db.py-র supplement।
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager


ROOT = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(ROOT, "database", "devices.db")


@contextmanager
def conn():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


# ═════════════════════════════════════════════════════════
# BoardView Files
# ═════════════════════════════════════════════════════════

def register_boardview(brand, model, board_number, file_path,
                       file_type="brd", source="manual",
                       license_status="personal", notes=""):
    """BoardView file register"""
    try:
        size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    except Exception:
        size = 0

    with conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO boardview_files
            (brand, model, board_number, file_path, file_type,
             file_size, source, license_status, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (brand, model, board_number, file_path, file_type,
              size, source, license_status, notes))
        return True


def find_boardview(brand, model):
    """BoardView file find"""
    with conn() as c:
        r = c.execute("""
            SELECT * FROM boardview_files
            WHERE brand=? AND model=?
            ORDER BY id DESC LIMIT 1
        """, (brand, model)).fetchone()
        return dict(r) if r else None


def list_all_boardviews(brand=None):
    with conn() as c:
        if brand:
            rows = c.execute("""
                SELECT * FROM boardview_files
                WHERE brand=? ORDER BY model
            """, (brand,)).fetchall()
        else:
            rows = c.execute("""
                SELECT * FROM boardview_files ORDER BY brand, model
            """).fetchall()
        return [dict(r) for r in rows]


def delete_boardview(file_id):
    with conn() as c:
        c.execute("DELETE FROM boardview_files WHERE id=?", (file_id,))
        return c.total_changes > 0


def boardview_count():
    with conn() as c:
        return c.execute(
            "SELECT COUNT(*) FROM boardview_files"
        ).fetchone()[0]


def boardview_brands():
    """Brand-wise file count"""
    with conn() as c:
        rows = c.execute("""
            SELECT brand, COUNT(*) AS n FROM boardview_files
            GROUP BY brand ORDER BY n DESC
        """).fetchall()
        return [dict(r) for r in rows]


# ═════════════════════════════════════════════════════════
# Board Scans
# ═════════════════════════════════════════════════════════

def save_scan(data):
    """
    data = {
        "scan_id": "SM-A105F-20260930-001",
        "brand": "Samsung",
        "model": "SM-A105F",
        "chipset": "Exynos 7884",
        "readings": {"vbat": 3.78, ...},
        "diagnosis": "...",
        ...
    }
    """
    scan_id = data.get("scan_id") or _generate_scan_id(
        data.get("brand", ""), data.get("model", "")
    )

    with conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO board_scans
            (scan_id, brand, model, chipset, phone_serial, board_serial,
             technician, client_name, client_phone,
             readings, current_draw, symptoms, diagnosis, suspect_ics,
             photos, boardview_file, schematic_file,
             reference_scan_id, deviation_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id,
            data.get("brand", ""),
            data.get("model", ""),
            data.get("chipset", ""),
            data.get("phone_serial", ""),
            data.get("board_serial", ""),
            data.get("technician", ""),
            data.get("client_name", ""),
            data.get("client_phone", ""),
            json.dumps(data.get("readings", {})),
            float(data.get("current_draw", 0)),
            json.dumps(data.get("symptoms", [])),
            data.get("diagnosis", ""),
            json.dumps(data.get("suspect_ics", [])),
            json.dumps(data.get("photos", [])),
            data.get("boardview_file", ""),
            data.get("schematic_file", ""),
            data.get("reference_scan_id", ""),
            float(data.get("deviation_score", 0)),
            data.get("notes", ""),
        ))
        return scan_id


def _generate_scan_id(brand, model):
    """Auto-generate scan ID"""
    brand_clean = (brand or "UNK").replace(" ", "").upper()[:6]
    model_clean = (model or "UNK").replace(" ", "").upper()[:12]
    date_str = datetime.now().strftime("%Y%m%d")

    with conn() as c:
        prefix = f"{model_clean}-{date_str}-"
        row = c.execute(
            "SELECT COUNT(*) FROM board_scans WHERE scan_id LIKE ?",
            (prefix + "%",)
        ).fetchone()
        n = (row[0] if row else 0) + 1

    return f"{model_clean}-{date_str}-{n:03d}"


def get_scan(scan_id):
    """Scan read + JSON parse"""
    with conn() as c:
        r = c.execute(
            "SELECT * FROM board_scans WHERE scan_id=?",
            (scan_id,)
        ).fetchone()

        if not r:
            return None

        d = dict(r)
        for key in ("readings", "symptoms", "suspect_ics", "photos"):
            try:
                d[key] = json.loads(d.get(key) or "[]")
            except Exception:
                d[key] = [] if key != "readings" else {}
        return d


def list_scans(brand=None, model=None, limit=100):
    """List scans with optional filter"""
    with conn() as c:
        if brand and model:
            rows = c.execute("""
                SELECT * FROM board_scans
                WHERE brand=? AND model=?
                ORDER BY id DESC LIMIT ?
            """, (brand, model, limit)).fetchall()
        elif brand:
            rows = c.execute("""
                SELECT * FROM board_scans
                WHERE brand=?
                ORDER BY id DESC LIMIT ?
            """, (brand, limit)).fetchall()
        else:
            rows = c.execute("""
                SELECT * FROM board_scans
                ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def delete_scan(scan_id):
    with conn() as c:
        c.execute("DELETE FROM board_scans WHERE scan_id=?", (scan_id,))
        c.execute("DELETE FROM scan_history WHERE scan_id=?", (scan_id,))
        return c.total_changes > 0


def scan_count():
    with conn() as c:
        return c.execute(
            "SELECT COUNT(*) FROM board_scans"
        ).fetchone()[0]


def scan_recent(days=7, limit=50):
    """Recent scans"""
    since = (datetime.now() - timedelta(days=days)).isoformat()
    with conn() as c:
        rows = c.execute("""
            SELECT * FROM board_scans
            WHERE ts >= ?
            ORDER BY id DESC LIMIT ?
        """, (since, limit)).fetchall()
        return [dict(r) for r in rows]


def scan_by_model(brand, model):
    """All scans for a specific model"""
    with conn() as c:
        rows = c.execute("""
            SELECT * FROM board_scans
            WHERE brand=? AND model=?
            ORDER BY id DESC
        """, (brand, model)).fetchall()
        return [dict(r) for r in rows]


# ═════════════════════════════════════════════════════════
# Scan History Log
# ═════════════════════════════════════════════════════════

def log_action(scan_id, action, details=""):
    with conn() as c:
        c.execute("""
            INSERT INTO scan_history (scan_id, action, details)
            VALUES (?, ?, ?)
        """, (scan_id, action, details))


def get_history(scan_id=None, limit=200):
    with conn() as c:
        if scan_id:
            rows = c.execute("""
                SELECT * FROM scan_history
                WHERE scan_id=?
                ORDER BY id DESC LIMIT ?
            """, (scan_id, limit)).fetchall()
        else:
            rows = c.execute("""
                SELECT * FROM scan_history
                ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]


# ═════════════════════════════════════════════════════════
# Stats
# ═════════════════════════════════════════════════════════

def dashboard_stats():
    """Overall dashboard statistics"""
    return {
        "devices": _count("devices"),
        "clones": _count("devices", "is_clone=1"),
        "scans": _count("board_scans"),
        "boardviews": _count("boardview_files"),
        "history_events": _count("history"),
    }


def _count(table, where=""):
    with conn() as c:
        query = f"SELECT COUNT(*) FROM {table}"
        if where:
            query += f" WHERE {where}"
        return c.execute(query).fetchone()[0]
 