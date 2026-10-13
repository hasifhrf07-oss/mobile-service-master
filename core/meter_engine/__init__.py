"""Meter Engine — Photo analysis for Analogue/Multimeter/DC Supply"""
try:
    from .brand_detector import detect_meter_brand, get_meter_info
    from .ocr_reader import read_meter_photo, needs_manual_input
    from .accuracy_map import get_accuracy_margin, is_reading_reliable
    from .rail_extractor import extract_rail_from_reading
    from .cross_validator import cross_validate_readings
    from .anomaly_detector import detect_anomalies
    from .engine import analyze_meter_photos
except ImportError:
    pass

__all__ = ['analyze_meter_photos']
