"""
State Comparator — Multiple board states compare করো।
Reference board vs current board, deviation detect।
"""

import os
import json
import sqlite3
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


class StateComparator:
    """
    দুই বা ততোধিক board scan compare করো।
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    # ═════════════════════════════════════════════════════════
    # Load Readings
    # ═════════════════════════════════════════════════════════

    def _load_readings(self, scan_id):
        """Scan থেকে readings parse করো"""
        try:
            with _db() as c:
                r = c.execute(
                    "SELECT readings FROM board_scans WHERE scan_id=?",
                    (scan_id,)
                ).fetchone()

                if not r:
                    return None
                try:
                    return json.loads(r["readings"] or "{}")
                except Exception:
                    return {}
        except Exception:
            return None

    # ═════════════════════════════════════════════════════════
    # Compare Two Scans
    # ═════════════════════════════════════════════════════════

    def compare(self, scan_id_a, scan_id_b, threshold_pct=20):
        """
        দুই scan-এর readings compare করো।

        Returns:
        {
            "ok": True,
            "scan_a": scan_id_a,
            "scan_b": scan_id_b,
            "deviations": [
                {
                    "rail": "vdd_cpu",
                    "a": 1.10,
                    "b": 0.00,
                    "diff_pct": 100.0,
                    "severity": "CRITICAL"
                }
            ],
            "summary": {...},
            "match_score": 85
        }
        """
        a = self._load_readings(scan_id_a)
        b = self._load_readings(scan_id_b)

        if a is None or b is None:
            return {"ok": False, "message": "Scan not found"}

        all_rails = set(a.keys()) | set(b.keys())
        deviations = []

        for rail in all_rails:
            va = a.get(rail)
            vb = b.get(rail)

            # Both numeric
            if not isinstance(va, (int, float)):
                continue
            if not isinstance(vb, (int, float)):
                continue

            # Baseline: higher value
            baseline = max(abs(va), abs(vb), 0.01)
            diff_pct = abs(va - vb) / baseline * 100

            if diff_pct >= threshold_pct:
                severity = self._severity(diff_pct)
                deviations.append({
                    "rail": rail,
                    "a": round(va, 3),
                    "b": round(vb, 3),
                    "diff_pct": round(diff_pct, 1),
                    "severity": severity,
                    "likely_bad": scan_id_a if va < vb else scan_id_b,
                })

        # Sort by diff_pct desc
        deviations.sort(key=lambda x: x["diff_pct"], reverse=True)

        # Match score
        total = len(all_rails) if all_rails else 1
        matching = total - len(deviations)
        match_score = round(matching / total * 100, 1)

        return {
            "ok": True,
            "scan_a": scan_id_a,
            "scan_b": scan_id_b,
            "deviations": deviations,
            "total_rails": total,
            "matching_rails": matching,
            "match_score": match_score,
            "summary": self._summary(deviations),
        }

    def _severity(self, diff_pct):
        if diff_pct >= 80:
            return "CRITICAL"
        elif diff_pct >= 50:
            return "HIGH"
        elif diff_pct >= 30:
            return "MEDIUM"
        else:
            return "LOW"

    def _summary(self, deviations):
        """Deviation summary"""
        critical = sum(1 for d in deviations if d["severity"] == "CRITICAL")
        high = sum(1 for d in deviations if d["severity"] == "HIGH")
        medium = sum(1 for d in deviations if d["severity"] == "MEDIUM")
        low = sum(1 for d in deviations if d["severity"] == "LOW")

        if critical:
            verdict = "🔴 Critical differences found"
        elif high:
            verdict = "🟠 High differences"
        elif medium:
            verdict = "🟡 Medium differences"
        elif low:
            verdict = "🟢 Minor differences"
        else:
            verdict = "✅ Boards match"

        return {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "verdict": verdict,
        }

    # ═════════════════════════════════════════════════════════
    # Compare with Reference
    # ═════════════════════════════════════════════════════════

    def compare_with_reference(self, scan_id):
        """
        Scan-টা একই model-এর reference (best) board-এর সাথে compare।
        """
        # Get scan
        try:
            with _db() as c:
                scan = c.execute(
                    "SELECT * FROM board_scans WHERE scan_id=?",
                    (scan_id,)
                ).fetchone()

                if not scan:
                    return {"ok": False, "message": "Scan not found"}

                # Find reference (best deviation_score = 0 or lowest)
                ref = c.execute("""
                    SELECT scan_id FROM board_scans
                    WHERE brand=? AND model=? AND scan_id != ?
                    ORDER BY deviation_score ASC, id ASC
                    LIMIT 1
                """, (scan["brand"], scan["model"], scan_id)).fetchone()

        except Exception as e:
            return {"ok": False, "message": str(e)}

        if not ref:
            return {
                "ok": True,
                "is_reference": True,
                "message": "No reference found — this board is now reference",
                "deviations": [],
                "match_score": 100,
            }

        result = self.compare(ref["scan_id"], scan_id)
        result["is_reference"] = False
        result["reference_scan_id"] = ref["scan_id"]
        return result

    # ═════════════════════════════════════════════════════════
    # Multi-scan Compare (3+ boards)
    # ═════════════════════════════════════════════════════════

    def compare_many(self, scan_ids):
        """
        Multiple boards compare করো।
        Baseline = most common values across all boards.
        """
        if len(scan_ids) < 2:
            return {"ok": False, "message": "Need at least 2 scans"}

        all_readings = {}
        for sid in scan_ids:
            r = self._load_readings(sid)
            if r is not None:
                all_readings[sid] = r

        if len(all_readings) < 2:
            return {"ok": False, "message": "Too few valid scans"}

        # Aggregate rails
        rails = set()
        for r in all_readings.values():
            rails.update(r.keys())

        # Find baseline per rail (most common value range)
        baseline = {}
        for rail in rails:
            values = []
            for r in all_readings.values():
                v = r.get(rail)
                if isinstance(v, (int, float)) and v > 0:
                    values.append(v)
            if values:
                baseline[rail] = sum(values) / len(values)

        # Per-board deviation
        per_board = {}
        for sid, r in all_readings.items():
            devs = []
            for rail, v in r.items():
                if not isinstance(v, (int, float)):
                    continue
                bv = baseline.get(rail)
                if not bv:
                    continue
                diff_pct = abs(v - bv) / bv * 100
                if diff_pct >= 20:
                    devs.append({
                        "rail": rail,
                        "value": round(v, 3),
                        "baseline": round(bv, 3),
                        "diff_pct": round(diff_pct, 1),
                    })
            per_board[sid] = {
                "deviations": devs,
                "deviation_count": len(devs),
            }

        return {
            "ok": True,
            "boards_count": len(per_board),
            "baseline": {k: round(v, 3) for k, v in baseline.items()},
            "per_board": per_board,
            "total_rails": len(rails),
        }

    # ═════════════════════════════════════════════════════════
    # Set Reference
    # ═════════════════════════════════════════════════════════

    def mark_as_reference(self, scan_id):
        """
        একটা scan-কে reference হিসেবে mark করো (deviation_score = 0)।
        """
        try:
            with _db() as c:
                c.execute("""
                    UPDATE board_scans
                    SET deviation_score=0, notes=notes || '[REFERENCE]'
                    WHERE scan_id=?
                """, (scan_id,))

            self.log(f"✅ Marked as reference: {scan_id}")
            return True
        except Exception as e:
            self.log(f"❌ Mark fail: {e}")
            return False