"""Health Check — for UptimeRobot"""
import sys
import os

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def check(url):
    if HAS_REQUESTS:
        try:
            r = requests.get(url, timeout=10)
            return r.status_code == 200
        except Exception:
            return False
    else:
        # Fallback: urllib
        import urllib.request
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                return r.status == 200
        except Exception:
            return False


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/healthz"
    print("OK" if check(url) else "FAIL")
