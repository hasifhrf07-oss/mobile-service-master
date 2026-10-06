"""Analyzer — SW/HW/Mixed/Account decision tree"""

from dataclasses import dataclass, field
from enum import Enum


class IssueType(Enum):
    SOFTWARE = "software"
    HARDWARE = "hardware"
    MIXED = "mixed"
    ACCOUNT = "account_lock"
    UNKNOWN = "unknown"


@dataclass
class Diagnosis:
    issue_type: IssueType
    summary: str
    evidence: list = field(default_factory=list)
    sw_actions: list = field(default_factory=list)
    hw_guide: list = field(default_factory=list)
    requires_consent: bool = False

    def to_dict(self):
        return {
            "issue_type": self.issue_type.value,
            "summary": self.summary,
            "evidence": self.evidence,
            "sw_actions": self.sw_actions,
            "hw_guide": self.hw_guide,
            "requires_consent": self.requires_consent,
        }


class Analyzer:
    def analyze(self, info, symptoms: dict) -> Diagnosis:
        ev, sw, hw = [], [], []

        lock = symptoms.get("lock_screen", "none")
        if lock in ("frp", "icloud", "mi"):
            label = {"frp": "Google FRP", "icloud": "Apple Activation Lock",
                     "mi": "Mi Account"}[lock]
            return Diagnosis(
                issue_type=IssueType.ACCOUNT,
                summary=f"{label} লক — মালিক যাচাই ছাড়া সমাধান অবৈধ",
                evidence=[f"Lock detected: {lock}"],
                sw_actions=[
                    "মূল মালিকের কাছ থেকে credentials আনাও",
                    "অথবা ক্রয়ের প্রমাণপত্র (IMEI সহ) সংগ্রহ করো",
                    "Official channel-এ unlock request পাঠাও",
                ],
                hw_guide=[],
                requires_consent=True,
            )

        if symptoms.get("water") == "yes":
            ev.append("Water damage reported")
            hw.extend([
                "Immediate power-off",
                "Ultrasonic clean (IPA)",
                "Corrosion check under microscope",
                "BoardView trace check",
            ])

        boot = symptoms.get("boot", "ok")
        if boot == "dead":
            ev.append("No boot response")
            hw.extend([
                "PMIC rail check (VPH_PWR, VBAT)",
                "eMMC/UFS continuity test",
                "Power button line check",
            ])
        elif boot == "loop":
            ev.append("Boot loop")
            sw.extend([
                "Cache wipe (recovery)",
                "Stock ROM reflash",
                "eMMC health check",
            ])

        disp = symptoms.get("display", "ok")
        if disp == "broken":
            ev.append("Display broken")
            hw.extend(["LCD/digitizer replace", "Connector reflow"])
        elif disp == "flicker":
            ev.append("Display flicker")
            hw.extend(["Flex cable reseat", "LCD IC reflow"])

        touch = symptoms.get("touch", "ok")
        if touch == "no":
            ev.append("Touch not working")
            hw.append("Touch digitizer / connector check")

        chg = symptoms.get("charging", "ok")
        if chg == "no":
            ev.append("No charging")
            hw.extend([
                "USB port continuity test",
                "Charging IC check",
                "VBUS rail voltage check",
            ])
        elif chg == "slow":
            ev.append("Slow charging")
            hw.extend(["Charging IC", "Battery health check"])

        net = symptoms.get("network", "ok")
        if net == "no":
            ev.append("No network")
            hw.extend(["PA IC check", "Antenna switch check"])
            sw.append("Modem firmware reflash")

        bat = symptoms.get("battery", "ok")
        if bat == "drain":
            ev.append("Battery drain")
            hw.append("Battery health check")
        elif bat == "swell":
            ev.append("Battery swollen")
            hw.append("Battery replacement")

        if symptoms.get("speaker") == "no":
            ev.append("Speaker dead")
            hw.append("Speaker / amplifier check")
        if symptoms.get("camera") == "no":
            ev.append("Camera dead")
            hw.append("Camera module / flex check")

        if sw and hw:
            it = IssueType.MIXED
            summary = "মিশ্র সমস্যা — আগে সফটওয়্যার, তারপর হার্ডওয়্যার"
        elif sw:
            it = IssueType.SOFTWARE
            summary = "সফটওয়্যার সমস্যা — ফ্ল্যাশ/আনলক দিয়ে সমাধান"
        elif hw:
            it = IssueType.HARDWARE
            summary = "হার্ডওয়্যার সমস্যা — ম্যানুয়াল সার্ভিসিং প্রয়োজন"
        else:
            it = IssueType.UNKNOWN
            summary = "কোনো স্পষ্ট সমস্যা সনাক্ত হয়নি"

        return Diagnosis(
            issue_type=it, summary=summary, evidence=ev,
            sw_actions=sw, hw_guide=hw,
            requires_consent=(it in (IssueType.SOFTWARE, IssueType.MIXED)),
        ) 