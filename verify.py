#!/usr/bin/env python3
"""verify.py — full system verification"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"


def check(name, condition, detail=""):
    symbol = PASS if condition else FAIL
    print(f"  {symbol} {name}" + (f" — {detail}" if detail else ""))
    return condition


def main():
    print("=" * 60)
    print("🔍 Mobile Service Master v3.0 — Verification")
    print("=" * 60)

    results = []

    # Python
    print("\n[1] Python Environment")
    v = sys.version_info
    results.append(check(
        f"Python {v.major}.{v.minor}.{v.micro}",
        v.major >= 3 and v.minor >= 10
    ))

    # Dependencies
    print("\n[2] Dependencies")
    for mod in ["PyQt6", "pyttsx3", "requests"]:
        try:
            __import__(mod)
            results.append(check(mod, True))
        except ImportError:
            results.append(check(mod, False, f"pip install {mod}"))

    # ADB
    print("\n[3] ADB Tools")
    import subprocess
    try:
        out = subprocess.check_output(
            ["adb", "version"], text=True, timeout=5,
            stderr=subprocess.STDOUT
        )
        results.append(check("ADB installed", "version" in out.lower()))
    except Exception:
        results.append(check("ADB", False, "PATH-এ যোগ করো"))

    # Folders
    print("\n[4] Folders")
    root = os.path.dirname(os.path.abspath(__file__))
    for folder in ["core", "data", "database", "ui",
                   "core/scanner", "guides", "logs"]:
        results.append(check(
            f"{folder}/",
            os.path.isdir(os.path.join(root, folder))
        ))

    # Core modules
    print("\n[5] Core Modules")
    modules = [
        "core.detector", "core.clone_checker", "core.analyzer",
        "core.consent", "core.voice", "core.updater",
        "core.auto_solver", "core.multi_detect",
        "core.scanner.board_scanner",
        "core.scanner.boardview_manager",
        "core.scanner.history_manager",
        "core.scanner.state_comparator",
    ]
    for m in modules:
        try:
            __import__(m)
            results.append(check(m, True))
        except Exception as e:
            results.append(check(m, False, str(e)[:40]))

    # UI modules
    print("\n[6] UI Modules")
    ui_mods = [
        "ui.style", "ui.tab_detect", "ui.tab_diagnose",
        "ui.tab_scanner", "ui.tab_boardview",
        "ui.tab_history", "ui.tab_settings", "ui.tab_update",
        "ui.scanner_widgets", "ui.main_window",
    ]
    for m in ui_mods:
        try:
            __import__(m)
            results.append(check(m, True))
        except Exception as e:
            results.append(check(m, False, str(e)[:40]))

    # DB Tables
    print("\n[7] Database Tables")
    try:
        import sqlite3
        db_path = os.path.join(root, "database", "devices.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )]
            conn.close()

            required = ["devices", "devices_fts", "meta", "history",
                        "update_log", "boardview_files", "board_scans",
                        "scan_history"]
            for t in required:
                results.append(check(f"Table: {t}", t in tables))
        else:
            results.append(check("devices.db", False, "init_db.py চালাও"))
    except Exception as e:
        results.append(check("DB", False, str(e)[:40]))

    # Summary
    print("\n" + "=" * 60)
    ok = sum(results)
    total = len(results)
    print(f"📊 Results: {ok}/{total} passed")
    if ok == total:
        print(f"{PASS} সব ঠিক — python main.py চালাও")
    else:
        print(f"{FAIL} কিছু missing — উপরে দেখো")
    print("=" * 60)


if __name__ == "__main__":
    main() 