"""
BoardView Manager — .brd/.pdf file registry + viewer helper
"""

import os
import sqlite3
import subprocess
import platform
from datetime import datetime
from contextlib import contextmanager


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB = os.path.join(ROOT, "database", "devices.db")
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


class BoardViewManager:
    """
    BoardView + Schematic file management।
    - Registry (DB-তে save)
    - Finder (brand/model দিয়ে খোঁজা)
    - External viewer (BoardViewer, PDF reader)
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print
        os.makedirs(BOARDVIEW_DIR, exist_ok=True)
        os.makedirs(SCHEMATIC_DIR, exist_ok=True)

    # ═════════════════════════════════════════════════════════
    # Register
    # ═════════════════════════════════════════════════════════

    def register(self, brand, model, board_number, file_path,
                 file_type="brd", source="manual",
                 license_status="personal", notes=""):
        """BoardView file register করো"""
        if not os.path.exists(file_path):
            self.log(f"❌ File not found: {file_path}")
            return False

        try:
            size = os.path.getsize(file_path)
        except Exception:
            size = 0

        try:
            with _db() as c:
                c.execute("""
                    INSERT OR REPLACE INTO boardview_files
                    (brand, model, board_number, file_path, file_type,
                     file_size, source, license_status, notes, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (brand, model, board_number, file_path, file_type,
                      size, source, license_status, notes))

            self.log(f"✅ Registered: {brand} {model} ({file_type})")
            return True
        except Exception as e:
            self.log(f"❌ Register fail: {e}")
            return False

    def unregister(self, file_id):
        """Registry থেকে remove করো (actual file মুছবে না)"""
        try:
            with _db() as c:
                c.execute("DELETE FROM boardview_files WHERE id=?",
                          (file_id,))
            return True
        except Exception:
            return False

    # ═════════════════════════════════════════════════════════
    # Find
    # ═════════════════════════════════════════════════════════

    def find(self, brand, model):
        """DB + filesystem — both check"""
        # DB first
        try:
            with _db() as c:
                r = c.execute("""
                    SELECT * FROM boardview_files
                    WHERE brand=? AND model=?
                    ORDER BY id DESC LIMIT 1
                """, (brand, model)).fetchone()

                if r and os.path.exists(r["file_path"]):
                    return dict(r)
        except Exception:
            pass

        # Filesystem fallback
        brand_clean = (brand or "").lower().strip().replace(" ", "_")
        model_clean = (model or "").lower().strip().replace(" ", "_")

        bv_dir = os.path.join(BOARDVIEW_DIR, brand_clean)
        if not os.path.isdir(bv_dir):
            return None

        for ext in (".brd", ".bvr", ".tvw", ".gr", ".BRD", ".BVR"):
            path = os.path.join(bv_dir, f"{model_clean}{ext}")
            if os.path.exists(path):
                return {
                    "brand": brand,
                    "model": model,
                    "file_path": path,
                    "file_type": ext[1:].lower(),
                    "file_size": os.path.getsize(path),
                    "source": "filesystem",
                    "license_status": "personal",
                }
        return None

    def find_schematic(self, brand, model):
        """Schematic file খোঁজো"""
        brand_clean = (brand or "").lower().strip().replace(" ", "_")
        model_clean = (model or "").lower().strip().replace(" ", "_")

        sch_dir = os.path.join(SCHEMATIC_DIR, brand_clean)
        if not os.path.isdir(sch_dir):
            return None

        for ext in (".pdf", ".PDF", ".png", ".jpg"):
            path = os.path.join(sch_dir, f"{model_clean}{ext}")
            if os.path.exists(path):
                return {
                    "file_path": path,
                    "file_type": ext[1:].lower(),
                    "file_size": os.path.getsize(path),
                }
        return None

    # ═════════════════════════════════════════════════════════
    # List / Stats
    # ═════════════════════════════════════════════════════════

    def list_all(self, brand=None, limit=500):
        """সব registered files"""
        try:
            with _db() as c:
                if brand:
                    rows = c.execute("""
                        SELECT * FROM boardview_files
                        WHERE brand=?
                        ORDER BY brand, model LIMIT ?
                    """, (brand, limit)).fetchall()
                else:
                    rows = c.execute("""
                        SELECT * FROM boardview_files
                        ORDER BY brand, model LIMIT ?
                    """, (limit,)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def count(self):
        try:
            with _db() as c:
                return c.execute(
                    "SELECT COUNT(*) FROM boardview_files"
                ).fetchone()[0]
        except Exception:
            return 0

    def brands_summary(self):
        """Brand-wise file count"""
        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT brand, COUNT(*) AS n FROM boardview_files
                    GROUP BY brand ORDER BY n DESC
                """).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    # ═════════════════════════════════════════════════════════
    # Open External Viewer
    # ═════════════════════════════════════════════════════════

    def open_file(self, file_path):
        """
        File-টা system default app-এ open করো।
        - .brd → BoardViewer / OpenBoardView
        - .pdf → PDF reader
        - .png/.jpg → Image viewer
        """
        if not os.path.exists(file_path):
            self.log(f"❌ File not found: {file_path}")
            return False

        try:
            system = platform.system()

            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", file_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", file_path])

            self.log(f"🔍 Opened: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            self.log(f"❌ Open fail: {e}")
            return False

    def scan_folder(self, brand, auto_register=True):
        """
        Brand folder scan করো → সব file register করো।
        """
        brand_clean = (brand or "").lower().strip().replace(" ", "_")
        bv_dir = os.path.join(BOARDVIEW_DIR, brand_clean)
        if not os.path.isdir(bv_dir):
            self.log(f"❌ Folder not found: {bv_dir}")
            return 0

        count = 0
        for fname in os.listdir(bv_dir):
            fpath = os.path.join(bv_dir, fname)
            if not os.path.isfile(fpath):
                continue

            ext = os.path.splitext(fname)[1].lower()
            if ext not in (".brd", ".bvr", ".tvw", ".gr"):
                continue

            if auto_register:
                model = os.path.splitext(fname)[0]
                self.register(
                    brand=brand,
                    model=model,
                    board_number=model,
                    file_path=fpath,
                    file_type=ext[1:],
                    source="folder_scan"
                )
                count += 1

        self.log(f"✅ Scanned {count} files in {brand}")
        return count