"""
Board Scanner — Motherboard state capture, save, and compare.
প্রতিটা board scan-এ:
- Physical readings capture
- BoardView file link
- Photos
- History save
- Compare with reference
"""

import os
import json
import sqlite3
from datetime import datetime
from contextlib import contextmanager


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB = os.path.join(ROOT, "database", "devices.db")
PHOTOS_DIR = os.path.join(ROOT, "logs", "scans")
BOARDVIEW_DIR = os.path.join(ROOT, "guides", "boardview")
SCHEMATIC_DIR = os.path.join(ROOT, "guides", "schematic")


@contextmanager
def _db():
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


class BoardScanner:
    """
    Multi-Device Scanner — প্রতিটা motherboard-এর state save ও compare করবে।
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        os.makedirs(PHOTOS_DIR, exist_ok=True)

    # ═════════════════════════════════════════════════════════
    # Scan ID Generator
    # ═════════════════════════════════════════════════════════

    def generate_scan_id(self, brand, model):
        """
        Unique scan ID বানাও:
        Example: SM-A105F-20260930-001
        """
        brand_clean = (brand or "UNK").replace(" ", "").upper()[:6]
        model_clean = (model or "UNK").replace(" ", "").upper()[:12]
        date_str = datetime.now().strftime("%Y%m%d")

        # আজকের কততম scan
        with _db() as c:
            prefix = f"{model_clean}-{date_str}-"
            rows = c.execute(
                "SELECT COUNT(*) FROM board_scans WHERE scan_id LIKE ?",
                (prefix + "%",)
            ).fetchone()
            count = (rows[0] if rows else 0) + 1

        return f"{model_clean}-{date_str}-{count:03d}"

    # ═════════════════════════════════════════════════════════
    # Capture Board State
    # ═════════════════════════════════════════════════════════

    def capture_state(self, brand, model, chipset="",
                      phone_serial="", board_serial="",
                      readings=None, current_draw=0,
                      symptoms=None, diagnosis="",
                      suspect_ics=None,
                      technician="", client_name="", client_phone="",
                      notes=""):
        """
        Board-এর current state capture করো।
       
        readings example:
        {
            "vbat": 3.78,
            "vph_pwr": 3.75,
            "vdd_cpu": 0.0,
            "vdd_mem": 1.12,
            "vcc_io": 1.81,
            "emmc_vcc": 3.31,
            "vcc_usb": 5.02
        }
        """
        if readings is None:
            readings = {}
        if symptoms is None:
            symptoms = []
        if suspect_ics is None:
            suspect_ics = []

        scan_id = self.generate_scan_id(brand, model)

        # BoardView + Schematic file check
        boardview_path = self._find_boardview(brand, model)
        schematic_path = self._find_schematic(brand, model)

        # Save scan to DB
        try:
            with _db() as c:
                c.execute("""
                    INSERT INTO board_scans
                    (scan_id, brand, model, chipset, phone_serial,
                     board_serial, technician, client_name, client_phone,
                     readings, current_draw, symptoms, diagnosis,
                     suspect_ics, photos, boardview_file, schematic_file,
                     notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_id, brand, model, chipset, phone_serial,
                    board_serial, technician, client_name, client_phone,
                    json.dumps(readings, ensure_ascii=False),
                    float(current_draw),
                    json.dumps(symptoms, ensure_ascii=False),
                    diagnosis,
                    json.dumps(suspect_ics, ensure_ascii=False),
                    json.dumps([]),
                    boardview_path,
                    schematic_path,
                    notes
                ))

                # Scan history log
                c.execute("""
                    INSERT INTO scan_history (scan_id, action, details)
                    VALUES (?, ?, ?)
                """, (scan_id, "scanned",
                      f"{brand} {model} — {diagnosis}"))

            self.log(f"✅ Scan saved: {scan_id}")
            return {
                "ok": True,
                "scan_id": scan_id,
                "boardview_path": boardview_path,
                "schematic_path": schematic_path,
                "message": f"Board state saved ({scan_id})"
            }

        except Exception as e:
            self.log(f"❌ Save fail: {e}")
            return {"ok": False, "message": str(e)}

    # ═════════════════════════════════════════════════════════
    # Read Existing Scan
    # ═════════════════════════════════════════════════════════

    def get_scan(self, scan_id):
        """Scan ID দিয়ে board state পড়ো"""
        try:
            with _db() as c:
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
        except Exception as e:
            self.log(f"❌ Read fail: {e}")
            return None

    def list_scans(self, brand=None, model=None, limit=100):
        """সব scan list করো (filter সহ)"""
        try:
            with _db() as c:
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
        except Exception as e:
            self.log(f"❌ List fail: {e}")
            return []

    def delete_scan(self, scan_id):
        """Scan delete করো"""
        try:
            with _db() as c:
                c.execute("DELETE FROM board_scans WHERE scan_id=?",
                          (scan_id,))
                c.execute("DELETE FROM scan_history WHERE scan_id=?",
                          (scan_id,))
            self.log(f"🗑️ Deleted: {scan_id}")
            return True
        except Exception as e:
            self.log(f"❌ Delete fail: {e}")
            return False

    def count(self):
        """মোট কতগুলো scan আছে"""
        try:
            with _db() as c:
                return c.execute(
                    "SELECT COUNT(*) FROM board_scans"
                ).fetchone()[0]
        except Exception:
            return 0

    # ═════════════════════════════════════════════════════════
    # Attach Photos to Scan
    # ═════════════════════════════════════════════════════════

    def attach_photo(self, scan_id, photo_path):
        """Scan-এ photo attach করো"""
        try:
            scan = self.get_scan(scan_id)
            if not scan:
                return False

            photos = scan.get("photos", [])
            if photo_path not in photos:
                photos.append(photo_path)

            with _db() as c:
                c.execute("""
                    UPDATE board_scans SET photos=? WHERE scan_id=?
                """, (json.dumps(photos), scan_id))

            self.log(f"📸 Photo attached: {os.path.basename(photo_path)}")
            return True
        except Exception as e:
            self.log(f"❌ Attach fail: {e}")
            return False

    # ═════════════════════════════════════════════════════════
    # BoardView + Schematic file finder
    # ═════════════════════════════════════════════════════════

    def _find_boardview(self, brand, model):
        """BoardView file খোঁজো"""
        if not brand or not model:
            return ""

        brand_clean = brand.lower().strip().replace(" ", "_")
        model_clean = model.lower().strip().replace(" ", "_")

        bv_dir = os.path.join(BOARDVIEW_DIR, brand_clean)
        if not os.path.isdir(bv_dir):
            return ""

        for ext in (".brd", ".bvr", ".tvw", ".gr", ".BRD"):
            path = os.path.join(bv_dir, f"{model_clean}{ext}")
            if os.path.exists(path):
                return path

        # Fallback: partial match
        try:
            for f in os.listdir(bv_dir):
                if model_clean.split("_")[0] in f.lower():
                    return os.path.join(bv_dir, f)
        except Exception:
            pass
        return ""

    def _find_schematic(self, brand, model):
        """Schematic file খোঁজো"""
        if not brand or not model:
            return ""

        brand_clean = brand.lower().strip().replace(" ", "_")
        model_clean = model.lower().strip().replace(" ", "_")

        sch_dir = os.path.join(SCHEMATIC_DIR, brand_clean)
        if not os.path.isdir(sch_dir):
            return ""

        for ext in (".pdf", ".png", ".jpg", ".PDF"):
            path = os.path.join(sch_dir, f"{model_clean}{ext}")
            if os.path.exists(path):
                return path

        return ""

    # ═════════════════════════════════════════════════════════
    # Compare with reference board
    # ═════════════════════════════════════════════════════════

    def find_reference_scan(self, brand, model):
        """
        একই model-এর reference (good) board খোঁজো।
        Reference = deviation_score সবচেয়ে কম
        """
        try:
            with _db() as c:
                r = c.execute("""
                    SELECT * FROM board_scans
                    WHERE brand=? AND model=?
                    ORDER BY deviation_score ASC, id ASC
                    LIMIT 1
                """, (brand, model)).fetchone()
                return dict(r) if r else None
        except Exception:
            return None

    def compare_with_reference(self, scan_id):
        """
        Current scan-কে reference-এর সাথে compare করো।
        """
        scan = self.get_scan(scan_id)
        if not scan:
            return {"ok": False, "message": "Scan not found"}

        ref = self.find_reference_scan(scan["brand"], scan["model"])
        if not ref or ref["scan_id"] == scan_id:
            return {
                "ok": True,
                "message": "No reference found — this can be reference",
                "is_reference": True,
                "deviations": []
            }

        # Parse readings
        try:
            cur = json.loads(scan.get("readings") or "{}")
            ref_r = json.loads(ref.get("readings") or "{}")
        except Exception:
            cur = {}
            ref_r = {}

        deviations = []
        for rail, val in cur.items():
            if rail not in ref_r:
                continue
            ref_val = ref_r[rail]
            if not isinstance(val, (int, float)):
                continue
            if not isinstance(ref_val, (int, float)):
                continue
            if ref_val == 0:
                continue

            # Percentage difference
            diff_pct = abs(val - ref_val) / ref_val * 100

            if diff_pct > 20:
                deviations.append({
                    "rail": rail,
                    "current": val,
                    "reference": ref_val,
                    "diff_pct": round(diff_pct, 1)
                })

        # Score
        score = min(100, len(deviations) * 15)

        return {
            "ok": True,
            "reference_scan_id": ref["scan_id"],
            "deviations": deviations,
            "deviation_score": score,
            "is_reference": False,
            "message": f"{len(deviations)} rail(s) deviate from reference"
        }