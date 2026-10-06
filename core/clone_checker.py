"""Clone Checker — Score-based"""


class CloneChecker:
    KNOWN_CHIPS = [
        "qcom", "qualcomm", "msm", "sm", "sdm", "snapdragon",
        "mt", "mediatek", "helio", "dimensity",
        "exynos", "kirin", "unisoc", "sprd",
        "apple", "a1", "bionic",
    ]

    REAL_BRANDS = {
        "samsung", "xiaomi", "redmi", "poco", "mi", "vivo", "oppo",
        "realme", "oneplus", "apple", "iphone", "huawei", "honor",
        "nokia", "motorola", "sony", "lg", "tecno", "itel",
        "infinix", "asus", "google", "pixel", "nothing",
    }

    MAX_REAL_ANDROID = 15

    def analyze(self, info) -> list:
        reasons = []
        brand = (info.brand or "").lower().strip()
        model = (info.model or "").lower().strip()
        fp = (info.build_fingerprint or "").lower()
        chip = (info.chipset or "").lower()
        android = (info.android or "").strip()

        if brand and fp and brand not in fp:
            reasons.append(f"brand/fingerprint mismatch: {info.brand}")

        if chip and not any(c in chip for c in self.KNOWN_CHIPS):
            reasons.append(f"unknown chipset: {info.chipset}")

        if brand == "samsung" and model and not model.startswith("sm-"):
            reasons.append(f"Samsung model format invalid: {info.model}")

        if ("iphone" in model or brand == "apple") and info.android:
            reasons.append("iPhone running Android (clone)")

        if android:
            try:
                ver = float(android.split(".")[0])
                if ver > self.MAX_REAL_ANDROID:
                    reasons.append(f"unrealistic Android version: {android}")
            except ValueError:
                reasons.append(f"unparseable Android version: {android}")

        if fp:
            for marker in ("generic", "test-keys", "eng.", "userdebug"):
                if marker in fp:
                    reasons.append(f"non-production fingerprint: {marker}")
                    break

        if brand and brand not in self.REAL_BRANDS:
            if "unknown" not in brand and "clone" not in brand:
                reasons.append(f"unrecognized brand: {info.brand}")

        if not model or model in ("unknown", "null", ""):
            reasons.append("empty/unknown model name")

        return reasons

    def is_clone(self, reasons, threshold=3):
        return len(reasons) >= threshold

    def verdict(self, reasons):
        n = len(reasons)
        if n == 0:
            return "✅ অরিজিনাল ডিভাইসের সম্ভাবনা"
        elif n < 3:
            return f"⚠️ সন্দেহজনক ({n} flag)"
        else:
            return f"🚨 ক্লোন/কপি ফোন নিশ্চিত ({n} flag)"