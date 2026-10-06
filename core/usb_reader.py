# USB Deep Reader — Comprehensive device info via ADB

import subprocess
import re


class USBReader:
    """USB data cable দিয়ে যতটুকু তথ্য পড়া যায়"""

    def __init__(self):
        self.info = {}

    def _adb(self, cmd, timeout=8):
        try:
            out = subprocess.check_output(
                ["adb"] + cmd.split(),
                stderr=subprocess.STDOUT,
                text=True, timeout=timeout
            )
            return out.strip()
        except Exception:
            return ""

    def _getprop(self, prop):
        return self._adb(f"shell getprop {prop}")

    def get_device_info(self):
        return {
            "brand": self._getprop("ro.product.brand") or
                     self._getprop("ro.product.manufacturer"),
            "model": self._getprop("ro.product.model"),
            "device": self._getprop("ro.product.device"),
            "android": self._getprop("ro.build.version.release"),
            "sdk": self._getprop("ro.build.version.sdk"),
            "serial": self._adb("get-serialno"),
            "build_id": self._getprop("ro.build.id"),
            "fingerprint": self._getprop("ro.build.fingerprint"),
            "board": self._getprop("ro.board.platform"),
            "hardware": self._getprop("ro.hardware"),
        }

    def get_battery_info(self):
        out = self._adb("shell dumpsys battery")
        info = {
            "level": -1, "voltage": 0, "temperature": 0,
            "status": "unknown", "health": "unknown",
            "power_source": "unknown",
        }
        if not out:
            return info

        for line in out.splitlines():
            line = line.strip()
            if "level:" in line:
                try:
                    info["level"] = int(line.split(":")[1].strip())
                except Exception:
                    pass
            elif "voltage:" in line:
                try:
                    info["voltage"] = int(line.split(":")[1].strip())
                except Exception:
                    pass
            elif "temperature:" in line:
                try:
                    info["temperature"] = int(line.split(":")[1].strip())
                except Exception:
                    pass
            elif "status:" in line:
                try:
                    s = int(line.split(":")[1].strip())
                    info["status"] = {
                        1: "Unknown", 2: "Charging",
                        3: "Discharging", 4: "Not charging", 5: "Full"
                    }.get(s, "Unknown")
                except Exception:
                    pass
            elif "health:" in line:
                try:
                    h = int(line.split(":")[1].strip())
                    info["health"] = {
                        1: "Unknown", 2: "Good", 3: "Overheat",
                        4: "Dead", 5: "Over voltage", 6: "Failure", 7: "Cold"
                    }.get(h, "Unknown")
                except Exception:
                    pass
            elif "AC powered: true" in line:
                info["power_source"] = "AC (charger)"
            elif "USB powered: true" in line:
                info["power_source"] = "USB"
        return info

    def get_cpu_info(self):
        info = {
            "hardware": self._getprop("ro.hardware"),
            "abi": self._getprop("ro.product.cpu.abi"),
            "abi2": self._getprop("ro.product.cpu.abi2"),
            "cores": 0,
            "frequency_max": "",
        }
        try:
            cpuinfo = self._adb("shell cat /proc/cpuinfo")
            info["cores"] = len(re.findall(r'processor\s*:', cpuinfo))
        except Exception:
            pass
        try:
            freq = self._adb("shell cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
            if freq and freq.isdigit():
                info["frequency_max"] = f"{int(freq)//1000} MHz"
        except Exception:
            pass
        return info

    def get_memory_info(self):
        info = {"total": 0, "free": 0, "used": 0,
                "total_str": "", "used_str": ""}
        try:
            out = self._adb("shell cat /proc/meminfo")
            for line in out.splitlines():
                if "MemTotal:" in line:
                    kb = int(re.search(r'(\d+)', line).group(1))
                    info["total"] = kb
                    info["total_str"] = f"{kb/1024/1024:.2f} GB"
                elif "MemAvailable:" in line:
                    kb = int(re.search(r'(\d+)', line).group(1))
                    info["free"] = kb
                    used = info["total"] - kb
                    info["used"] = used
                    info["used_str"] = f"{used/1024/1024:.2f} GB"
        except Exception:
            pass
        return info

    def get_storage_info(self):
        info = {}
        for partition, key in [("/data", "data"), ("/system", "system")]:
            try:
                out = self._adb(f"shell df {partition}")
                lines = out.strip().split("\n")
                if len(lines) >= 2:
                    parts = lines[-1].split()
                    if len(parts) >= 4:
                        total = int(parts[1]) / 1024 / 1024
                        used = int(parts[2]) / 1024 / 1024
                        info[key] = {
                            "total": f"{total:.2f} GB",
                            "used": f"{used:.2f} GB",
                            "free": f"{total-used:.2f} GB",
                            "usage_pct": f"{(used/total*100):.1f}%" if total else "0%",
                        }
            except Exception:
                pass
        return info

    def get_network_info(self):
        info = {"wifi": "unknown", "mobile": "unknown"}
        try:
            wifi = self._adb("shell dumpsys wifi | grep 'Wi-Fi is'")
            if "enabled" in wifi.lower():
                info["wifi"] = "Enabled"
            elif "disabled" in wifi.lower():
                info["wifi"] = "Disabled"
        except Exception:
            pass
        try:
            data = self._adb("shell settings get global mobile_data")
            info["mobile"] = "Enabled" if data == "1" else "Disabled"
        except Exception:
            pass
        return info

    def read_all(self):
        self.info = {
            "device": self.get_device_info(),
            "battery": self.get_battery_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "storage": self.get_storage_info(),
            "network": self.get_network_info(),
        }
        return self.info

    def format_report(self):
        if not self.info:
            self.read_all()
        d = self.info.get("device", {})
        b = self.info.get("battery", {})
        return (
            f"DEVICE INFO\n"
            f"  Brand: {d.get('brand', 'N/A')}\n"
            f"  Model: {d.get('model', 'N/A')}\n"
            f"  Chipset: {d.get('board', 'N/A')}\n"
            f"  Android: {d.get('android', 'N/A')}\n"
            f"  Serial: {d.get('serial', 'N/A')}\n"
            f"  Battery: {b.get('level', '?')}%"
        )