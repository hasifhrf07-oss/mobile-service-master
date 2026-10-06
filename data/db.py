"""DB Helper — extended with BoardView + Scanner"""

import sqlite3
import json
import os
from contextlib import contextmanager

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                  "database", "devices.db")


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
# Devices
# ═════════════════════════════════════════════════════════

def find_device(brand, model):
    with conn() as c:
        r = c.execute(
            "SELECT * FROM devices WHERE brand = ? AND model = ? LIMIT 1",
            (brand, model)
        ).fetchone()
        return dict(r) if r else None


def search_devices(query, limit=50):
    q = query.strip()
    if not q:
        return []
    with conn() as c:
        try:
            rows = c.execute("""
                SELECT d.* FROM devices d
                JOIN devices_fts f ON f.rowid = d.id
                WHERE devices_fts MATCH ?
                LIMIT ?
            """, (q + "*", limit)).fetchall()
        except sqlite3.OperationalError:
            rows = c.execute("""
                SELECT * FROM devices
                WHERE brand LIKE ? OR model LIKE ? OR chipset LIKE ?
                LIMIT ?
            """, (f"%{q}%", f"%{q}%", f"%{q}%", limit)).fetchall()
        return [dict(r) for r in rows]


def list_brands():
    with conn() as c:
        rows = c.execute("""
            SELECT brand, COUNT(*) AS n FROM devices
            GROUP BY brand ORDER BY n DESC
        """).fetchall()
        return [dict(r) for r in rows]


def total_count():
    with conn() as c:
        return c.execute("SELECT COUNT(*) FROM devices").fetchone()[0]


def clone_count():
    with conn() as c:
        return c.execute("SELECT COUNT(*) FROM devices WHERE is_clone=1").fetchone()[0]


def add_device(brand, model, codename="", chipset="", android_ver="",
               release_year=0, is_clone=0, common_issues=None,
               hw_guide_path=""):
    if common_issues is None:
        common_issues = []
    with conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO devices
            (brand, model, codename, chipset, android_ver,
             release_year, is_clone, common_issues, hw_guide_path, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (brand, model, codename, chipset, android_ver,
              release_year, is_clone, json.dumps(common_issues),
              hw_guide_path))
        return c.total_changes > 0


def delete_device(brand, model):
    with conn() as c:
        c.execute("DELETE FROM devices WHERE brand=? AND model=?",
                  (brand, model))
        return c.total_changes > 0


# ═════════════════════════════════════════════════════════
# Meta
# ═════════════════════════════════════════════════════════

def get_meta(key, default=None):
    with conn() as c:
        r = c.execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
        return r["v"] if r else default


def set_meta(key, value):
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)",
                  (key, str(value)))


# ═════════════════════════════════════════════════════════
# History
# ═════════════════════════════════════════════════════════

def log_history(brand, model, issue_type, summary,
                action="", notes="", client_name="", client_phone=""):
    with conn() as c:
        c.execute("""
            INSERT INTO history
            (brand, model, issue_type, summary, action, notes,
             client_name, client_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (brand, model, issue_type, summary, action, notes,
              client_name, client_phone))


def recent_history(limit=100):
    with conn() as c:
        rows = c.execute("""
            SELECT * FROM history
            ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def history_stats():
    with conn() as c:
        total = c.execute("SELECT COUNT(*) FROM history").fetchone()[0]
        by_type = c.execute("""
            SELECT issue_type, COUNT(*) AS n FROM history
            GROUP BY issue_type ORDER BY n DESC
        """).fetchall()
        by_brand = c.execute("""
            SELECT brand, COUNT(*) AS n FROM history
            WHERE brand IS NOT NULL
            GROUP BY brand ORDER BY n DESC LIMIT 10
        """).fetchall()
        return {
            "total": total,
            "by_type": [dict(r) for r in by_type],
            "top_brands": [dict(r) for r in by_brand],
        }


# ═════════════════════════════════════════════════════════
# NEW: BoardView Files
# ═════════════════════════════════════════════════════════

def add_boardview_file(brand, model, board_number, file_path,
                       file_type, file_size=0, source="manual",
                       license_status="personal", notes=""):
    """BoardView file register করো"""
    with conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO boardview_files
            (brand, model, board_number, file_path, file_type,
             file_size, source, license_status, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (brand, model, board_number, file_path, file_type,
              file_size, source, license_status, notes))
        return c.total_changes > 0


def find_boardview_file(brand, model):
    """BoardView file খোঁজো"""
    with conn() as c:
        r = c.execute("""
            SELECT * FROM boardview_files
            WHERE brand = ? AND model = ?
            ORDER BY id DESC LIMIT 1
        """, (brand, model)).fetchone()
        return dict(r) if r else None


def list_boardview_files(brand=None, limit=200):
    """BoardView files list"""
    with conn() as c:
        if brand:
            rows = c.execute("""
                SELECT * FROM boardview_files
                WHERE brand = ?
                ORDER BY brand, model LIMIT ?
            """, (brand, limit)).fetchall()
        else:
            rows = c.execute("""
                SELECT * FROM boardview_files
                ORDER BY brand, model LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def delete_boardview_file(file_id):
    with conn() as c:
        c.execute("DELETE FROM boardview_files WHERE id=?", (file_id,))
        return c.total_changes > 0


# ═════════════════════════════════════════════════════════
# NEW: Board Scans (Motherboard State)
# ═════════════════════════════════════════════════════════

def save_board_scan(scan_id, brand, model, chipset,
                    phone_serial="", board_serial="",
                    technician="", client_name="", client_phone="",
                    readings=None, current_draw=0,
                    symptoms=None, diagnosis="", suspect_ics=None,
                    photos=None, boardview_file="", schematic_file="",
                    reference_scan_id="", deviation_score=0,
                    notes=""):
    """Board state save করো"""
    if readings is None:
        readings = {}
    if symptoms is None:
        symptoms = []
    if suspect_ics is None:
        suspect_ics = []
    if photos is None:
        photos = []

    with conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO board_scans
            (scan_id, brand, model, chipset, phone_serial, board_serial,
             technician, client_name, client_phone,
             readings, current_draw, symptoms, diagnosis, suspect_ics,
             photos, boardview_file, schematic_file,
             reference_scan_id, deviation_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, brand, model, chipset, phone_serial, board_serial,
              technician, client_name, client_phone,
              json.dumps(readings), current_draw,
              json.dumps(symptoms), diagnosis, json.dumps(suspect_ics),
              json.dumps(photos), boardview_file, schematic_file,
              reference_scan_id, deviation_score, notes))
        return c.total_changes > 0


def get_board_scan(scan_id):
    with conn() as c:
        r = c.execute("""
            SELECT * FROM board_scans WHERE scan_id = ?
        """, (scan_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        # Parse JSON
        for key in ("readings", "symptoms", "suspect_ics", "photos"):
            try:
                d[key] = json.loads(d.get(key) or "[]")
            except Exception:
                d[key] = []
        return d


def list_board_scans(brand=None, model=None, limit=100):
    with conn() as c:
        if brand and model:
            rows = c.execute("""
                SELECT * FROM board_scans
                WHERE brand = ? AND model = ?
                ORDER BY id DESC LIMIT ?
            """, (brand, model, limit)).fetchall()
        elif brand:
            rows = c.execute("""
                SELECT * FROM board_scans
                WHERE brand = ?
                ORDER BY id DESC LIMIT ?
            """, (brand, limit)).fetchall()
        else:
            rows = c.execute("""
                SELECT * FROM board_scans
                ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def delete_board_scan(scan_id):
    with conn() as c:
        c.execute("DELETE FROM board_scans WHERE scan_id=?", (scan_id,))
        return c.total_changes > 0


def scan_count():
    with conn() as c:
        return c.execute("SELECT COUNT(*) FROM board_scans").fetchone()[0]


def boardview_count():
    with conn() as c:
        return c.execute("SELECT COUNT(*) FROM boardview_files").fetchone()[0]


# ═════════════════════════════════════════════════════════
# NEW: Scan History Log
# ═════════════════════════════════════════════════════════

def log_scan_action(scan_id, action, details=""):
    with conn() as c:
        c.execute("""
            INSERT INTO scan_history (scan_id, action, details)
            VALUES (?, ?, ?)
        """, (scan_id, action, details))


def get_scan_history(scan_id=None, limit=100):
    with conn() as c:
        if scan_id:
            rows = c.execute("""
                SELECT * FROM scan_history
                WHERE scan_id = ?
                ORDER BY id DESC LIMIT ?
            """, (scan_id, limit)).fetchall()
        else:
            rows = c.execute("""
                SELECT * FROM scan_history
                ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]