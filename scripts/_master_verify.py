"""MASTER VERIFY — Complete system check"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def line(ch="="):
    print(ch * 65)


def check_file(path):
    """Check if file exists"""
    full = os.path.join(ROOT, path)
    if os.path.exists(full):
        size = os.path.getsize(full)
        return True, size
    return False, 0


def check_import(module):
    """Test import"""
    try:
        __import__(module)
        return True, "OK"
    except Exception as e:
        return False, str(e)[:80]


def main():
    print()
    line()
    print("   MASTER SYSTEM VERIFY")
    print("   Mobile Service Master v3.1.0")
    line()

    # ═══════════════════════════════════════════════════════
    # SECTION 1: FILE COUNT
    # ═══════════════════════════════════════════════════════
    print()
    print("📊 [1/8] FILE COUNT")
    print("-" * 65)

    py_count = 0
    py_files = []
    for root, dirs, files in os.walk(ROOT):
        if any(x in root for x in ["venv", "build", "dist", "__pycache__", ".git"]):
            continue
        for f in files:
            if f.endswith(".py"):
                py_count += 1
                py_files.append(os.path.join(root, f))

    html_count = 0
    for root, dirs, files in os.walk(ROOT):
        if any(x in root for x in ["venv", "build", "dist", "__pycache__", ".git"]):
            continue
        for f in files:
            if f.endswith(".html"):
                html_count += 1

    print(f"   Total .py files:   {py_count}")
    print(f"   Total .html files: {html_count}")

    # ═══════════════════════════════════════════════════════
    # SECTION 2: CRITICAL FILES
    # ═══════════════════════════════════════════════════════
    print()
    print("📁 [2/8] CRITICAL FILES")
    print("-" * 65)

    critical = [
        # Root
        "web_app.py", "main.py", "launcher_admin.py", "launcher_client.py",
        "admin.spec", "client.spec", "requirements.txt",
        "version.json", "VERSION", "render.yaml", "Procfile",
        # Data
        "data/db.py", "data/__init__.py", "data/brand_master_full.json",
        # Core
        "core/__init__.py", "core/adb_manager.py", "core/detector.py",
        "core/multi_detect.py", "core/analyzer.py", "core/clone_checker.py",
        "core/usb_reader.py", "core/subscription.py", "core/privacy_manager.py",
        "core/analytics.py", "core/auto_delivery.py", "core/auto_connect.py",
        "core/photo_connect.py", "core/deep_analyzer.py", "core/chart_generator.py",
        # Meter engine
        "core/meter_engine/__init__.py", "core/meter_engine/engine.py",
        "core/meter_engine/brand_detector.py", "core/meter_engine/ocr_reader.py",
        "core/meter_engine/accuracy_map.py", "core/meter_engine/rail_extractor.py",
        "core/meter_engine/cross_validator.py", "core/meter_engine/anomaly_detector.py",
        # Comment engine
        "core/comment_engine/__init__.py", "core/comment_engine/classifier.py",
        "core/comment_engine/auto_reply.py", "core/comment_engine/learning_log.py",
        "core/comment_engine/admin_queue.py",
        # Scanner
        "core/scanner/__init__.py", "core/scanner/board_scanner.py",
        "core/scanner/boardview_manager.py", "core/scanner/history_manager.py",
        "core/scanner/state_comparator.py",
        # Multimeter
        "core/multimeter/__init__.py", "core/multimeter/rail_database.py",
        "core/multimeter/reading_analyzer.py",
        # Scripts
        "scripts/__init__.py", "scripts/auto_approve.py",
        "scripts/auto_update_models.py", "scripts/monthly_backup.py",
        "scripts/privacy_cleanup.py", "scripts/health_check.py",
        # Templates
        "templates/dashboard_v2.html", "templates/verify.html",
        "templates/login.html", "templates/landing.html", "templates/pending.html",
        # Database
        "database/devices.db",
    ]

    present = 0
    missing = 0
    for f in critical:
        ok, size = check_file(f)
        if ok:
            present += 1
        else:
            print(f"   ❌ MISSING: {f}")
            missing += 1

    print(f"   Present: {present}/{len(critical)}")
    if missing == 0:
        print(f"   ✅ ALL CRITICAL FILES PRESENT!")
    else:
        print(f"   ⚠️  {missing} files missing")

    # ═══════════════════════════════════════════════════════
    # SECTION 3: IMPORTS
    # ═══════════════════════════════════════════════════════
    print()
    print("🔌 [3/8] PYTHON IMPORTS")
    print("-" * 65)

    imports = [
        "web_app", "data.db",
        "core.adb_manager", "core.detector", "core.multi_detect",
        "core.analyzer", "core.clone_checker", "core.usb_reader",
        "core.subscription", "core.privacy_manager", "core.analytics",
        "core.auto_delivery", "core.auto_connect", "core.photo_connect",
        "core.deep_analyzer", "core.chart_generator",
        "core.meter_engine", "core.comment_engine",
        "core.scanner", "core.scanner.board_scanner",
        "core.multimeter.reading_analyzer",
        "scripts.auto_approve", "scripts.auto_update_models",
    ]

    ok_count = 0
    fail_count = 0
    for m in imports:
        ok, msg = check_import(m)
        if ok:
            ok_count += 1
        else:
            fail_count += 1
            print(f"   ❌ {m} — {msg}")

    print(f"   Import OK:   {ok_count}/{len(imports)}")
    print(f"   Import FAIL: {fail_count}")

    # ═══════════════════════════════════════════════════════
    # SECTION 4: DATABASE
    # ═══════════════════════════════════════════════════════
    print()
    print("💾 [4/8] DATABASE STATUS")
    print("-" * 65)

    try:
        from data import db
        total = db.total_count()
        clones = db.clone_count()
        brands = db.list_brands()
        print(f"   Total Models: {total}")
        print(f"   Clone Models: {clones}")
        print(f"   Total Brands: {len(brands)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # ═══════════════════════════════════════════════════════
    # SECTION 5: WEB ROUTES
    # ═══════════════════════════════════════════════════════
    print()
    print("🌐 [5/8] WEB ROUTES")
    print("-" * 65)

    try:
        import web_app
        routes = list(web_app.app.url_map.iter_rules())
        print(f"   Total Routes: {len(routes)}")

        key_routes = [
            ("/", "Landing"),
            ("/login", "Login"),
            ("/verify", "OTP"),
            ("/dashboard-v2", "Dashboard"),
            ("/healthz", "Health"),
            ("/api/connect", "USB Connect"),
            ("/api/upload-meter-photos", "Photo Upload"),
            ("/api/comment", "Comment"),
            ("/api/admin/users", "Admin Users"),
            ("/api/version/check", "Version"),
            ("/api/brands/list", "Brands"),
        ]

        route_strs = [str(r) for r in routes]
        for path, name in key_routes:
            if path in route_strs:
                print(f"   ✅ {name:<20} ({path})")
            else:
                print(f"   ❌ {name:<20} ({path}) MISSING")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # ═══════════════════════════════════════════════════════
    # SECTION 6: FEATURES FUNCTIONAL TEST
    # ═══════════════════════════════════════════════════════
    print()
    print("🧠 [6/8] FEATURE TESTS")
    print("-" * 65)

    tests = [
        ("Detector", lambda: __import__("core.detector", fromlist=["Detector"]).Detector() and "OK"),
        ("CloneChecker", lambda: __import__("core.clone_checker", fromlist=["CloneChecker"]).CloneChecker() and "OK"),
        ("Analyzer", lambda: __import__("core.analyzer", fromlist=["Analyzer"]).Analyzer() and "OK"),
        ("MeterEngine", lambda: __import__("core.meter_engine", fromlist=["analyze_meter_photos"]).analyze_meter_photos and "OK"),
        ("CommentEngine", lambda: str(__import__("core.comment_engine", fromlist=["classify_comment"]).classify_comment("test"))[:40]),
        ("DeepAnalyzer", lambda: __import__("core.deep_analyzer", fromlist=["deep_analyze"]).deep_analyze({}, {})["diagnosis"]["verdict"]),
        ("AutoConnect", lambda: str(__import__("core.auto_connect", fromlist=["get_connected_devices"]).get_connected_devices())),
        ("Analytics", lambda: str(__import__("core.analytics", fromlist=["get_all_users_stats"]).get_all_users_stats()["total_users"])),
        ("Subscription", lambda: __import__("core.subscription", fromlist=["check_status"]).check_status("test@test.com")["status"]),
        ("Privacy", lambda: str(__import__("core.privacy_manager", fromlist=["get_retention_policy"]).get_retention_policy()["images_days"])),
        ("AutoDelivery", lambda: str(__import__("core.auto_delivery", fromlist=["get_delivery_status"]).get_delivery_status()["enabled"])),
        ("BoardScanner", lambda: __import__("core.scanner.board_scanner", fromlist=["BoardScanner"]).BoardScanner() and "OK"),
        ("StateComparator", lambda: __import__("core.scanner.state_comparator", fromlist=["StateComparator"]).StateComparator() and "OK"),
        ("ChartGenerator", lambda: str(len(__import__("core.chart_generator", fromlist=["generate_brand_tree"]).generate_brand_tree({"name":"Test","series":["A"]})))),
        ("ReadingAnalyzer", lambda: __import__("core.multimeter.reading_analyzer", fromlist=["ReadingAnalyzer"]).ReadingAnalyzer().analyze_voltage("vbat", 3.78)["status"]),
    ]

    pass_count = 0
    for name, fn in tests:
        try:
            result = fn()
            print(f"   ✅ {name:<18} → {str(result)[:40]}")
            pass_count += 1
        except Exception as e:
            print(f"   ❌ {name:<18} → {str(e)[:60]}")

    print(f"   Passed: {pass_count}/{len(tests)}")

    # ═══════════════════════════════════════════════════════
    # SECTION 7: EXE FILES
    # ═══════════════════════════════════════════════════════
    print()
    print("💻 [7/8] EXE FILES")
    print("-" * 65)

    exe_files = [
        "dist/MobileServiceMaster_Admin.exe",
        "dist/MobileServiceMaster_Client.exe",
    ]

    for e in exe_files:
        full = os.path.join(ROOT, e)
        if os.path.exists(full):
            size = round(os.path.getsize(full) / (1024 * 1024), 2)
            print(f"   ✅ {os.path.basename(e):<40} {size} MB")
        else:
            print(f"   ❌ {os.path.basename(e)} MISSING")

    # ═══════════════════════════════════════════════════════
    # SECTION 8: FINAL SUMMARY
    # ═══════════════════════════════════════════════════════
    print()
    line()
    print("   FINAL SUMMARY")
    line()
    print(f"   Total .py files:      {py_count}")
    print(f"   Total .html files:    {html_count}")
    print(f"   Critical files:       {present}/{len(critical)}")
    print(f"   Import OK:            {ok_count}/{len(imports)}")
    print(f"   Feature tests:        {pass_count}/{len(tests)}")
    line()

    if missing == 0 and fail_count == 0 and pass_count == len(tests):
        print()
        print("   ✅✅✅ SYSTEM READY — ALL GOOD ✅✅✅")
    else:
        print()
        print(f"   ⚠️  Check above for issues")
        if missing > 0:
            print(f"      • {missing} missing files")
        if fail_count > 0:
            print(f"      • {fail_count} import failures")
        if pass_count < len(tests):
            print(f"      • {len(tests) - pass_count} feature failures")

    print()


if __name__ == "__main__":
    main()
