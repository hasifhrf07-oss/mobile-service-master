"""
Rail Database — Power rail reference values for common chipsets.
Common rails with expected voltage ranges + troubleshooting hints.
"""


# ═══════════════════════════════════════════════════════════
# Common Power Rails — universal reference
# ═══════════════════════════════════════════════════════════
COMMON_RAILS = {
    "vbat": {
        "label": "VBAT (Battery)",
        "min": 3.5, "max": 4.3, "unit": "V",
        "typical": 3.8,
        "source": "Battery connector",
        "test_point": "Battery + terminal",
        "if_zero": "Battery dead / connector loose / fuse blown",
        "if_low": "Battery low charge / FUSE partial / connector corroded",
        "if_high": "Rare — check charger circuit",
        "priority": 1,
    },
    "vph_pwr": {
        "label": "VPH_PWR (PMIC input)",
        "min": 3.5, "max": 4.3, "unit": "V",
        "typical": 3.75,
        "source": "PMIC input",
        "test_point": "PMIC pin (see schematic)",
        "if_zero": "FUSE blown / PMIC input shorted / no power from battery",
        "if_low": "FUSE resistance / PMIC input leakage",
        "if_high": "Rare",
        "priority": 2,
    },
    "vdd_cpu": {
        "label": "VDD_CPU (CPU core)",
        "min": 0.85, "max": 1.35, "unit": "V",
        "typical": 1.10,
        "source": "CPU PMIC rail",
        "test_point": "CPU power pad",
        "if_zero": "CPU PMIC dead / CPU BGA issue / rail open",
        "if_low": "CPU PMIC weak / BGA partial",
        "if_high": "PMIC overvoltage — dangerous",
        "priority": 3,
    },
    "vdd_mem": {
        "label": "VDD_MEM (RAM)",
        "min": 1.05, "max": 1.25, "unit": "V",
        "typical": 1.12,
        "source": "Memory PMIC rail",
        "test_point": "RAM power pad",
        "if_zero": "Memory rail dead",
        "if_low": "Memory rail weak",
        "if_high": "Overvoltage",
        "priority": 4,
    },
    "vcc_io": {
        "label": "VCC_IO (I/O logic)",
        "min": 1.70, "max": 1.90, "unit": "V",
        "typical": 1.80,
        "source": "I/O PMIC rail",
        "test_point": "Various (see schematic)",
        "if_zero": "I/O rail dead — no peripheral",
        "if_low": "I/O rail weak",
        "if_high": "Overvoltage",
        "priority": 5,
    },
    "emmc_vcc": {
        "label": "eMMC VCC",
        "min": 3.0, "max": 3.5, "unit": "V",
        "typical": 3.3,
        "source": "eMMC power",
        "test_point": "eMMC power pad",
        "if_zero": "eMMC power rail dead — no boot",
        "if_low": "eMMC power weak — intermittent",
        "if_high": "Overvoltage — eMMC damage risk",
        "priority": 6,
    },
    "vcc_usb": {
        "label": "VCC_USB (USB VBUS)",
        "min": 4.75, "max": 5.25, "unit": "V",
        "typical": 5.0,
        "source": "USB VBUS",
        "test_point": "USB port VBUS",
        "if_zero": "USB cable / charger / USB port",
        "if_low": "Charging IC issue / USB port corroded",
        "if_high": "Charging IC overvoltage — replace IC",
        "priority": 7,
    },
    "vreg_l1": {
        "label": "VREG_L1 (aux)",
        "min": 1.15, "max": 1.35, "unit": "V",
        "typical": 1.25,
        "source": "PMIC LDO",
        "test_point": "See schematic",
        "if_zero": "LDO dead",
        "if_low": "LDO weak",
        "if_high": "LDO overvoltage",
        "priority": 8,
    },
    "vreg_l2": {
        "label": "VREG_L2 (aux)",
        "min": 2.7, "max": 3.0, "unit": "V",
        "typical": 2.85,
        "source": "PMIC LDO",
        "test_point": "See schematic",
        "if_zero": "LDO dead",
        "if_low": "LDO weak",
        "if_high": "LDO overvoltage",
        "priority": 9,
    },
    "vdd_gpu": {
        "label": "VDD_GPU",
        "min": 0.7, "max": 1.0, "unit": "V",
        "typical": 0.85,
        "source": "GPU rail",
        "test_point": "GPU power pad",
        "if_zero": "GPU rail dead",
        "if_low": "GPU rail weak",
        "if_high": "Overvoltage",
        "priority": 10,
    },
}


# ═══════════════════════════════════════════════════════════
# Current Draw Reference
# ═══════════════════════════════════════════════════════════
CURRENT_REFERENCE = {
    "dead": {
        "min": 0, "max": 2,
        "label": "Dead (no power)",
        "diagnosis": "PMIC dead / FUSE blown / battery connector",
    },
    "no_boot": {
        "min": 5, "max": 20,
        "label": "No Boot (Standby)",
        "diagnosis": "PMIC output present but boot fail — check CPU/eMMC rails",
    },
    "boot_start": {
        "min": 50, "max": 150,
        "label": "Boot Start",
        "diagnosis": "Boot sequence initiated — check eMMC data",
    },
    "android_load": {
        "min": 150, "max": 400,
        "label": "Android Loading",
        "diagnosis": "System loading — if hangs, eMMC/software issue",
    },
    "normal": {
        "min": 400, "max": 1500,
        "label": "Normal Running",
        "diagnosis": "Phone booted OK",
    },
    "short": {
        "min": 1500, "max": 99999,
        "label": "SHORT CIRCUIT",
        "diagnosis": "Immediate short — isolate rails",
    },
}


# ═══════════════════════════════════════════════════════════
# Common Symptoms → Likely faulty rails
# ═══════════════════════════════════════════════════════════
SYMPTOM_TO_RAILS = {
    "dead": ["vbat", "vph_pwr", "vdd_cpu", "emmc_vcc"],
    "no_boot": ["vdd_cpu", "vdd_mem", "emmc_vcc", "vcc_io"],
    "boot_loop": ["vdd_cpu", "emmc_vcc", "vdd_mem"],
    "no_charging": ["vcc_usb", "vbat"],
    "no_display": ["vcc_io", "vreg_l1", "vreg_l2"],
    "no_touch": ["vcc_io", "vreg_l1"],
    "no_network": ["vcc_io", "vreg_l2"],
    "no_camera": ["vreg_l1", "vreg_l2"],
    "no_audio": ["vreg_l2"],
}


# ═══════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════

def get_rail_info(rail_key):
    """Get rail reference by key"""
    return COMMON_RAILS.get(rail_key.lower().strip())


def all_rails():
    """All rails sorted by priority"""
    return sorted(
        COMMON_RAILS.items(),
        key=lambda x: x[1].get("priority", 999)
    )


def find_rails_by_symptom(symptom):
    """Symptom থেকে suspect rails"""
    return SYMPTOM_TO_RAILS.get(symptom.lower().strip(), [])


def get_current_category(current_ma):
    """Current reading দিয়ে category"""
    try:
        c = float(current_ma)
    except Exception:
        return None

    for key, ref in CURRENT_REFERENCE.items():
        if ref["min"] <= c <= ref["max"]:
            return key, ref
    return None, None 