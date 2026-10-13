"""
MASTER FILE CREATOR
Creates all missing .py files for Mobile Service Master
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = {}

# ═══════════════════════════════════════════════════════════
# 1. SCANNER MODULE — Motherboard scan + IC diagnosis
# ═══════════════════════════════════════════════════════════

FILES["core/scanner/board_scanner.py"] = '''"""Board Scanner — Motherboard state capture + IC diagnosis"""
import os
import json
import sqlite3
from datetime import datetime
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


class BoardScanner:
    """Motherboard scanner — state capture, IC diagnosis, comparison"""

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def generate_scan_id(self, brand, model):
        """Generate unique scan ID"""
        b = (brand or "UNK").replace(" ", "").upper()[:6]
        m = (model or "UNK").replace(" ", "").upper()[:12]
        date = datetime.now().strftime("%Y%m%d")
        with _db() as c:
            prefix = f"{m}-{date}-"
            row = c.execute(
                "SELECT COUNT(*) FROM board_scans WHERE scan_id LIKE ?",
                (prefix + "%",)
            ).fetchone()
            count = (row[0] if row else 0) + 1
        return f"{m}-{date}-{count:03d}"

    def capture_state(self, brand, model, chipset="", phone_serial="",
                      readings=None, current_draw=0, symptoms=None,
                      diagnosis="", suspect_ics=None, technician="",
                      client_name="", client_phone="", notes=""):
        """Capture motherboard state"""
        if readings is None:
            readings = {}
        if symptoms is None:
            symptoms = []
        if suspect_ics is None:
            suspect_ics = []

        scan_id = self.generate_scan_id(brand, model)

        try:
            with _db() as c:
                c.execute("""
                    INSERT INTO board_scans
                    (scan_id, brand, model, chipset, phone_serial, technician,
                     client_name, client_phone, readings, current_draw,
                     symptoms, diagnosis, suspect_ics, photos, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_id, brand, model, chipset, phone_serial, technician,
                    client_name, client_phone,
                    json.dumps(readings), float(current_draw),
                    json.dumps(symptoms), diagnosis,
                    json.dumps(suspect_ics), json.dumps([]), notes
                ))
                c.execute("""
                    INSERT INTO scan_history (scan_id, action, details)
                    VALUES (?, ?, ?)
                """, (scan_id, "scanned",
                      f"{brand} {model} - {diagnosis}"))

            self.log(f"Scan saved: {scan_id}")
            return {"ok": True, "scan_id": scan_id,
                    "message": f"Board state saved ({scan_id})"}
        except Exception as e:
            self.log(f"Save fail: {e}")
            return {"ok": False, "message": str(e)}

    def get_scan(self, scan_id):
        """Get scan by ID"""
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
        except Exception:
            return None

    def list_scans(self, brand=None, model=None, limit=100):
        """List scans"""
        try:
            with _db() as c:
                if brand and model:
                    rows = c.execute(
                        "SELECT * FROM board_scans WHERE brand=? AND model=? ORDER BY id DESC LIMIT ?",
                        (brand, model, limit)
                    ).fetchall()
                elif brand:
                    rows = c.execute(
                        "SELECT * FROM board_scans WHERE brand=? ORDER BY id DESC LIMIT ?",
                        (brand, limit)
                    ).fetchall()
                else:
                    rows = c.execute(
                        "SELECT * FROM board_scans ORDER BY id DESC LIMIT ?",
                        (limit,)
                    ).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def delete_scan(self, scan_id):
        """Delete scan"""
        try:
            with _db() as c:
                c.execute("DELETE FROM board_scans WHERE scan_id=?", (scan_id,))
                c.execute("DELETE FROM scan_history WHERE scan_id=?", (scan_id,))
            return True
        except Exception:
            return False

    def count(self):
        try:
            with _db() as c:
                return c.execute("SELECT COUNT(*) FROM board_scans").fetchone()[0]
        except Exception:
            return 0
'''

FILES["core/scanner/boardview_manager.py"] = '''"""BoardView Manager — .brd/.pdf file registry"""
import os
import sqlite3
import subprocess
import platform
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
    def __init__(self, log_callback=None):
        self.log = log_callback or print
        os.makedirs(BOARDVIEW_DIR, exist_ok=True)
        os.makedirs(SCHEMATIC_DIR, exist_ok=True)

    def register(self, brand, model, board_number="", file_path="",
                 file_type="brd", source="manual",
                 license_status="personal", notes=""):
        if not os.path.exists(file_path):
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
            return True
        except Exception as e:
            self.log(f"Register fail: {e}")
            return False

    def unregister(self, file_id):
        try:
            with _db() as c:
                c.execute("DELETE FROM boardview_files WHERE id=?", (file_id,))
            return True
        except Exception:
            return False

    def find(self, brand, model):
        try:
            with _db() as c:
                r = c.execute("""
                    SELECT * FROM boardview_files WHERE brand=? AND model=?
                    ORDER BY id DESC LIMIT 1
                """, (brand, model)).fetchone()
                if r and os.path.exists(r["file_path"]):
                    return dict(r)
        except Exception:
            pass
        # Filesystem fallback
        b = (brand or "").lower().strip().replace(" ", "_")
        m = (model or "").lower().strip().replace(" ", "_")
        d = os.path.join(BOARDVIEW_DIR, b)
        if os.path.isdir(d):
            for ext in (".brd", ".bvr", ".tvw", ".gr"):
                p = os.path.join(d, f"{m}{ext}")
                if os.path.exists(p):
                    return {"brand": brand, "model": model,
                            "file_path": p, "file_type": ext[1:],
                            "file_size": os.path.getsize(p)}
        return None

    def find_schematic(self, brand, model):
        b = (brand or "").lower().strip().replace(" ", "_")
        m = (model or "").lower().strip().replace(" ", "_")
        d = os.path.join(SCHEMATIC_DIR, b)
        if os.path.isdir(d):
            for ext in (".pdf", ".png", ".jpg"):
                p = os.path.join(d, f"{m}{ext}")
                if os.path.exists(p):
                    return {"file_path": p, "file_type": ext[1:],
                            "file_size": os.path.getsize(p)}
        return None

    def list_all(self, brand=None, limit=500):
        try:
            with _db() as c:
                if brand:
                    rows = c.execute(
                        "SELECT * FROM boardview_files WHERE brand=? LIMIT ?",
                        (brand, limit)
                    ).fetchall()
                else:
                    rows = c.execute(
                        "SELECT * FROM boardview_files LIMIT ?", (limit,)
                    ).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def count(self):
        try:
            with _db() as c:
                return c.execute("SELECT COUNT(*) FROM boardview_files").fetchone()[0]
        except Exception:
            return 0

    def open_file(self, file_path):
        if not os.path.exists(file_path):
            return False
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
            return True
        except Exception:
            return False
'''

FILES["core/scanner/history_manager.py"] = '''"""History Manager — Board scan timeline + stats"""
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
    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def get_timeline(self, days=30, limit=200):
        since = (datetime.now() - timedelta(days=days)).isoformat()
        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT sh.*, bs.brand, bs.model, bs.diagnosis
                    FROM scan_history sh
                    LEFT JOIN board_scans bs ON bs.scan_id = sh.scan_id
                    WHERE sh.ts >= ?
                    ORDER BY sh.id DESC LIMIT ?
                """, (since, limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def get_scan_events(self, scan_id):
        try:
            with _db() as c:
                rows = c.execute(
                    "SELECT * FROM scan_history WHERE scan_id=? ORDER BY id ASC",
                    (scan_id,)
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def model_history(self, brand, model, limit=50):
        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT scan_id, ts, chipset, diagnosis, technician
                    FROM board_scans WHERE brand=? AND model=?
                    ORDER BY id DESC LIMIT ?
                """, (brand, model, limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def stats(self):
        result = {"total_scans": 0, "total_boardviews": 0,
                  "brand_wise": [], "recent_week": 0}
        try:
            with _db() as c:
                result["total_scans"] = c.execute(
                    "SELECT COUNT(*) FROM board_scans"
                ).fetchone()[0]
                result["total_boardviews"] = c.execute(
                    "SELECT COUNT(*) FROM boardview_files"
                ).fetchone()[0]
                rows = c.execute("""
                    SELECT brand, COUNT(*) AS n FROM board_scans
                    WHERE brand IS NOT NULL GROUP BY brand ORDER BY n DESC
                """).fetchall()
                result["brand_wise"] = [dict(r) for r in rows]
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                result["recent_week"] = c.execute(
                    "SELECT COUNT(*) FROM board_scans WHERE ts >= ?",
                    (week_ago,)
                ).fetchone()[0]
        except Exception as e:
            self.log(f"Stats fail: {e}")
        return result

    def search_scans(self, query="", limit=100):
        try:
            with _db() as c:
                q = f"%{query}%"
                rows = c.execute("""
                    SELECT * FROM board_scans
                    WHERE brand LIKE ? OR model LIKE ? OR phone_serial LIKE ?
                       OR diagnosis LIKE ? OR client_name LIKE ?
                    ORDER BY id DESC LIMIT ?
                """, (q, q, q, q, q, limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def export_csv(self, output_path=None):
        import csv
        if not output_path:
            date = datetime.now().strftime("%Y%m%d_%H%M%S")
            d = os.path.join(ROOT, "reports", "exports")
            os.makedirs(d, exist_ok=True)
            output_path = os.path.join(d, f"scans_{date}.csv")
        try:
            with _db() as c:
                rows = c.execute("""
                    SELECT scan_id, ts, brand, model, chipset,
                           phone_serial, technician, client_name,
                           diagnosis, notes FROM board_scans ORDER BY id DESC
                """).fetchall()
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["Scan ID", "Time", "Brand", "Model", "Chipset",
                            "Serial", "Technician", "Client", "Diagnosis", "Notes"])
                for r in rows:
                    w.writerow([r[k] for k in r.keys()])
            return output_path
        except Exception as e:
            self.log(f"Export fail: {e}")
            return None
'''

FILES["core/scanner/state_comparator.py"] = '''"""State Comparator — Compare multiple board states"""
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
    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def _load_readings(self, scan_id):
        try:
            with _db() as c:
                r = c.execute(
                    "SELECT readings FROM board_scans WHERE scan_id=?",
                    (scan_id,)
                ).fetchone()
                if not r:
                    return None
                return json.loads(r["readings"] or "{}")
        except Exception:
            return None

    def compare(self, scan_a, scan_b, threshold_pct=20):
        a = self._load_readings(scan_a)
        b = self._load_readings(scan_b)
        if a is None or b is None:
            return {"ok": False, "message": "Scan not found"}

        all_rails = set(a.keys()) | set(b.keys())
        deviations = []
        for rail in all_rails:
            va, vb = a.get(rail), b.get(rail)
            if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
                continue
            baseline = max(abs(va), abs(vb), 0.01)
            diff_pct = abs(va - vb) / baseline * 100
            if diff_pct >= threshold_pct:
                severity = "CRITICAL" if diff_pct >= 80 else (
                    "HIGH" if diff_pct >= 50 else (
                        "MEDIUM" if diff_pct >= 30 else "LOW"))
                deviations.append({
                    "rail": rail, "a": round(va, 3), "b": round(vb, 3),
                    "diff_pct": round(diff_pct, 1), "severity": severity,
                })
        deviations.sort(key=lambda x: x["diff_pct"], reverse=True)

        total = len(all_rails) if all_rails else 1
        match_score = round((total - len(deviations)) / total * 100, 1)

        return {
            "ok": True, "scan_a": scan_a, "scan_b": scan_b,
            "deviations": deviations, "total_rails": total,
            "match_score": match_score,
        }

    def compare_with_reference(self, scan_id):
        try:
            with _db() as c:
                scan = c.execute(
                    "SELECT * FROM board_scans WHERE scan_id=?", (scan_id,)
                ).fetchone()
                if not scan:
                    return {"ok": False, "message": "Scan not found"}
                ref = c.execute("""
                    SELECT scan_id FROM board_scans
                    WHERE brand=? AND model=? AND scan_id != ?
                    ORDER BY id ASC LIMIT 1
                """, (scan["brand"], scan["model"], scan_id)).fetchone()
        except Exception as e:
            return {"ok": False, "message": str(e)}

        if not ref:
            return {"ok": True, "is_reference": True,
                    "message": "No reference", "deviations": [],
                    "match_score": 100}

        result = self.compare(ref["scan_id"], scan_id)
        result["is_reference"] = False
        result["reference_scan_id"] = ref["scan_id"]
        return result

    def mark_as_reference(self, scan_id):
        try:
            with _db() as c:
                c.execute("""
                    UPDATE board_scans SET deviation_score=0,
                    notes = notes || '[REFERENCE]'
                    WHERE scan_id=?
                """, (scan_id,))
            return True
        except Exception:
            return False
'''

FILES["core/scanner/__init__.py"] = '''"""Scanner package"""
from .board_scanner import BoardScanner
from .boardview_manager import BoardViewManager
from .history_manager import HistoryManager
from .state_comparator import StateComparator

__all__ = ["BoardScanner", "BoardViewManager", "HistoryManager", "StateComparator"]
'''

# ═══════════════════════════════════════════════════════════
# 2. CHART / DIAGRAM MODULE
# ═══════════════════════════════════════════════════════════

FILES["core/chart_generator.py"] = '''"""Chart Generator — System diagrams for brands and diagnosis"""
import os
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))


def generate_brand_tree(brand_data):
    """Generate ASCII tree for a brand"""
    lines = []
    lines.append(f"📱 {brand_data.get('name', '?')}")
    lines.append(f"├── Status: {brand_data.get('status', '?')}")
    lines.append(f"├── Country: {brand_data.get('country', '?')}")

    series = brand_data.get("series", [])
    if series:
        lines.append(f"├── Series ({len(series)}):")
        for i, s in enumerate(series):
            prefix = "│   └──" if i == len(series) - 1 else "│   ├──"
            lines.append(f"{prefix} {s}")

    markets = brand_data.get("markets", [])
    if markets:
        lines.append(f"├── Markets ({len(markets)}): {', '.join(markets[:5])}")

    tool = brand_data.get("flashing_tool", "?")
    lines.append(f"└── ⚡ Flashing: {tool}")

    return "\\n".join(lines)


def generate_mermaid_brand(brand_data):
    """Generate Mermaid.js diagram code"""
    name = brand_data.get("name", "?").replace(" ", "_")
    lines = [f"graph TD", f"  {name}[\\"{brand_data.get('name', '?')}\\"]"]

    for i, series in enumerate(brand_data.get("series", [])[:6]):
        s_id = f"{name}_S{i}"
        lines.append(f"  {name} --> {s_id}[\\"{series}\\"]")

    tool = brand_data.get("flashing_tool", "")
    if tool:
        lines.append(f"  {name} --> {name}_T[\\"⚡ {tool}\\"]")

    return "\\n".join(lines)


def generate_brand_html_chart(brand_data):
    """Generate HTML chart for one brand"""
    name = brand_data.get("name", "?")
    series = brand_data.get("series", [])
    markets = brand_data.get("markets", [])
    tool = brand_data.get("flashing_tool", "")
    status = brand_data.get("status", "")

    html = f'''
    <div class="brand-chart-card">
      <div class="brand-chart-header">
        <h3>{name}</h3>
        <span class="status {'active' if status == 'active' else 'disc'}">{status}</span>
      </div>
      <div class="brand-chart-row">
        <div class="brand-chart-col">
          <div class="brand-chart-label">Series</div>
          <ul>{''.join(f'<li>{s}</li>' for s in series[:8])}</ul>
        </div>
        <div class="brand-chart-col">
          <div class="brand-chart-label">Markets</div>
          <ul>{''.join(f'<li>{m}</li>' for m in markets[:6])}</ul>
        </div>
        <div class="brand-chart-col">
          <div class="brand-chart-label">Flashing</div>
          <div class="flashing-tool">⚡ {tool}</div>
        </div>
      </div>
    </div>
    '''
    return html


def generate_diagnosis_flow(issue_type="software"):
    """Generate diagnosis flow chart"""
    if issue_type == "software":
        return """
        graph TD
            Start[Phone Problem] --> Q{Device Connect?}
            Q -->|Yes| ADB[ADB Detect]
            Q -->|No| Photo[Photo Upload]
            ADB --> Symptoms[Analyze Symptoms]
            Photo --> OCR[OCR + Database]
            Symptoms --> Diag{Issue Type?}
            OCR --> Diag
            Diag -->|Software| AutoSolver[Auto Solve]
            Diag -->|Hardware| Guide[Hardware Guide]
            AutoSolver --> Fix{Fixed?}
            Fix -->|Yes| Report[Generate Report]
            Fix -->|No| Guide
            Guide --> Report
        """
    else:
        return """
        graph TD
            Start[Photo Upload] --> OCR[OCR Analysis]
            OCR --> Rail[Rail Detection]
            Rail --> Compare[Database Compare]
            Compare --> Verdict{Verdict}
            Verdict -->|OK| Connected[CONNECTED]
            Verdict -->|Warning| Warning[INVESTIGATE]
            Verdict -->|Critical| Critical[HARDWARE FAULT]
            Critical --> Report[Report]
            Warning --> Report
            Connected --> Report
        '''


def create_diagnosis_html():
    """Create complete diagnosis chart HTML"""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mobile Service Master — Diagnosis System</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Segoe UI",Arial,sans-serif;background:#0f172a;color:#e2e8f0;padding:24px}
h1{color:#38bdf8;text-align:center;margin-bottom:8px}
.sub{text-align:center;color:#94a3b8;margin-bottom:30px}
.section{background:#1e293b;border-radius:12px;padding:24px;margin-bottom:24px;border-left:4px solid #38bdf8}
.section h2{color:#f1f5f9;font-size:18px;margin-bottom:16px}
.mermaid{background:#0f172a;padding:20px;border-radius:8px;text-align:center}
.legend{display:flex;gap:20px;flex-wrap:wrap;margin-top:16px;padding-top:16px;border-top:1px solid #334155}
.legend-item{display:flex;align-items:center;gap:8px;font-size:13px;color:#cbd5e1}
.legend-dot{width:12px;height:12px;border-radius:50%}
.dot-blue{background:#38bdf8}.dot-green{background:#22c55e}.dot-yellow{background:#f59e0b}.dot-red{background:#ef4444}
</style>
</head>
<body>
<div class="container" style="max-width:1200px;margin:0 auto;">
  <h1>🔧 Mobile Service Master — Diagnosis System</h1>
  <p class="sub">Complete flowchart for software + hardware problem detection</p>

  <div class="section">
    <h2>📊 System Architecture Flow</h2>
    <div class="mermaid">
      graph TB
        User[Technician] --> Login[Login + OTP]
        Login --> Dash[9-Tab Dashboard]
        Dash --> USB[USB Connect]
        Dash --> Photo[Photo Upload]

        USB --> ADB[ADB Manager]
        ADB --> Detect[Device Detect]
        Detect --> Analyzer[Analyzer]

        Photo --> OCR[OCR Reader]
        OCR --> Engine[Meter Engine]
        Engine --> Rail[Rail Extractor]
        Rail --> Database[(Database)]
        Database --> Validator[Cross Validator]

        Analyzer --> Diag{Issue Type}
        Validator --> Diag
        Diag -->|Software| Solver[Auto Solver]
        Diag -->|Hardware| Guide[Hardware Guide]
        Diag -->|Account| Lock[Owner Verify]

        Solver --> Report[Report Generator]
        Guide --> Report
        Lock --> Report
        Report --> Customer[Customer Display]
    </div>
  </div>

  <div class="section">
    <h2>💊 Software Problem Flow</h2>
    <div class="mermaid">
      graph LR
        Problem[Phone Problem] --> Connect{Can Connect?}
        Connect -->|Yes| ADB[USB/ADB]
        Connect -->|No| Photo[Photo Upload]
        ADB --> Detect[Device Detect]
        Photo --> OCR[OCR Analysis]
        Detect --> Symptoms[Symptom Check]
        OCR --> Match[Database Match]
        Symptoms --> Diag[Diagnosis]
        Match --> Diag
        Diag --> Auto[Auto Solve]
        Auto --> Result{Success?}
        Result -->|Yes| Done[Report + Fix]
        Result -->|No| Manual[Manual Guide]
        Manual --> Done
    </div>
  </div>

  <div class="section">
    <h2>🔧 Hardware Problem Flow</h2>
    <div class="mermaid">
      graph LR
        Customer[Customer Phone] --> Dead{Phone State?}
        Dead -->|Dead| EDL[EDL/MTK Mode]
        Dead -->|Boot Loop| Recovery[Recovery Mode]
        Dead -->|Screen Broken| OTG[OTG Mouse]
        EDL --> Rails[Rail Check]
        Recovery --> Cache[Cache Wipe]
        OTG --> Options[Developer Options]
        Rails --> IC[IC Diagnosis]
        Cache --> IC
        Options --> USB[USB Access]
        IC --> Report[Hardware Report]
        USB --> Report
        Report --> Repair[Repair Guidance]
    </div>
  </div>

  <div class="section">
    <h2>📸 Photo Connect Flow</h2>
    <div class="mermaid">
      graph LR
        Photo1[Analogue Meter] --> Upload[4-Photo Upload]
        Photo2[Multimeter] --> Upload
        Photo3[DC Supply] --> Upload
        Photo4[Extra] --> Upload
        Upload --> OCR[OCR Reading]
        OCR --> Rail[Rail Detect]
        Rail --> Compare[DB Compare]
        Compare --> Score{Match Score}
        Score -->|80+| Connected[CONNECTED]
        Score -->|50-79| Partial[PARTIAL]
        Score -->|<50| Failed[FAILED]
        Connected --> Session[Session Save]
        Partial --> Session
        Failed --> Session
        Session --> Report[Report]
    </div>
  </div>

  <div class="legend">
    <div class="legend-item"><span class="legend-dot dot-blue"></span> Input/Connect</div>
    <div class="legend-item"><span class="legend-dot dot-green"></span> Success</div>
    <div class="legend-item"><span class="legend-dot dot-yellow"></span> Warning</div>
    <div class="legend-item"><span class="legend-dot dot-red"></span> Critical</div>
  </div>
</div>

<script>
mermaid.initialize({ startOnLoad: true, theme: 'dark' });
</script>
</body>
</html>
'''
    return html


def save_all_charts():
    """Save all charts to data/charts/"""
    out_dir = os.path.join(ROOT, "data", "charts")
    os.makedirs(out_dir, exist_ok=True)

    # Diagnosis chart
    html = create_diagnosis_html()
    path = os.path.join(out_dir, "diagnosis_system.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    # Copy to Desktop
    desk = os.path.join(os.path.expanduser("~"), "Desktop")
    desk_path = os.path.join(desk, "MSM_Diagnosis_System.html")
    with open(desk_path, "w", encoding="utf-8") as f:
        f.write(html)

    return {"chart": path, "desktop": desk_path}


if __name__ == "__main__":
    result = save_all_charts()
    print(f"Chart: {result['chart']}")
    print(f"Desktop: {result['desktop']}")
'''

# ═══════════════════════════════════════════════════════════
# 3. WORKING MEMORY — Save all files
# ═══════════════════════════════════════════════════════════

def main():
    print()
    print("=" * 60)
    print("   MASTER FILE CREATOR")
    print("=" * 60)
    print()

    created = 0
    skipped = 0

    for rel_path, content in FILES.items():
        full_path = os.path.join(ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        if os.path.exists(full_path):
            skipped += 1
            print(f"   Skipped (exists): {rel_path}")
            continue

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        size = os.path.getsize(full_path)
        print(f"   ✅ Created: {rel_path} ({size} bytes)")
        created += 1

    print()
    print("-" * 60)
    print(f"   Created: {created}")
    print(f"   Skipped: {skipped}")
    print(f"   Total:   {len(FILES)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
