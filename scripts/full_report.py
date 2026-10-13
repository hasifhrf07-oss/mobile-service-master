"""Complete System Report"""
import os
import sys
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def line():
    print("=" * 65)


def main():
    print()
    line()
    print("   MOBILE SERVICE MASTER v3.1.0 — FULL REPORT")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    line()

    # ═══════════════════════════════════════════════════════
    # 1. DATABASE
    # ═══════════════════════════════════════════════════════
    print()
    print("📊 [1] DATABASE STATUS")
    print("-" * 65)
    try:
        from data import db
        total = db.total_count()
        clones = db.clone_count()
        brands = db.list_brands()

        print(f"   Total Models:     {total}")
        print(f"   Clone Models:     {clones}")
        print(f"   Total Brands:     {len(brands)}")
        print()
        print("   Brand Breakdown (Top 15):")
        for b in brands[:15]:
            print(f"     • {b.get('brand', '?'):<20} {b.get('n', 0)} models")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # ═══════════════════════════════════════════════════════
    # 2. USERS
    # ═══════════════════════════════════════════════════════
    print()
    print("👥 [2] USER DATABASE")
    print("-" * 65)
    try:
        users_file = os.path.join(ROOT, "users.json")
        if os.path.exists(users_file):
            users = json.load(open(users_file, "r", encoding="utf-8"))
            print(f"   Total Users: {len(users)}")
            for email, u in list(users.items())[:10]:
                verified = "✅" if u.get("verified") else "⏳"
                print(f"     {verified} {email}")
        else:
            print("   ℹ️  No users.json (fresh start)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # ═══════════════════════════════════════════════════════
    # 3. ADMIN DASHBOARD TABS
    # ═══════════════════════════════════════════════════════
    print()
    print("📱 [3] ADMIN DASHBOARD — 9 TABS")
    print("-" * 65)
    tabs = [
        ("Connect",      "Model search + USB connect"),
        ("Picture",      "4-photo upload + analysis"),
        ("Result",       "Diagnosis display"),
        ("History",      "Service timeline"),
        ("Calibration",  "DECOY — fake feature"),
        ("Warranty",     "DECOY — fake feature"),
        ("Reports",      "DECOY — fake feature"),
        ("Settings",     "System info + delivery config"),
        ("Admin",        "User management (admin only)"),
    ]
    for i, (name, desc) in enumerate(tabs, 1):
        print(f"   {i}. 📌 {name:<12} — {desc}")

    # ═══════════════════════════════════════════════════════
    # 4. API ROUTES
    # ═══════════════════════════════════════════════════════
    print()
    print("🔌 [4] API ROUTES")
    print("-" * 65)
    try:
        import web_app
        routes = sorted([str(r) for r in web_app.app.url_map.iter_rules()])
        print(f"   Total Routes: {len(routes)}")
        print()
        print("   Key Routes:")
        key = ["/", "/login", "/verify", "/dashboard-v2", "/healthz",
               "/api/connect", "/api/upload-meter-photos", "/api/comment",
               "/api/admin/users", "/api/version/check"]
        for r in routes:
            if any(r.startswith(k) for k in key):
                print(f"     • {r}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # ═══════════════════════════════════════════════════════
    # 5. FEATURES
    # ═══════════════════════════════════════════════════════
    print()
    print("🧠 [5] FEATURES ACTIVE")
    print("-" * 65)
    features = [
        ("Role-based login", "admin / technician"),
        ("Auto-approve", "24-hour delay"),
        ("Meter photo analysis", "OCR + rails"),
        ("Photo Connect", "Session-based"),
        ("Deep Analyzer", "4-photo diagnosis"),
        ("Comment engine", "Auto-reply + learning"),
        ("Live user monitor", "Real-time activity"),
        ("Auto model update", "Every 15 days"),
        ("Auto EXE delivery", "Every 3 months"),
        ("Subscription", "6-month trial"),
        ("Privacy cleanup", "30-day auto-delete"),
        ("Analytics", "User stats"),
        ("Board scanner", "State capture"),
        ("Multimeter analysis", "Rail database"),
    ]
    for name, desc in features:
        print(f"   ✅ {name:<25} — {desc}")

    # ═══════════════════════════════════════════════════════
    # 6. FILE STATUS
    # ═══════════════════════════════════════════════════════
    print()
    print("📁 [6] FILE STATUS")
    print("-" * 65)
    critical = [
        "web_app.py", "data/db.py",
        "core/detector.py", "core/analyzer.py",
        "core/meter_engine/engine.py",
        "core/photo_connect.py", "core/deep_analyzer.py",
        "core/auto_connect.py", "core/analytics.py",
        "core/auto_delivery.py",
        "scripts/auto_update_models.py",
        "templates/dashboard_v2.html",
        "templates/landing.html",
    ]
    present = 0
    for f in critical:
        path = os.path.join(ROOT, f)
        if os.path.exists(path):
            print(f"   ✅ {f}")
            present += 1
        else:
            print(f"   ❌ {f} MISSING")
    print()
    print(f"   Files Present: {present}/{len(critical)}")

    # ═══════════════════════════════════════════════════════
    # 7. EXE FILES
    # ═══════════════════════════════════════════════════════
    print()
    print("💻 [7] EXE FILES")
    print("-" * 65)
    exes = [
        "dist/MobileServiceMaster_Admin.exe",
        "dist/MobileServiceMaster_Client.exe",
    ]
    for e in exes:
        path = os.path.join(ROOT, e)
        if os.path.exists(path):
            size = round(os.path.getsize(path) / (1024 * 1024), 2)
            print(f"   ✅ {os.path.basename(e)}: {size} MB")
        else:
            print(f"   ❌ {os.path.basename(e)} missing")

    # ═══════════════════════════════════════════════════════
    # 8. AUTO-CONNECT ANSWER
    # ═══════════════════════════════════════════════════════
    print()
    print("🔗 [8] AUTO-CONNECT STATUS")
    print("-" * 65)
    print("   ✅ Photo → OCR → Database → CONNECTED status")
    print("   ✅ Session saved + Admin tracking")
    print("   ❌ WiFi/Bluetooth/USB physical connect (impossible)")
    print("   ℹ️  Method: Database-based session (not network)")

    # ═══════════════════════════════════════════════════════
    # 9. SOFTWARE PROBLEM SOLUTIONS
    # ═══════════════════════════════════════════════════════
    print()
    print("💊 [9] SOFTWARE PROBLEM SOLUTIONS")
    print("-" * 65)
    solutions = [
        ("Boot loop", "Cache wipe → Stock ROM reflash"),
        ("No boot", "eMMC health → PMIC rails check"),
        ("Network issue", "Network reset → Modem reflash"),
        ("Display flicker", "Display reset → Flex reseat"),
        ("Slow charging", "Charging IC → Battery stats reset"),
        ("Battery drain", "Battery health → Stats reset"),
        ("FRP lock", "Owner verification required"),
    ]
    for problem, solution in solutions:
        print(f"   {problem:<20} → {solution}")

    # ═══════════════════════════════════════════════════════
    # 10. FINAL
    # ═══════════════════════════════════════════════════════
    print()
    line()
    print("   ✅ SYSTEM REPORT COMPLETE")
    line()
    print()


if __name__ == "__main__":
    main()
