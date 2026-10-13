"""ADB Lifecycle — Auto install + session reset"""
import os, subprocess, time, zipfile, urllib.request, shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
TOOLS_DIR = os.path.join(ROOT, "tools")
ADB_DIR = os.path.join(TOOLS_DIR, "platform-tools")
ADB_EXE = os.path.join(ADB_DIR, "adb.exe")
URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"

os.makedirs(TOOLS_DIR, exist_ok=True)


def is_adb_installed(): return os.path.exists(ADB_EXE)


def install_adb_auto():
    if is_adb_installed():
        return {"ok": True, "message": "Already installed", "path": ADB_EXE, "already": True}
    zip_path = os.path.join(TOOLS_DIR, "platform-tools.zip")
    try:
        urllib.request.urlretrieve(URL, zip_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(TOOLS_DIR)
        os.remove(zip_path)
    except Exception as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True, "message": "Installed", "path": ADB_EXE, "already": False}


def _run_adb(args, timeout=15):
    if not is_adb_installed(): return False, "ADB missing"
    try:
        r = subprocess.run([ADB_EXE] + args, capture_output=True, text=True, timeout=timeout)
        return True, r.stdout + r.stderr
    except Exception as e: return False, str(e)


def start_server(): return {"ok": _run_adb(["start-server"])[0]}
def kill_server():
    if is_adb_installed():
        try: subprocess.run([ADB_EXE, "kill-server"], timeout=10, capture_output=True)
        except Exception: pass


def reset_session():
    kill_server()
    time.sleep(1)
    _run_adb(["start-server"])
    return {"ok": True, "message": "Session reset for next phone"}


def detect_device():
    if not is_adb_installed(): return {"ok": False, "state": "adb_missing"}
    ok, out = _run_adb(["devices"])
    if not ok: return {"ok": False, "state": "error"}
    for line in out.strip().split("\n")[1:]:
        if "\tdevice" in line:
            s = line.split("\t")[0].strip()
            info = {}
            for p in ["ro.product.brand", "ro.product.model", "ro.board.platform", "ro.build.version.release"]:
                _, v = _run_adb(["-s", s, "shell", "getprop", p])
                info[p.split(".")[-1]] = v.strip()
            info["serial"] = s
            return {"ok": True, "state": "connected", "serial": s, "info": info}
        elif "\tunauthorized" in line:
            return {"ok": False, "state": "unauthorized", "message": "Allow popup"}
    return {"ok": False, "state": "no_device"}


def auto_connect_workflow():
    r = {"steps": []}
    inst = install_adb_auto()
    r["steps"].append({"install": inst["ok"]})
    if not inst["ok"]: r["ok"] = False; return r
    start_server()
    det = detect_device()
    r["ok"] = det["ok"]
    r["device"] = det.get("info", {})
    r["state"] = det.get("state")
    r["finished_at"] = datetime.now().isoformat(timespec="seconds")
    return r


def auto_disconnect_workflow(): return reset_session()
def get_lifecycle_status():
    return {"adb_installed": is_adb_installed(), "adb_path": ADB_EXE if is_adb_installed() else ""}


if __name__ == "__main__":
    print(get_lifecycle_status())
