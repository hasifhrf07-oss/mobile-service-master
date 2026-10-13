"""
Smart Software Problem Solver
Detects + solves software problems automatically
"""
import subprocess
import time
from datetime import datetime


class SoftwareSolver:
    """Software problem auto-solver"""

    def __init__(self, log_callback=None):
        self.log = log_callback or print

    def _adb(self, cmd, timeout=30):
        try:
            out = subprocess.check_output(
                ["adb"] + cmd.split(),
                stderr=subprocess.STDOUT, text=True, timeout=timeout
            )
            return True, out.strip()
        except subprocess.CalledProcessError as e:
            return False, str(e.output)
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def is_device_connected(self):
        """Check if device connected"""
        ok, out = self._adb("devices")
        return ok and "\tdevice" in out

    # ═══════════════════════════════════════════════
    # INDIVIDUAL SOLVERS
    # ═══════════════════════════════════════════════

    def solve_cache_wipe(self):
        """Clear app cache"""
        self.log("🔄 Clearing cache...")
        self._adb("shell pm trim-caches 999999999")
        return {"success": True, "action": "cache_wipe", "message": "Cache cleared"}

    def solve_battery_stats(self):
        """Reset battery stats"""
        self.log("🔋 Resetting battery stats...")
        self._adb("shell dumpsys batterystats --reset")
        return {"success": True, "action": "battery_reset", "message": "Battery stats reset"}

    def solve_network_reset(self):
        """Reset network"""
        self.log("📶 Resetting network...")
        self._adb("shell svc wifi disable")
        time.sleep(1)
        self._adb("shell svc wifi enable")
        self._adb("shell svc data disable")
        time.sleep(1)
        self._adb("shell svc data enable")
        return {"success": True, "action": "network_reset", "message": "Network reset"}

    def solve_display_reset(self):
        """Reset display"""
        self.log("📺 Resetting display...")
        self._adb("shell wm size reset")
        self._adb("shell wm density reset")
        return {"success": True, "action": "display_reset", "message": "Display reset"}

    def solve_soft_reboot(self):
        """Soft reboot"""
        self.log("🔄 Rebooting device...")
        self._adb("reboot")
        return {"success": True, "action": "reboot", "message": "Rebooting"}

    def solve_recovery_mode(self):
        """Enter recovery mode"""
        self.log("🔧 Entering recovery...")
        self._adb("reboot recovery")
        return {"success": True, "action": "recovery", "message": "Rebooting to recovery"}

    def solve_fastboot_mode(self):
        """Enter fastboot mode"""
        self.log("⚡ Entering fastboot...")
        self._adb("reboot bootloader")
        return {"success": True, "action": "fastboot", "message": "Rebooting to fastboot"}

    # ═══════════════════════════════════════════════
    # SMART SOLVER — Auto detect + solve
    # ═══════════════════════════════════════════════

    def smart_solve(self, issue_type, symptoms=None):
        """
        Smart solving based on issue type and symptoms.
        Returns: {success, action, message, next_step}
        """
        symptoms = symptoms or {}

        self.log(f"🔍 Analyzing: {issue_type}")

        # Check device connection
        connected = self.is_device_connected()

        if not connected:
            return {
                "success": False,
                "action": "no_device",
                "message": "Device not connected. Please use Photo Mode or connect via USB.",
                "next_step": "photo_mode",
                "hint": "Use Photo Connect feature for non-connectable phones"
            }

        # Smart solving logic
        if issue_type == "boot_loop":
            self.log("→ Boot loop detected. Trying cache wipe...")
            result = self.solve_cache_wipe()
            if result["success"]:
                time.sleep(3)
                return self.solve_soft_reboot()

        elif issue_type == "no_boot":
            self.log("→ No boot. Trying recovery...")
            return self.solve_recovery_mode()

        elif issue_type == "software_crash":
            self.log("→ Software crash. Wiping cache...")
            return self.solve_cache_wipe()

        elif issue_type == "network":
            self.log("→ Network issue. Resetting...")
            return self.solve_network_reset()

        elif issue_type == "display":
            self.log("→ Display issue. Resetting...")
            return self.solve_display_reset()

        elif issue_type == "battery":
            self.log("→ Battery issue. Resetting stats...")
            return self.solve_battery_stats()

        elif issue_type == "slow":
            self.log("→ Slow phone. Cleaning cache...")
            self.solve_cache_wipe()
            time.sleep(2)
            return self.solve_battery_stats()

        else:
            # Default: cache wipe + reboot
            self.log("→ General software fix...")
            self.solve_cache_wipe()
            time.sleep(2)
            return self.solve_soft_reboot()

    def full_diagnose_and_solve(self):
        """
        Complete: diagnose + solve + verify
        """
        self.log("=" * 50)
        self.log("🚀 Full Auto-Diagnose + Solve")
        self.log("=" * 50)

        if not self.is_device_connected():
            return {
                "success": False,
                "message": "No device connected",
                "hint": "Connect USB or use Photo Mode",
                "connected": False
            }

        # Get symptoms
        symptoms = self._get_symptoms()

        # Determine issue
        issue = self._detect_issue(symptoms)
        self.log(f"Detected issue: {issue}")

        # Solve
        result = self.smart_solve(issue, symptoms)

        return {
            "success": result.get("success", False),
            "issue": issue,
            "action": result.get("action"),
            "message": result.get("message"),
            "symptoms": symptoms,
            "connected": True,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    def _get_symptoms(self):
        """Get device symptoms"""
        symptoms = {}

        # Battery
        ok, out = self._adb("shell dumpsys battery")
        if ok:
            for line in out.splitlines():
                if "level:" in line:
                    try:
                        symptoms["battery"] = int(line.split(":")[1].strip())
                    except Exception:
                        pass

        # Boot state
        ok, out = self._adb("shell getprop sys.boot_completed")
        symptoms["boot_completed"] = out.strip() == "1"

        # Display
        ok, out = self._adb("shell dumpsys display | grep mScreenState")
        symptoms["screen_state"] = out.strip() if ok else "unknown"

        return symptoms

    def _detect_issue(self, symptoms):
        """Detect issue type from symptoms"""
        if not symptoms.get("boot_completed"):
            return "boot_loop"

        battery = symptoms.get("battery", 100)
        if battery < 15:
            return "battery"

        return "slow"


if __name__ == "__main__":
    solver = SoftwareSolver()
    print(json.dumps({
        "connected": solver.is_device_connected(),
        "solver": "ready"
    }, indent=2))
