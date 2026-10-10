
"""Meter Engine — Photo analysis for Analogue/Multimeter/DC Supply"""
from .brand_detector import detect_meter_brand, get_meter_info
from .ocr_reader import read_meter_photo, needs_manual_input
from .accuracy_map import get_accuracy_margin, is_reading_reliable
from .rail_extractor import extract_rail_from_reading
from .cross_validator import cross_validate_readings
from .anomaly_detector import detect_anomalies
from .engine import analyze_meter_photos

__all__ = [
    "detect_meter_brand",
    "get_meter_info",
    "read_meter_photo",
    "needs_manual_input",
    "get_accuracy_margin",
    "is_reading_reliable",
    "extract_rail_from_reading",
    "cross_validate_readings",
    "detect_anomalies",
    "analyze_meter_photos",
]