"""OCR Reader for meter photos"""
import os
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    OCR_OK = True
except ImportError:
    OCR_OK = False

def read_meter_photo(image_path, meter_type="multimeter"):
    result = {"ok": False, "raw_text": "", "value": None, "unit": "",
              "confidence": 0, "meter_type": meter_type, "image_path": image_path}
    if not image_path or not os.path.exists(image_path):
        result["error"] = "File not found"
        return result
    if not OCR_OK:
        result["fallback"] = "manual_input_required"
        return result
    try:
        img = Image.open(image_path).convert("RGB")
        text = pytesseract.image_to_string(img, lang="eng")
        result["raw_text"] = text
        result["ok"] = True
        parsed = _parse_reading(text)
        result.update(parsed)
        result["confidence"] = min(95, 60 + len(str(parsed.get("value", "")))*5) if parsed.get("value") else 20
        return result
    except Exception as e:
        result["error"] = str(e)
        result["fallback"] = "manual_input_required"
        return result

def _parse_reading(text):
    import re
    if not text:
        return {"value": None, "unit": ""}
    patterns = [r"(-?\d+\.\d+)\s*(V|v|mV|mA|A|Ω|ohm)", r"(-?\d+\.\d+)", r"(-?\d+)"]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            try:
                return {"value": float(m.group(1)), "unit": m.group(2) if len(m.groups())>1 else ""}
            except: continue
    return {"value": None, "unit": ""}

def needs_manual_input(r):
    return not r.get("ok") or r.get("value") is None or r.get("confidence", 0) < 70
