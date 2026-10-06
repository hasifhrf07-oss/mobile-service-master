"""
ADB Manager — Connection logic + Authorization tracker
প্রথমবার popup, second time auto-connect
"""

import subprocess
import os
import json
import time
from datetime import datetime


ROOT = os.path.dirname(os.path.dirname(__file__))
AUTHORIZED_FILE = os.path.join(ROOT, "database", "authorized_devices.json")


class ADBManager:
    """
    ADB connection handling — track authorized devices
    """

    def __init__(self):
        self.authorized_devices = self._load_authorized()

    # ═════════════════════════════════════════════════════
    # Authorization Tracker
    # ═════════════════════════════════════════════════════

    def _load_authorized(self):
        """Load authorized device list"""
        if not os.path.exists(AUTHORIZED_FILE):
            return {}
        try:
            with open(AUTHORIZED_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_authorized(self):
        """Save authorized list"""
        try:
            os.makedirs(os.path.dirname(AUTHORIZED_FILE), exist_ok=True)
            with open(AUTHORIZED_FILE, "w", encoding="utf-8") as f:
                json.dump(self.authorized_devices, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def mark_authorized(self, serial, brand="", model=""):
        """ফোন authorized হিসেবে mark করো"""
        if not serial:
            return False

        self.authorized_devices[serial] = {
            "brand": brand,
            "model": model,
            "first_authorized": self.authorized_devices.get(serial, {}).get(
                "first_authorized", datetime.now().isoformat()
            ),
            "last_seen": datetime.now().isoformat(),
            "count": self.authorized_devices.get(serial, {}).get("count", 0) + 1,
        }
        return self._save_authorized()

    def is_authorized(self, serial):
        """এই ফোন আগে authorized হয়েছিল কিনা"""
        return serial in self.authorized_devices

    def get_authorized_list(self):
        """সব authorized device list"""
        return list(self.authorized_devices.items())

    def forget_device(self, serial):
        """Authorized list থেকে সরাও"""
        if serial in self.authorized_devices:
            del self.authorized_devices[serial]
            self._save_authorized()
            return True
        return False

    # ═════════════════════════════════════════════════════
    # ADB Connection
    # ═════════════════════════════════════════════════════

    def _adb(self, args, timeout=8):
        try:
            return subprocess.check_output(
                ["adb"] + args,
                stderr=subprocess.STDOUT,
                text=True, timeout=timeout
            ).strip()
        except Exception:
            return ""

    def restart_server(self):
        """ADB server restart — connection reset"""
        self._adb(["kill-server"])
        time.sleep(1)
        self._adb(["start-server"])
        time.sleep(1)
        return True

    def get_devices(self):
        """
        Return:
        [
            {"serial": "xxx", "status": "device"},
            {"serial": "yyy", "status": "unauthorized"},
            {"serial": "zzz", "status": "offline"},
        ]
        """
        out = self._adb(["devices"])
        devices = []

        for line in out.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                devices.append({
                    "serial": parts[0].strip(),
                    "status": parts[1].strip(),
                })
        return devices

    def check_connection(self):
        """
        Returns:
        {
            "state": "no_device" | "unauthorized" | "device" | "offline" | "multiple",
            "devices": [...],
            "primary": {...} or None,
        }
        """
        devices = self.get_devices()

        if not devices:
            return {
                "state": "no_device",
                "devices": [],
                "primary": None,
            }

        # Find first "device" status (authorized)
        device = next((d for d in devices if d["status"] == "device"), None)
        if device:
            if len(devices) == 1:
                state = "device"
            else:
                state = "multiple"
            return {
                "state": state,
                "devices": devices,
                "primary": device,
            }

        # Unauthorized?
        unauth = next((d for d in devices if d["status"] == "unauthorized"), None)
        if unauth:
            return {
                "state": "unauthorized",
                "devices": devices,
                "primary": unauth,
            }

        # Offline
        offline = next((d for d in devices if d["status"] == "offline"), None)
        if offline:
            return {
                "state": "offline",
                "devices": devices,
                "primary": offline,
            }

        return {
            "state": "unknown",
            "devices": devices,
            "primary": devices[0] if devices else None,
        }

    def get_device_serial(self):
        """Current device serial"""
        return self._adb(["get-serialno"])

    def get_device_model(self):
        """Model via ADB"""
        return self._adb(["shell", "getprop", "ro.product.model"])

    def get_device_brand(self):
        """Brand via ADB"""
        return self._adb(["shell", "getprop", "ro.product.brand"])

    def install_apk(self, apk_path):
        """APK install"""
        return self._adb(["install", "-r", apk_path], timeout=60)

    def shell(self, cmd):
        """Run shell command"""
        return self._adb(["shell"] + cmd.split())

    def reboot(self, mode=None):
        """Reboot device"""
        if mode:
            return self._adb(["reboot", mode])
        return self._adb(["reboot"])

    # ═════════════════════════════════════════════════════
    # Wait for Authorization
    # ═════════════════════════════════════════════════════

    def wait_for_authorization(self, timeout=60, callback=None):
        """
        Popup আসার পর client "Allow" ক্লিক করার জন্য wait।
        callback: function(state, elapsed_seconds)
        """
        start = time.time()

        while time.time() - start < timeout:
            result = self.check_connection()
            elapsed = int(time.time() - start)

            if callback:
                callback(result["state"], elapsed)

            if result["state"] == "device":
                return {
                    "ok": True,
                    "device": result["primary"],
                    "elapsed": elapsed,
                }

            time.sleep(1.5)

        return {
            "ok": False,
            "message": "Timeout — client Allow করেনি",
            "elapsed": timeout,
        }