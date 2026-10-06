"""Auto Solver — Software problems auto fix"""

import subprocess
import time


class AutoSolver:
    """
    Software problem গুলো automatically solve করবে।
    সব action safe — data loss minimize।
    """

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def _adb(self, cmd, timeout=30):
        try:
            out = subprocess.check_output(
                ["adb"] + cmd.split(),
                stderr=subprocess.STDOUT,
                text=True, timeout=timeout
            )
            return True, out.strip()
        except subprocess.CalledProcessError as e:
            return False, str(e.output)
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    # ═════════════════════════════════════════════════════════
    # Individual Solutions
    # ═════════════════════════════════════════════════════════

    def solve_cache_wipe(self):
        self.log("🔄 Cache wipe শুরু...")
        ok, msg = self._adb("shell pm trim-caches 999999999")
        if not ok:
            return {"success": False, "message": f"Cache wipe fail: {msg}"}
        self.log("✅ Cache wipe সফল")
        return {"success": True, "message": "Cache wipe সম্পন্ন"}

    def solve_battery_stats_reset(self):
        self.log("🔋 Battery stats reset...")
        ok, _ = self._adb("shell dumpsys batterystats --reset")
        if not ok:
            return {"success": False, "message": "Battery reset fail"}
        self.log("✅ Battery stats reset সফল")
        return {"success": True, "message": "Battery stats reset"}

    def solve_network_reset(self):
        self.log("📶 Network reset...")
        self._adb("shell svc wifi disable")
        time.sleep(1)
        self._adb("shell svc wifi enable")
        time.sleep(1)
        self._adb("shell svc data disable")
        time.sleep(1)
        self._adb("shell svc data enable")
        self.log("✅ Network reset সফল")
        return {"success": True, "message": "Network reset সম্পন্ন"}

    def solve_display_reset(self):
        self.log("📺 Display reset...")
        self._adb("shell wm size reset")
        self._adb("shell wm density reset")
        self.log("✅ Display reset সফল")
        return {"success": True, "message": "Display reset সম্পন্ন"}

    def solve_soft_reboot(self):
        self.log("🔄 Soft reboot...")
        ok, msg = self._adb("reboot")
        if not ok:
            return {"success": False, "message": f"Reboot fail: {msg}"}
        self.log("✅ Reboot command সফল")
        return {"success": True, "message": "ফোন reboot হয়েছে"}

    # ═════════════════════════════════════════════════════════
    # Auto-select
    # ═════════════════════════════════════════════════════════

    def auto_solve(self, diagnosis):
        issue_type = diagnosis.get("issue_type", "").lower()
        symptoms = diagnosis.get("symptoms", {})

        if issue_type == "software":
            boot = symptoms.get("boot", "ok")
            charging = symptoms.get("charging", "ok")
            display = symptoms.get("display", "ok")
            network = symptoms.get("network", "ok")

            if boot == "loop":
                self.log("🔄 Boot loop → Cache wipe + Reboot")
                r1 = self.solve_cache_wipe()
                if r1["success"]:
                    time.sleep(2)
                    return self.solve_soft_reboot()
                return r1

            elif network in ("no", "weak"):
                self.log("📶 Network issue → Network reset")
                return self.solve_network_reset()

            elif display == "flicker":
                self.log("📺 Display flicker → Display reset")
                return self.solve_display_reset()

            elif charging == "slow":
                self.log("🔋 Slow charging → Battery stats reset")
                return self.solve_battery_stats_reset()

            else:
                self.log("🔄 General software → Reboot")
                return self.solve_soft_reboot()

        elif issue_type == "mixed":
            self.log("⚠️ Mixed → Software part first")
            return self.solve_cache_wipe()

        elif issue_type == "hardware":
            return {
                "success": False,
                "message": "⚠️ Hardware problem — Manual service required",
                "manual": True
            }

        elif issue_type == "account_lock":
            return {
                "success": False,
                "message": "🚫 Account lock — Owner verification required",
                "manual": True
            }

        return {
            "success": False,
            "message": "❓ Unknown issue — manual check",
            "manual": True
        } 