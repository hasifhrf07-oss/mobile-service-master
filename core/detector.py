"""Device Detector — extended with BoardView check"""

import subprocess
import re
import os
from dataclasses import dataclass, field, asdict


@dataclass
class DeviceInfo:
    brand: str = ""
    model: str = ""
    codename: str = ""
    chipset: str = ""
    android: str = ""
    serial: str = ""
    imei: str = ""
    build_fingerprint: str = ""
    connection_mode: str = "none"
    is_clone: bool = False
    clone_reasons: list = field(default_factory=list)
    boardview_path: str = ""
    schematic_path: str = ""

    def to_dict(self):
        return asdict(self)


class Detector:
    def __init__(self):
        self.info = DeviceInfo()

    def _run(self, cmd_list, timeout=10):
        try:
            return subprocess.check_output(
                cmd_list, stderr=subprocess.STDOUT,
                text=True, timeout=timeout
            ).strip()
        except Exception:
            return ""

    def _adb(self, cmd, timeout=10):
        return self._run(["adb"] + cmd.split(), timeout)

    def _fastboot(self, cmd, timeout=10):
        return self._run(["fastboot"] + cmd.split(), timeout)

    # ═════════════════════════════════════════════════════
    # Detection modes
    # ═════════════════════════════════════════════════════

    def detect_adb(self):
        out = self._adb("devices")
        if "\tdevice" not in out:
            return False
        self.info.connection_mode = "adb"
        self.info.brand = self._adb("shell getprop ro.product.brand") or \
                          self._adb("shell getprop ro.product.manufacturer")
        self.info.model = self._adb("shell getprop ro.product.model")
        self.info.codename = self._adb("shell getprop ro.product.device")
        self.info.chipset = (self._adb("shell getprop ro.hardware") or
                             self._adb("shell getprop ro.board.platform"))
        self.info.android = self._adb("shell getprop ro.build.version.release")
        self.info.serial = self._adb("get-serialno")
        self.info.build_fingerprint = self._adb("shell getprop ro.build.fingerprint")
        return True

    def detect_fastboot(self):
        out = self._fastboot("devices")
        if not out or "\t" not in out:
            return False
        self.info.connection_mode = "fastboot"
        self.info.serial = out.split("\t")[0].strip()
        self.info.brand = "Unknown (fastboot)"
        return True

    def detect_edl(self):
        try:
            cmd = ["powershell", "-Command",
                   'Get-PnpDevice -PresentOnly | '
                   'Where-Object {$_.FriendlyName -like "*9008*"} | '
                   'Select-Object -First 1 -ExpandProperty FriendlyName']
            out = self._run(cmd, timeout=10)
            if "9008" in out:
                self.info.connection_mode = "edl"
                self.info.chipset = "Qualcomm (EDL 9008)"
                self.info.brand = "Unknown (EDL)"
                return True
        except Exception:
            pass
        return False

    def detect_mtk(self):
        try:
            cmd = ["powershell", "-Command",
                   'Get-PnpDevice -PresentOnly | '
                   'Where-Object {$_.FriendlyName -like "*MTK*" -or '
                   '$_.FriendlyName -like "*MediaTek*"} | '
                   'Select-Object -First 1 -ExpandProperty FriendlyName']
            out = self._run(cmd, timeout=10)
            if "MTK" in out or "MediaTek" in out:
                self.info.connection_mode = "mtk"
                self.info.chipset = "MediaTek (BROM)"
                self.info.brand = "Unknown (MTK)"
                return True
        except Exception:
            pass
        return False

    def auto_detect(self):
        self.info = DeviceInfo()
        for fn in [self.detect_adb, self.detect_fastboot,
                   self.detect_edl, self.detect_mtk]:
            if fn():
                self._check_boardview_files()
                return True
        self.info.connection_mode = "none"
        return False

    # ═════════════════════════════════════════════════════
    # BoardView File Check
    # ═════════════════════════════════════════════════════

    def _check_boardview_files(self):
        """Detect করার পর BoardView + Schematic file check"""
        if not self.info.brand or not self.info.model:
            return

        root = os.path.dirname(os.path.dirname(__file__))

        # Brand normalize (lowercase)
        brand = self.info.brand.lower().strip()
        model = self.info.model.lower().strip()

        # BoardView path check
        bv_dir = os.path.join(root, "guides", "boardview", brand)
        sch_dir = os.path.join(root, "guides", "schematic", brand)

        # Check boardview
        if os.path.isdir(bv_dir):
            for ext in [".brd", ".bvr", ".tvw", ".gr"]:
                check = os.path.join(bv_dir, f"{model}{ext}")
                if os.path.exists(check):
                    self.info.boardview_path = check
                    break

        # Check schematic
        if os.path.isdir(sch_dir):
            for ext in [".pdf", ".png", ".jpg"]:
                check = os.path.join(sch_dir, f"{model}{ext}")
                if os.path.exists(check):
                    self.info.schematic_path = check
                    break

    # ═════════════════════════════════════════════════════
    # Utilities
    # ═════════════════════════════════════════════════════

    def get_battery_level(self):
        out = self._adb("shell dumpsys battery")
        for line in out.splitlines():
            line = line.strip()
            if line.lower().startswith("level:"):
                try:
                    return int(line.split(":")[1].strip())
                except Exception:
                    pass
        return -1

    def get_storage_info(self):
        out = self._adb("shell df /data")
        lines = out.strip().split("\n")
        if len(lines) >= 2:
            return lines[-1].strip()
        return ""

    def is_charging(self):
        out = self._adb("shell dumpsys battery")
        if "AC powered: true" in out:
            return True
        if "USB powered: true" in out:
            return True
        return False