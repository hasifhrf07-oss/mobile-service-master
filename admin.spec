# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    "web_app", "data", "data.db", "core",
    "core.subscription", "core.privacy_manager",
    "core.meter_engine", "core.meter_engine.engine",
    "core.meter_engine.brand_detector", "core.meter_engine.ocr_reader",
    "core.meter_engine.accuracy_map", "core.meter_engine.rail_extractor",
    "core.meter_engine.cross_validator", "core.meter_engine.anomaly_detector",
    "core.comment_engine", "core.comment_engine.classifier",
    "core.comment_engine.auto_reply", "core.comment_engine.learning_log",
    "core.comment_engine.admin_queue",
    "core.multimeter", "core.multimeter.rail_database", "core.multimeter.reading_analyzer",
    "core.adb_manager", "core.detector", "core.multi_detect",
    "core.analyzer", "core.clone_checker", "core.usb_reader",
    "core.voice", "core.consent", "core.updater",
    "core.scanner", "core.scanner.board_scanner",
    "core.scanner.boardview_manager", "core.scanner.history_manager",
    "core.scanner.state_comparator",
    "scripts", "scripts.auto_approve",
    "apscheduler", "apscheduler.schedulers", "apscheduler.schedulers.background",
    "flask", "flask.json", "cryptography", "cryptography.fernet",
    "werkzeug", "werkzeug.utils", "jinja2",
]

for pkg in ["flask", "cryptography", "jinja2", "apscheduler", "werkzeug"]:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as e:
        print(f"Skip {pkg}: {e}")

# ═════════════════════════════════════════════════════════
# CRITICAL: web_app.py must be in datas as a file
# ═════════════════════════════════════════════════════════
datas += [
    ("web_app.py", "."),
    ("templates", "templates"),
    ("core", "core"),
    ("scripts", "scripts"),
]

for folder in ["static", "data", "database", "guides"]:
    if os.path.exists(folder):
        datas += [(folder, folder)]

for f in ["version.json", "VERSION", "render.yaml", "requirements.txt",
          "runtime.txt", "README.md", ".secret_key", ".encryption_key", "users.json"]:
    if os.path.exists(f):
        datas.append((f, "."))

block_cipher = None

a = Analysis(
    ["launcher_admin.py"],
    pathex=[os.path.abspath(".")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "PyQt5", "PyQt6", "scipy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name="MobileServiceMaster_Admin",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
