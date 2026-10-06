"""Reading Analyzer — Voltage / Current reading interpret.
"""

from core.multimeter.rail_database import (
    get_rail_info, get_current_category, find_rails_by_symptom
)


class ReadingAnalyzer:
    """
    একটা reading নিয়ে analysis দেবে।
    """

    def analyze_voltage(self, rail_key, value):
        """
        Voltage reading analyze করো।

        Returns:
        {
            "ok": True/False,
            "rail": "vbat",
            "label": "VBAT (Battery)",
            "value": 3.78,
            "expected": "3.5-4.3V",
            "status": "NORMAL" | "LOW" | "HIGH" | "DEAD",
            "severity": "OK" | "WARN" | "CRITICAL",
            "message": "...",
            "hint": "...",
            "color": "#a6e3a1"  # for UI
        }
        """
        info = get_rail_info(rail_key)
        if not info:
            return {
                "ok": False,
                "message": f"Unknown rail: {rail_key}",
            }

        try:
            v = float(value)
        except (ValueError, TypeError):
            return {
                "ok": False,
                "message": f"Invalid value: {value}",
            }

        vmin = info["min"]
        vmax = info["max"]
        expected_str = f"{vmin}-{vmax}{info['unit']}"

        # Determine status
        if v < 0.1:
            status = "DEAD"
            severity = "CRITICAL"
            color = "#f38ba8"
            message = f"❌ DEAD — {info['label']} = 0V"
            hint = info["if_zero"]
        elif v < vmin:
            status = "LOW"
            severity = "WARN"
            color = "#f9e2af"
            message = f"⚠️ LOW — {info['label']} = {v}V (need {expected_str})"
            hint = info["if_low"]
        elif v > vmax:
            status = "HIGH"
            severity = "WARN"
            color = "#f9e2af"
            message = f"⚠️ HIGH — {info['label']} = {v}V (max {vmax}V)"
            hint = info["if_high"]
        else:
            status = "NORMAL"
            severity = "OK"
            color = "#a6e3a1"
            message = f"✅ NORMAL — {info['label']} = {v}V"
            hint = ""

        return {
            "ok": True,
            "rail": rail_key.lower(),
            "label": info["label"],
            "value": v,
            "expected": expected_str,
            "typical": info.get("typical"),
            "status": status,
            "severity": severity,
            "message": message,
            "hint": hint,
            "source": info.get("source", ""),
            "test_point": info.get("test_point", ""),
            "color": color,
            "priority": info.get("priority", 999),
        }

    def analyze_current(self, value_ma):
        """
        Current reading analyze করো।
        """
        try:
            v = float(value_ma)
        except (ValueError, TypeError):
            return {
                "ok": False,
                "message": f"Invalid value: {value_ma}",
            }

        key, ref = get_current_category(v)

        if not ref:
            return {
                "ok": True,
                "value": v,
                "category": "unknown",
                "label": "Unknown",
                "message": f"❓ {v} mA — no reference range",
                "color": "#6c7086",
            }

        # Color by category
        if key == "short":
            color = "#f38ba8"
            severity = "CRITICAL"
        elif key in ("dead", "no_boot"):
            color = "#f9e2af"
            severity = "WARN"
        elif key == "normal":
            color = "#a6e3a1"
            severity = "OK"
        else:
            color = "#89b4fa"
            severity = "INFO"

        return {
            "ok": True,
            "value": v,
            "category": key,
            "label": ref["label"],
            "diagnosis": ref["diagnosis"],
            "message": f"{ref['label']}: {v} mA",
            "color": color,
            "severity": severity,
        }

    def analyze_batch(self, readings_dict):
        """
        একাধিক rail একসাথে analyze।
        readings_dict = {"vbat": 3.78, "vdd_cpu": 0.0, ...}
        """
        results = []
        for rail_key, value in readings_dict.items():
            r = self.analyze_voltage(rail_key, value)
            if r.get("ok"):
                results.append(r)

        # Sort by priority
        results.sort(key=lambda x: x.get("priority", 999))

        # Summary
        critical = sum(1 for r in results if r["severity"] == "CRITICAL")
        warn = sum(1 for r in results if r["severity"] == "WARN")
        ok = sum(1 for r in results if r["severity"] == "OK")

        # Verdict
        if critical:
            verdict = f"🔴 {critical} critical rail(s) — hardware fault"
            verdict_color = "#f38ba8"
        elif warn:
            verdict = f"🟡 {warn} rail(s) deviate — investigate"
            verdict_color = "#f9e2af"
        else:
            verdict = "✅ All rails normal"
            verdict_color = "#a6e3a1"

        return {
            "ok": True,
            "readings": results,
            "summary": {
                "critical": critical,
                "warning": warn,
                "ok": ok,
                "total": len(results),
                "verdict": verdict,
                "verdict_color": verdict_color,
            }
        }

    def suggest_next_rail(self, checked_rails):
        """
        Checked rails list থেকে পরের rail suggest করো।
        """
        from core.multimeter.rail_database import COMMON_RAILS
        checked = set(r.lower() for r in checked_rails)

        remaining = []
        for key, info in COMMON_RAILS.items():
            if key not in checked:
                remaining.append((info.get("priority", 999), key, info))

        remaining.sort()
        if remaining:
            return {
                "rail": remaining[0][1],
                "label": remaining[0][2]["label"],
                "expected": f"{remaining[0][2]['min']}-{remaining[0][2]['max']}V",
                "test_point": remaining[0][2].get("test_point", ""),
            }
        return None

    def diagnose_from_symptom(self, symptom, readings):
        """
        Symptom + readings থেকে full diagnosis।
        """
        rails_to_check = find_rails_by_symptom(symptom)

        analysis = self.analyze_batch(readings)

        suspects = []
        for r in analysis["readings"]:
            if r["rail"] in rails_to_check and r["severity"] in ("CRITICAL", "WARN"):
                suspects.append(r)

        return {
            "ok": True,
            "symptom": symptom,
            "rails_of_interest": rails_to_check,
            "analysis": analysis,
            "suspects": suspects,
        }