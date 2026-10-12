"""Mobile Service Master — Admin Launcher"""
import os
import sys
import time
import threading
import webbrowser

# ═════════════════════════════════════════════════════════
# PyInstaller frozen path setup
# ═════════════════════════════════════════════════════════
if getattr(sys, "frozen", False):
    BUNDLE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(sys.executable)
    sys.path.insert(0, BUNDLE_DIR)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BUNDLE_DIR
    sys.path.insert(0, BUNDLE_DIR)

os.chdir(EXE_DIR)

# Create writable folders
for d in ["static/uploads", "data", "database", "logs", "backups"]:
    try:
        os.makedirs(os.path.join(EXE_DIR, d), exist_ok=True)
    except Exception:
        pass

print()
print("=" * 62)
print("   Mobile Service Master — ADMIN")
print("=" * 62)
print(f"   Bundle dir: {BUNDLE_DIR}")
print(f"   Data dir:   {EXE_DIR}")
print()


def open_browser(url, delay=3):
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print(f"   Browser opened: {url}")
    except Exception as e:
        print(f"   [BROWSER ERROR] {e}")


def main():
    try:
        print("   Loading web_app...")
        from web_app import app
        print("   web_app loaded OK")
    except Exception as e:
        print()
        print(f"   FAILED: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("   Files in bundle dir:")
        try:
            for f in os.listdir(BUNDLE_DIR)[:30]:
                print(f"     - {f}")
        except Exception:
            pass
        input("Press Enter to exit...")
        sys.exit(1)

    url = "http://127.0.0.1:5000/"
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    print(f"   Starting server at {url}")
    print("   Keep window open")
    print("=" * 62)
    print()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=False, threaded=False)


if __name__ == "__main__":
    main()
