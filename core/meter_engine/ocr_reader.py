"""OCR Reader — Tesseract + fallback for meter photos"""
import os
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    OCR_OK = True
except ImportError:
    OCR_OK = False


def read_meter_photo(image_path, meter_type="multimeter"):
    result = {
        "ok": False, "raw_text": "", "value": None, "unit": "",
        "confidence": 0, "meter_type": meter_type,
        "image_path": image_path,
        "read_at": datetime.now().isoformat(timespec="seconds"),
    }
    if not image_path or not os.path.exists(image_path):
        result["error"] = "Image file not found"
        return result
    if not OCR_OK:
        result["error"] = "Tesseract/PIL not installed"
        result["fallback"] = "manual_input_required"
        return result
    try:
        img = Image.open(image_path).convert("RGB")
        text = pytesseract.image_to_string(img, lang="eng")
        result["raw_text"] = text
        result["ok"] = True
        parsed = _parse_reading(text, meter_type)
        result.update(parsed)
        if parsed.get("value") is not None:
            result["confidence"] = min(95, 60 + len(str(parsed["value"])) * 5)
        else:
            result["confidence"] = 20
            result["fallback"] = "manual_input_required"
        return result
    except Exception as e:
        result["error"] = str(e)
        result["fallback"] = "manual_input_required"
        return result


def _parse_reading(text, meter_type):
    import re
    if not text:
        return {"value": None, "unit": ""}
    patterns = [
        r"(-?\d+\.\d+)\s*(V|v|mV|mA|A|Ω|ohm|kΩ)",
        r"(-?\d+\.\d+)",
        r"(-?\d+)\s*(V|v|mV|mA|A)",
        r"(-?\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            try:
                val = float(m.group(1))
                unit = m.group(2) if len(m.groups()) > 1 else ""
                return {"value": val, "unit": unit}
            except (ValueError, IndexError):
                continue
    return {"value": None, "unit": ""}


def needs_manual_input(ocr_result):
    if not ocr_result.get("ok"):
        return True
    if ocr_result.get("value") is None:
        return True
    if ocr_result.get("confidence", 0) < 70:
        return True
    return False
