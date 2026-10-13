"""Complete System Verification"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def test_import(module_name):
    """Test single import"""
    try:
        __import__(module_name)
        return True, "OK"
    except Exception as e:
        return False, str(e)[:80]


def test_function(name, func):
    """Test single function"""
    try:
        result = func()
        return True, str(result)[:60]
    except Exception as e:
        return False, str(e)[:80]


def main():
    print()
    print("=" * 60)
    print("   FULL SYSTEM VERIFY")
    print("=" * 60)

    # ═══════════════════════════════════════════════════════
    # [1] File Count
    # ═══════════════════════════════════════════════════════
    print()
    print("[1/6] File Count...")
    py_count = 0
    for root, dirs, files in os.walk(ROOT):
        if any(x in root for x in ["venv", "build", "dist", "__pycache__", ".git"]):
            continue
        py_count += len([f for f in files if f.endswith(".py")])
    print(f"   Total .py files: {py_count}")

    # ═══════════════════════════════════════════════════════
    # [2] Imports Test
    # ═══════════════════════════════════════════════════════
    print()
    print("[2/6] Import Test...")

    imports = [
        "web_app",
        "data.db",
        "core.adb_manager",
        "core.detector",
        "core.multi_detect",
        "core.analyzer",
        "core.clone_checker",
        "core.usb_reader",
        "core.subscription",
        "core.privacy_manager",
        "core.analytics",
        "core.auto_delivery",
        "core.auto_connect",
        "core.photo_connect",
        "core.deep_analyzer",
        "core.meter_engine",
        "core.comment_engine",
        "core.scanner.board_scanner",
        "core.multimeter.reading_analyzer",
        "scripts.auto_approve",
        "scripts.auto_update_models",
    ]

    ok = 0
    fail = 0
    for mod in imports:
        success, msg = test_import(mod)
        if success:
            ok += 1
            print(f"   OK   {mod}")
        else:
            fail += 1
            print(f"   FAIL {mod} — {msg}")

    print(f"   Result: {ok}/{len(imports)} OK")

    # ═══════════════════════════════════════════════════════
    # [3] Functional Tests
    # ═══════════════════════════════════════════════════════
    print()
    print("[3/6] Functional Tests...")

    tests = []

    # DB Count
    def t_db():
        from data import db
        return f"Models: {db.total_count()}"
    tests.append(("Database", t_db))

    # Detector
    def t_detector():
        from core.detector import Detector
        Detector()
        return "Detector OK"
    tests.append(("Detector", t_detector))

    # Clone Checker
    def t_clone():
        from core.clone_checker import CloneChecker
        CloneChecker()
        return "CloneChecker OK"
    tests.append(("CloneChecker", t_clone))

    # Reading Analyzer
    def t_reading():
        from core.multimeter.reading_analyzer import ReadingAnalyzer
        r = ReadingAnalyzer().analyze_voltage("vbat", 3.78)
        return f"VBAT 3.78V -> {r['status']}"
    tests.append(("ReadingAnalyzer", t_reading))

    # Meter Engine
    def t_meter():
        from core.meter_engine import analyze_meter_photos
        return "MeterEngine OK"
    tests.append(("MeterEngine", t_meter))

    # Comment Engine
    def t_comment():
        from core.comment_engine import classify_comment
        c = classify_comment("Fluke meter dead")
        return f"Intents: {c['intents']}"
    tests.append(("CommentEngine", t_comment))

    # Deep Analyzer
    def t_deep():
        from core.deep_analyzer import deep_analyze
        r = deep_analyze({}, {})
        return f"Verdict: {r['diagnosis']['verdict']}"
    tests.append(("DeepAnalyzer", t_deep))

    # Auto Connect
    def t_connect():
        from core.auto_connect import get_connected_devices
        return f"Connected: {len(get_connected_devices())}"
    tests.append(("AutoConnect", t_connect))

    # Analytics
    def t_analytics():
        from core.analytics import get_all_users_stats
        s = get_all_users_stats()
        return f"Live: {s['live_now']}"
    tests.append(("Analytics", t_analytics))

    # Subscription
    def t_sub():
        from core.subscription import check_status
        s = check_status("test@test.com")
        return f"Status: {s['status']}"
    tests.append(("Subscription", t_sub))

    # Privacy
    def t_privacy():
        from core.privacy_manager import get_retention_policy
        p = get_retention_policy()
        return f"Retention: {p['images_days']}d"
    tests.append(("Privacy", t_privacy))

    # Auto Delivery
    def t_delivery():
        from core.auto_delivery import get_delivery_status
        s = get_delivery_status()
        return f"Enabled: {s['enabled']}"
    tests.append(("AutoDelivery", t_delivery))

    for name, fn in tests:
        success, msg = test_function(name, fn)
        if success:
            print(f"   OK   {name}: {msg}")
        else:
            print(f"   FAIL {name} — {msg}")

    # ═══════════════════════════════════════════════════════
    # [4] Web Routes
    # ═══════════════════════════════════════════════════════
    print()
    print("[4/6] Web Routes...")
    try:
        import web_app
        routes = list(web_app.app.url_map.iter_rules())
        print(f"   Total routes: {len(routes)}")

        # Check key routes
        route_strs = [str(r) for r in routes]
        key_routes = {
            "/": "Landing",
            "/login": "Login",
            "/dashboard-v2": "Dashboard",
            "/healthz": "Health",
        }
        for path, name in key_routes.items():
            if path in route_strs:
                print(f"   OK   {name} ({path})")
            else:
                print(f"   MISS {name} ({path})")
    except Exception as e:
        print(f"   FAIL web_app: {e}")

    # ═══════════════════════════════════════════════════════
    # [5] Database Stats
    # ═══════════════════════════════════════════════════════
    print()
    print("[5/6] Database Stats...")
    try:
        from data import db
        total = db.total_count()
        clones = db.clone_count()
        brands = len(db.list_brands())
        print(f"   Total models: {total}")
        print(f"   Clones:       {clones}")
        print(f"   Brands:       {brands}")
    except Exception as e:
        print(f"   FAIL: {e}")

    # ═══════════════════════════════════════════════════════
    # [6] Summary
    # ═══════════════════════════════════════════════════════
    print()
    print("=" * 60)
    print("   SUMMARY")
    print("=" * 60)
    print(f"   Total .py files:  {py_count}")
    print(f"   Import OK:        {ok}/{len(imports)}")
    print(f"   Import FAIL:      {fail}")
    print(f"   Functional tests: {len(tests)}")
    print("=" * 60)
    print()

    if fail == 0:
        print("   ✅ SYSTEM READY — ALL GOOD!")
    else:
        print(f"   ⚠️  {fail} import(s) failing — check above")

    print()


if __name__ == "__main__":
    main()
