"""
History Manager — Board scan timeline, model-wise history, statistics.
প্রতিটা scan action track করে, timeline বানায়।
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB = os.path.join(ROOT, "database", "devices.db")


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


class HistoryManager:
    """
    Scan history — timeline, model-wise, brand-wise
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    # ═════════════════════════════════════════════════════════
    # Timeline
    # ═════════════════════════════════════════════════════════

    def get_timeline(self, days=30, limit=200):
        """
        শেষ N দিনের সব scan action timeline।
        """
        since = (datetime.now() - timedelta(days=days)).isoformat()

        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT sh.*, bs.brand, bs.model, bs.diagnosis
                    FROM scan_history sh
                    LEFT JOIN board_scans bs ON bs.scan_id = sh.scan_id
                    WHERE sh.ts >= ?
                    ORDER BY sh.id DESC
                    LIMIT ?
                """, (since, limit)).fetchall()

                return [dict(r) for r in rows]
        except Exception as e:
            self.log(f"❌ Timeline fail: {e}")
            return []

    def get_scan_events(self, scan_id):
        """একটা scan-এর সব events"""
        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT * FROM scan_history
                    WHERE scan_id=?
                    ORDER BY id ASC
                """, (scan_id,)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    # ═════════════════════════════════════════════════════════
    # Model-wise History
    # ═════════════════════════════════════════════════════════

    def model_history(self, brand, model, limit=50):
        """
        একই model-এর সব scan — chronological।
        """
        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT scan_id, ts, chipset, diagnosis,
                           current_draw, deviation_score, technician
                    FROM board_scans
                    WHERE brand=? AND model=?
                    ORDER BY id DESC LIMIT ?
                """, (brand, model, limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def brand_history(self, brand, limit=100):
        """
        একই brand-এর সব scan।
        """
        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT scan_id, ts, model, chipset, diagnosis,
                           current_draw, technician
                    FROM board_scans
                    WHERE brand=?
                    ORDER BY id DESC LIMIT ?
                """, (brand, limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    # ═════════════════════════════════════════════════════════
    # Statistics
    # ═════════════════════════════════════════════════════════

    def stats(self):
        """
        Overall statistics:
        - Total scans
        - Brand-wise count
        - Model-wise top
        - Recent 7 days
        """
        result = {
            "total_scans": 0,
            "total_boardviews": 0,
            "brand_wise": [],
            "model_wise": [],
            "recent_week": 0,
        }

        try:
            with _db() as c:
                # Total scans
                result["total_scans"] = c.execute(
                    "SELECT COUNT(*) FROM board_scans"
                ).fetchone()[0]

                # Total boardviews
                result["total_boardviews"] = c.execute(
                    "SELECT COUNT(*) FROM boardview_files"
                ).fetchone()[0]

                # Brand-wise
                rows = c.execute("""
                    SELECT brand, COUNT(*) AS n FROM board_scans
                    WHERE brand IS NOT NULL
                    GROUP BY brand ORDER BY n DESC
                """).fetchall()
                result["brand_wise"] = [dict(r) for r in rows]

                # Top models
                rows = c.execute("""
                    SELECT brand, model, COUNT(*) AS n FROM board_scans
                    WHERE brand IS NOT NULL AND model IS NOT NULL
                    GROUP BY brand, model ORDER BY n DESC LIMIT 10
                """).fetchall()
                result["model_wise"] = [dict(r) for r in rows]

                # Recent week
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                result["recent_week"] = c.execute("""
                    SELECT COUNT(*) FROM board_scans WHERE ts >= ?
                """, (week_ago,)).fetchone()[0]

        except Exception as e:
            self.log(f"❌ Stats fail: {e}")

        return result

    # ═════════════════════════════════════════════════════════
    # Search
    # ═════════════════════════════════════════════════════════

    def search_scans(self, query="", limit=100):
        """
        Query দিয়ে scan খোঁজো (brand/model/serial/diagnosis)।
        """
        try:
            with _db() as c:
                q = f"%{query}%"
                rows = c.execute("""
                    SELECT * FROM board_scans
                    WHERE brand LIKE ?
                       OR model LIKE ?
                       OR phone_serial LIKE ?
                       OR board_serial LIKE ?
                       OR diagnosis LIKE ?
                       OR client_name LIKE ?
                       OR client_phone LIKE ?
                    ORDER BY id DESC LIMIT ?
                """, (q, q, q, q, q, q, q, limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    # ═════════════════════════════════════════════════════════
    # Cleanup
    # ═════════════════════════════════════════════════════════

    def cleanup_old_history(self, days=180):
        """
        পুরনো scan_history delete করো (board_scans থাকবে)।
        Default: ১৮০ দিনের বেশি পুরনো।
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        try:
            with _db() as c:
                c.execute("""
                    DELETE FROM scan_history WHERE ts < ?
                """, (cutoff,))
                count = c.total_changes

            self.log(f"🗑️ Cleaned {count} old history entries")
            return count
        except Exception as e:
            self.log(f"❌ Cleanup fail: {e}")
            return 0

    # ═════════════════════════════════════════════════════════
    # Export
    # ═════════════════════════════════════════════════════════

    def export_csv(self, output_path=None):
        """
        সব scan data CSV তে export করো।
        """
        import csv

        if output_path is None:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = os.path.join(ROOT, "reports", "exports")
            os.makedirs(export_dir, exist_ok=True)
            output_path = os.path.join(export_dir,
                                       f"scans_{date_str}.csv")

        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT scan_id, ts, brand, model, chipset,
                           phone_serial, board_serial, technician,
                           client_name, client_phone, current_draw,
                           diagnosis, notes
                    FROM board_scans
                    ORDER BY id DESC
                """).fetchall()

            with open(output_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Scan ID", "Timestamp", "Brand", "Model", "Chipset",
                    "Phone Serial", "Board Serial", "Technician",
                    "Client", "Phone", "Current (mA)", "Diagnosis", "Notes"
                ])
                for r in rows:
                    writer.writerow([
                        r["scan_id"], r["ts"], r["brand"], r["model"],
                        r["chipset"], r["phone_serial"], r["board_serial"],
                        r["technician"], r["client_name"], r["client_phone"],
                        r["current_draw"], r["diagnosis"], r["notes"]
                    ])

            self.log(f"✅ Exported: {output_path}")
            return output_path
        except Exception as e:
            self.log(f"❌ Export fail: {e}")
            return None