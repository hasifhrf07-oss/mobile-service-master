"""
FINAL DEEP VERIFICATION
Complete system check — files, imports, routes, features, DB, EXEs
"""
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def line(ch="═"):
    print(ch * 67)


def check_file(path):
    full = os.path.join(ROOT, path)
    if os.path.exists(full):
        return True, os.path.getsize(full)
    return False, 0


def check_import(module):
    try:
        __import__(module)
        return True, "OK"
    except Exception as e:
        return False, str(e)[:60]


def main():
    print()
    line()
    print("   MOBILE SERVICE MASTER v3.1.0")
    print("   FINAL DEEP VERIFICATION")
    print(f"   {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    line()

    # ═══════════════════════════════════════════════
    # 1. FILE COUNT
    # ═══════════════════════════════════════════════
    print("\n📁 [1/8] FILE COUNT")
    print("-" * 67)

    py_count = 0
    html_count = 0
    json_count = 0

    for root, dirs, files in os.walk(ROOT):
        if any(x in root for x in ["venv", "build", "dist", "__pycache__", ".git"]):
            continue
        for f in files:
            if f.endswith(".py"):
                py_count += 1
            elif f.endswith(".html"):
                html_count += 1
            elif f.endswith(".json"):
                json_count += 1

    print(f"   .py files:    {py_count}")
    print(f"   .html files:  {html_count}")
    print(f"   .json files:  {json_count}")

    # ═══════════════════════════════════════════════
    # 2. CRITICAL FILES
    # ═══════════════════════════════════════════════
    print("\n📋 [2/8] CRITICAL FILES")
    print("-" * 67)

    critical = [
        "web_app.py", "main.py", "launcher_admin.py", "launcher_client.py",
        "admin.spec", "client.spec", "requirements.txt",
        "version.json", "VERSION", "render.yaml", "Procfile",
        "data/db.py", "data/brand_master_full.json",
        "core/__init__.py", "core/detector.py", "core/analyzer.py",
        "core/clone_checker.py", "core/adb_manager.py", "core/multi_detect.py",
        "core/usb_reader.py", "core/subscription.py", "core/privacy_manager.py",
        "core/analytics.py", "core/auto_delivery.py", "core/auto_connect.py",
        "core/photo_connect.py", "core/deep_analyzer.py", "core/chart_generator.py",
        "core/whatsapp_sender.py", "core/mlm_system.py", "core/software_solver.py",
        "core/language_manager.py", "core/user_onboarding.py",
        "core/meter_engine/engine.py", "core/comment_engine/classifier.py",
        "core/scanner/board_scanner.py", "core/multimeter/reading_analyzer.py",
        "scripts/auto_approve.py", "scripts/auto_update_models.py",
        "templates/dashboard_v2.html", "templates/admin_master.html",
        "templates/landing.html", "templates/login.html", "templates/verify.html",
        "templates/pending.html",
        "data/i18n/en.json", "data/i18n/bn.json",
        "data/i18n/hi.json", "data/i18n/ar.json",
        "database/devices.db",
    ]

    present = 0
    missing = []
    for f in critical:
        ok, size = check_file(f)
        if ok:
            present += 1
        else:
            missing.append(f)

    print(f"   Present: {present}/{len(critical)}")
    if missing:
        for m in missing:
            print(f"   ❌ {m}")
    else:
        print("   ✅ ALL CRITICAL FILES PRESENT")

    # ═══════════════════════════════════════════════
    # 3. IMPORTS
    # ═══════════════════════════════════════════════
    print("\n🔌 [3/8] PYTHON IMPORTS")
    print("-" * 67)

    imports = [
        "web_app", "data.db",
        "core.detector", "core.analyzer", "core.clone_checker",
        "core.adb_manager", "core.multi_detect", "core.usb_reader",
        "core.subscription", "core.privacy_manager", "core.analytics",
        "core.auto_delivery", "core.auto_connect", "core.photo_connect",
        "core.deep_analyzer", "core.chart_generator",
        "core.whatsapp_sender", "core.mlm_system", "core.software_solver",
        "core.language_manager", "core.user_onboarding",
        "core.meter_engine", "core.comment_engine", "core.scanner",
        "core.multimeter.reading_analyzer",
    ]

    ok_c = 0
    fail_c = 0
    for m in imports:
        ok, msg = check_import(m)
        if ok:
            ok_c += 1
        else:
            fail_c += 1
            print(f"   ❌ {m} — {msg}")

    print(f"   Import OK:   {ok_c}/{len(imports)}")
    print(f"   Import FAIL: {fail_c}")

    # ═══════════════════════════════════════════════
    # 4. DATABASE
    # ═══════════════════════════════════════════════
    print("\n💾 [4/8] DATABASE")
    print("-" * 67)

    try:
        from data import db
        print(f"   Total Models: {db.total_count()}")
        print(f"   Clone Models: {db.clone_count()}")
        brands = db.list_brands()
        print(f"   Total Brands: {len(brands)}")

        print("\n   Top 10 Brands:")
        for b in brands[:10]:
            print(f"     • {b.get('brand', '?'):<20} {b.get('n', 0)}")
    except Exception as e:
        print(f"   ❌ {e}")

    # ═══════════════════════════════════════════════
    # 5. WEB ROUTES
    # ═══════════════════════════════════════════════
    print("\n🌐 [5/8] WEB ROUTES")
    print("-" * 67)

    try:
        import web_app
        routes = list(web_app.app.url_map.iter_rules())
        print(f"   Total Routes: {len(routes)}")

        key = [
            ("/", "Landing"),
            ("/login", "Login"),
            ("/verify", "OTP"),
            ("/dashboard-v2", "Technician Dashboard"),
            ("/admin-master", "Master Admin"),
            ("/healthz", "Health"),
            ("/api/connect", "USB Connect"),
            ("/api/upload-meter-photos", "Photo Upload"),
            ("/api/whatsapp/test", "WhatsApp"),
            ("/api/mlm/stats", "MLM"),
            ("/api/solve/auto", "Solver"),
            ("/api/languages", "Languages"),
            ("/api/onboarding/status", "Onboarding"),
            ("/api/scanner/capture", "Scanner"),
        ]

        route_strs = [str(r) for r in routes]
        for path, name in key:
            icon = "✅" if path in route_strs else "❌"
            print(f"   {icon} {name:<22} {path}")
    except Exception as e:
        print(f"   ❌ {e}")

    # ═══════════════════════════════════════════════
    # 6. FEATURES
    # ═══════════════════════════════════════════════
    print("\n🧠 [6/8] FEATURES FUNCTIONAL")
    print("-" * 67)

    features = [
        ("Language Manager", lambda: len(__import__("core.language_manager", fromlist=["get_available_languages"]).get_available_languages())),
        ("WhatsApp Config", lambda: __import__("core.whatsapp_sender", fromlist=["get_config"]).get_config()["admin_number"]),
        ("MLM System", lambda: __import__("core.mlm_system", fromlist=["get_stats"]).get_stats()["total_users"]),
        ("Software Solver", lambda: __import__("core.software_solver", fromlist=["SoftwareSolver"]).SoftwareSolver() and "OK"),
        ("Deep Analyzer", lambda: __import__("core.deep_analyzer", fromlist=["deep_analyze"]).deep_analyze({}, {})["diagnosis"]["verdict"]),
        ("Auto Connect", lambda: len(__import__("core.auto_connect", fromlist=["get_connected_devices"]).get_connected_devices())),
        ("Onboarding", lambda: __import__("core.user_onboarding", fromlist=["get_stats"]).get_stats()["total"]),
        ("Chart Generator", lambda: len(__import__("core.chart_generator", fromlist=["generate_brand_tree"]).generate_brand_tree({"name": "T", "series": ["A"]}))),
    ]

    pass_c = 0
    for name, fn in features:
        try:
            res = fn()
            print(f"   ✅ {name:<20} → {str(res)[:40]}")
            pass_c += 1
        except Exception as e:
            print(f"   ❌ {name:<20} → {str(e)[:50]}")

    print(f"   Passed: {pass_c}/{len(features)}")

    # ═══════════════════════════════════════════════
    # 7. EXE FILES
    # ═══════════════════════════════════════════════
    print("\n💻 [7/8] EXE FILES")
    print("-" * 67)

    for e in ["dist/MobileServiceMaster_Admin.exe", "dist/MobileServiceMaster_Client.exe"]:
        full = os.path.join(ROOT, e)
        if os.path.exists(full):
            s = round(os.path.getsize(full) / (1024 * 1024), 2)
            print(f"   ✅ {os.path.basename(e):<45} {s} MB")
        else:
            print(f"   ❌ {os.path.basename(e)} — MISSING")

    # ═══════════════════════════════════════════════
    # 8. FINAL SUMMARY
    # ═══════════════════════════════════════════════
    print()
    line()
    print("   FINAL SUMMARY")
    line()
    print(f"   Total .py files:      {py_count}")
    print(f"   Total .html files:    {html_count}")
    print(f"   Critical files:       {present}/{len(critical)}")
    print(f"   Import OK:            {ok_c}/{len(imports)}")
    print(f"   Features working:     {pass_c}/{len(features)}")
    line()

    if not missing and fail_c == 0 and pass_c == len(features):
        print()
        print("   🎉✅ SYSTEM 100% READY — ALL GOOD ✅🎉")
    else:
        print()
        print("   ⚠️  Issues found:")
        if missing:
            print(f"      • {len(missing)} missing files")
        if fail_c:
            print(f"      • {fail_c} import failures")
        if pass_c < len(features):
            print(f"      • {len(features) - pass_c} feature failures")

    print()


if __name__ == "__main__":
    main()
