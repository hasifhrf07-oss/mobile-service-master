COMMON_RAILS = {
    "vbat": {"label": "VBAT (Battery)", "min": 3.5, "max": 4.3, "typical": 3.8, "priority": 1},
    "vph_pwr": {"label": "VPH_PWR (PMIC)", "min": 3.5, "max": 4.3, "typical": 3.75, "priority": 2},
    "vdd_cpu": {"label": "VDD_CPU (CPU)", "min": 0.85, "max": 1.35, "typical": 1.10, "priority": 3},
    "vdd_mem": {"label": "VDD_MEM (RAM)", "min": 1.05, "max": 1.25, "typical": 1.12, "priority": 4},
    "vcc_io": {"label": "VCC_IO (I/O)", "min": 1.70, "max": 1.90, "typical": 1.80, "priority": 5},
    "emmc_vcc": {"label": "eMMC VCC", "min": 3.0, "max": 3.5, "typical": 3.3, "priority": 6},
    "vcc_usb": {"label": "VCC_USB (VBUS)", "min": 4.75, "max": 5.25, "typical": 5.0, "priority": 7},
}

def get_rail_info(key):
    return COMMON_RAILS.get(key.lower().strip())

def all_rails():
    return sorted(COMMON_RAILS.items(), key=lambda x: x[1].get("priority", 999))
