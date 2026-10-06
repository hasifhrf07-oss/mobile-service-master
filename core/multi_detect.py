"""Multi-Mode Detection — ADB / Fastboot / EDL / MTK / iPhone"""

import subprocess
import re


class MultiDetector:
    """
    ৫টি mode-এ device খোঁজে:
    1. ADB       — Normal Android
    2. Fastboot  — Bootloader mode
    3. EDL 9008  — Qualcomm dead boot
    4. MTK BROM  — MediaTek dead boot
    5. iPhone    — Apple devices
    """

    def __init__(self):
        self.result = {
            "mode": "none",
            "brand": "",
            "model": "",
            "chipset": "",
            "serial": "",
            "extra": "",
            "confidence": 0,
            "message": "",
        }

    def _run(self, cmd_list, timeout=10):
        try:
            return subprocess.check_output(
                cmd_list, stderr=subprocess.STDOUT,
                text=True, timeout=timeout
            ).strip()
        except Exception:
            return ""

    def _powershell(self, ps_command, timeout=10):
        return self._run(
            ["powershell", "-Command", ps_command],
            timeout=timeout
        )

    # ═════════════════════════════════════════════════════════
    # 1. ADB
    # ═════════════════════════════════════════════════════════

    def check_adb(self):
        out = self._run(["adb", "devices"])
        lines = out.strip().split("\n")

        for line in lines[1:]:
            if "\tdevice" in line:
                serial = line.split("\t")[0].strip()

                def adb(cmd):
                    return self._run(["adb"] + cmd.split(), timeout=5)

                brand = adb("shell getprop ro.product.brand") or \
                        adb("shell getprop ro.product.manufacturer")
                model = adb("shell getprop ro.product.model")
                chipset = adb("shell getprop ro.board.platform") or \
                          adb("shell getprop ro.hardware")
                android = adb("shell getprop ro.build.version.release")

                self.result.update({
                    "mode": "adb",
                    "brand": brand or "Unknown (ADB)",
                    "model": model or "Unknown",
                    "chipset": chipset or "Unknown",
                    "serial": serial,
                    "extra": f"Android {android}" if android else "",
                    "confidence": 100,
                    "message": "✅ Normal ADB mode — device connected"
                })
                return True

            elif "unauthorized" in line:
                serial = line.split("\t")[0].strip()
                self.result.update({
                    "mode": "adb_unauthorized",
                    "brand": "Unknown",
                    "model": "Unknown (Unauthorized)",
                    "serial": serial,
                    "confidence": 50,
                    "message": "⚠️ ADB detected but UNAUTHORIZED — accept popup on phone"
                })
                return True

        return False

    # ═════════════════════════════════════════════════════════
    # 2. Fastboot
    # ═════════════════════════════════════════════════════════

    def check_fastboot(self):
        out = self._run(["fastboot", "devices"], timeout=5)
        if out and "\t" in out:
            serial = out.split("\t")[0].strip()

            def fb(cmd):
                return self._run(["fastboot"] + cmd.split(), timeout=3)

            product = fb("getvar product")
            variant = fb("getvar variant")

            model = ""
            chipset = ""
            if "product:" in product:
                m = re.search(r'product:\s*(\S+)', product)
                if m:
                    model = m.group(1)
            if "variant:" in variant:
                m = re.search(r'variant:\s*(\S+)', variant)
                if m:
                    chipset = m.group(1)

            self.result.update({
                "mode": "fastboot",
                "brand": "Fastboot",
                "model": model or "Unknown (Fastboot)",
                "chipset": chipset or "Unknown",
                "serial": serial,
                "confidence": 90,
                "message": "⚠️ Fastboot mode — device in bootloader"
            })
            return True
        return False

    # ═════════════════════════════════════════════════════════
    # 3. EDL 9008
    # ═════════════════════════════════════════════════════════

    def check_edl(self):
        try:
            out = self._powershell(
                'Get-PnpDevice -PresentOnly | '
                'Where-Object {$_.FriendlyName -like "*9008*" -or '
                '$_.FriendlyName -like "*QDLoader*"} | '
                'Select-Object -First 1 -ExpandProperty FriendlyName'
            )
            if "9008" in out or "QDLoader" in out.lower():
                self.result.update({
                    "mode": "edl",
                    "brand": "Qualcomm",
                    "model": "EDL 9008 Mode",
                    "chipset": "Qualcomm (Snapdragon)",
                    "serial": "EDL-MODE",
                    "confidence": 95,
                    "message": "🔴 EDL 9008 — Qualcomm DEAD BOOT mode"
                })
                return True
        except Exception:
            pass
        return False

    # ═════════════════════════════════════════════════════════
    # 4. MTK BROM
    # ═════════════════════════════════════════════════════════

    def check_mtk(self):
        try:
            out = self._powershell(
                'Get-PnpDevice -PresentOnly | '
                'Where-Object {$_.FriendlyName -like "*MTK*" -or '
                '$_.FriendlyName -like "*MediaTek*" -or '
                '$_.FriendlyName -like "*Preloader*"} | '
                'Select-Object -First 1 -ExpandProperty FriendlyName'
            )
            if "MTK" in out or "MediaTek" in out or "Preloader" in out:
                chip = "MediaTek (BROM)"
                m = re.search(r'(MT\d{4})', out)
                if m:
                    chip = m.group(1)

                self.result.update({
                    "mode": "mtk",
                    "brand": "MediaTek",
                    "model": "BROM Mode",
                    "chipset": chip,
                    "serial": "MTK-BROM",
                    "confidence": 95,
                    "message": "🔴 MTK BROM — MediaTek DEAD BOOT mode"
                })
                return True
        except Exception:
            pass
        return False

    # ═════════════════════════════════════════════════════════
    # 5. iPhone
    # ═════════════════════════════════════════════════════════

    def check_iphone(self):
        try:
            out = self._powershell(
                'Get-PnpDevice -PresentOnly | '
                'Where-Object {$_.FriendlyName -like "*Apple*" -or '
                '$_.FriendlyName -like "*iPhone*"} | '
                'Select-Object -First 1 -ExpandProperty FriendlyName'
            )
            if "Apple" in out or "iPhone" in out:
                self.result.update({
                    "mode": "iphone",
                    "brand": "Apple",
                    "model": "iPhone",
                    "chipset": "Apple",
                    "serial": "iPHONE",
                    "confidence": 80,
                    "message": "🍎 iPhone detected — Check iTunes/lock screen"
                })
                return True
        except Exception:
            pass
        return False

    # ═════════════════════════════════════════════════════════
    # Auto-detect
    # ═════════════════════════════════════════════════════════

    def auto_detect_all(self):
        """সব mode try করবে"""
        # Reset result
        self.result = {
            "mode": "none",
            "brand": "",
            "model": "",
            "chipset": "",
            "serial": "",
            "extra": "",
            "confidence": 0,
            "message": "",
        }

        checks = [
            ("adb", self.check_adb),
            ("fastboot", self.check_fastboot),
            ("edl", self.check_edl),
            ("mtk", self.check_mtk),
            ("iphone", self.check_iphone),
        ]

        for mode_name, check_fn in checks:
            if check_fn():
                return self.result

        self.result.update({
            "mode": "none",
            "message": "❌ কোনো device পাওয়া যায়নি — সব mode fail"
        })
        return self.result

    def get_result(self):
        return self.result