# Run Web App + Cloudflare Tunnel (Free Permanent URL)

import os
import sys
import subprocess
import time
import shutil


def find_cloudflared():
    cf = shutil.which("cloudflared")
    if cf:
        return cf
    paths = [
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
        r"C:\cloudflared\cloudflared.exe",
        os.path.expanduser(r"~\cloudflared\cloudflared.exe"),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def main():
    print("=" * 62)
    print("   Mobile Service Master — Cloudflare Public Access")
    print("=" * 62)
    print()

    print("[1/3] Finding cloudflared...")
    cf_path = find_cloudflared()

    if not cf_path:
        print()
        print("❌ cloudflared install করা নেই!")
        print("   Run: winget install --id Cloudflare.cloudflared")
        print()
        return

    print(f"      ✓ Found: {cf_path}")

    print()
    print("[2/3] Starting Flask (port 5000)...")
    flask = subprocess.Popen(
        [sys.executable, "web_app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(4)
    print("      ✓ Flask running")

    print()
    print("[3/3] Creating Cloudflare tunnel...")
    print("      URL আসতে ৫-১০ সেকেন্ড লাগবে")
    print()

    cf = None
    try:
        cf = subprocess.Popen(
            [cf_path, "tunnel", "--url", "http://localhost:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        url_found = False
        start = time.time()

        while time.time() - start < 30:
            line = cf.stdout.readline()
            if line:
                line = line.strip()
                if line:
                    print(f"      {line}")
                if "trycloudflare.com" in line:
                    url_found = True
                    break

        if url_found:
            print()
            print("=" * 62)
            print("   🎉 PUBLIC URL READY!")
            print("=" * 62)
            print()
            print("   📱 Mobile-এ Chrome খুলে উপরের URL খোলো")
            print()
            print("   🛑 বন্ধ করতে: Ctrl + C")
            print()
            print("=" * 62)

        try:
            cf.wait()
        except KeyboardInterrupt:
            pass

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        flask.terminate()
        if cf:
            try:
                cf.terminate()
            except Exception:
                pass
        print("✅ Stopped")


if __name__ == "__main__":
    main()