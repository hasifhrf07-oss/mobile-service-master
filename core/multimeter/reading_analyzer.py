from core.multimeter.rail_database import get_rail_info

class ReadingAnalyzer:
    def analyze_voltage(self, rail_key, value):
        info = get_rail_info(rail_key)
        if not info:
            return {"ok": False, "message": f"Unknown rail: {rail_key}"}
        try: v = float(value)
        except: return {"ok": False, "message": f"Invalid: {value}"}
        vmin, vmax = info["min"], info["max"]
        if v < 0.1:
            status, sev, color = "DEAD", "CRITICAL", "#f38ba8"
            msg = f"❌ DEAD — {info['label']} = 0V"
        elif v < vmin:
            status, sev, color = "LOW", "WARN", "#f9e2af"
            msg = f"⚠️ LOW — {info['label']} = {v}V"
        elif v > vmax:
            status, sev, color = "HIGH", "WARN", "#f9e2af"
            msg = f"⚠️ HIGH — {info['label']} = {v}V"
        else:
            status, sev, color = "NORMAL", "OK", "#a6e3a1"
            msg = f"✅ NORMAL — {info['label']} = {v}V"
        return {"ok": True, "rail": rail_key, "label": info["label"], "value": v,
                "status": status, "severity": sev, "message": msg, "color": color}
