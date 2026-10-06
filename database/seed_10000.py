import sqlite3
import json
import os

DB = os.path.join(os.path.dirname(__file__), "devices.db")

BRANDS = {
    "Samsung": {
        "patterns": [
            ("SM-A{n:03d}F", 1, 80),
            ("SM-A{n:03d}G", 1, 40),
            ("SM-G{n:03d}B", 100, 200),
            ("SM-M{n:03d}F", 10, 60),
            ("SM-S{n:03d}B", 900, 930),
            ("SM-N{n:03d}", 900, 990),
            ("SM-J{n:03d}F", 100, 800),
        ],
        "chips": ["Exynos 7884", "Exynos 850", "Exynos 9611",
                  "Exynos 1280", "Exynos 2100", "Exynos 2200",
                  "Snapdragon 665", "Snapdragon 720G",
                  "Snapdragon 8 Gen 1", "Snapdragon 8 Gen 2"],
        "years": list(range(2015, 2025)),
        "issues": ["Boot loop", "FRP lock", "Charging port",
                   "Display flicker", "Battery drain"],
    },
    "Xiaomi": {
        "patterns": [
            ("Redmi {n}A", 1, 20),
            ("Redmi Note {n}", 5, 15),
            ("Redmi Note {n} Pro", 5, 15),
            ("POCO X{n}", 2, 7),
            ("POCO M{n}", 2, 7),
            ("Mi {n}", 5, 15),
            ("Redmi {n}C", 5, 15),
        ],
        "chips": ["Helio G35", "Helio G85", "Helio G96",
                  "Snapdragon 680", "Snapdragon 685", "Snapdragon 720G",
                  "Dimensity 700", "Dimensity 920", "Dimensity 1080"],
        "years": list(range(2016, 2025)),
        "issues": ["Mi account lock", "Boot loop", "Charging IC",
                   "Display damage", "Battery health"],
    },
    "Apple": {
        "patterns": [
            ("iPhone {n}", 5, 15),
            ("iPhone {n} Plus", 6, 8),
            ("iPhone {n} Pro", 11, 15),
            ("iPhone {n} Pro Max", 11, 15),
            ("iPhone SE {n}", 1, 3),
        ],
        "chips": ["A9", "A10", "A11 Bionic", "A12 Bionic",
                  "A13 Bionic", "A14 Bionic", "A15 Bionic", "A16 Bionic"],
        "years": list(range(2015, 2025)),
        "issues": ["Battery health", "Face ID", "Charging port",
                   "Display damage", "Water damage"],
    },
    "Vivo": {
        "patterns": [
            ("Y{n:02d}", 1, 99),
            ("V{n:02d}", 1, 30),
            ("X{n:02d}", 20, 100),
            ("S{n:02d}", 1, 20),
        ],
        "chips": ["Helio P35", "Helio G35", "Helio G70",
                  "Snapdragon 665", "Snapdragon 680",
                  "Dimensity 700", "Dimensity 900"],
        "years": list(range(2017, 2025)),
        "issues": ["Display", "Charging", "Network", "Battery"],
    },
    "Oppo": {
        "patterns": [
            ("A{n:02d}", 1, 99),
            ("Reno {n}", 1, 12),
            ("F{n:02d}", 1, 30),
            ("Find X{n}", 1, 8),
        ],
        "chips": ["Helio P35", "Helio G35", "Snapdragon 460",
                  "Snapdragon 662", "Snapdragon 680",
                  "Dimensity 700", "Dimensity 900"],
        "years": list(range(2016, 2025)),
        "issues": ["Boot loop", "Display", "Battery", "Charging"],
    },
    "Realme": {
        "patterns": [
            ("C{n:02d}", 1, 60),
            ("Narzo {n:02d}", 1, 60),
            ("{n} Pro", 5, 12),
            ("GT Neo {n}", 2, 5),
        ],
        "chips": ["Helio G35", "Helio G70", "Helio G85",
                  "Snapdragon 460", "Snapdragon 680",
                  "Dimensity 700", "Dimensity 900"],
        "years": list(range(2018, 2025)),
        "issues": ["Charging port", "Display", "Battery", "Boot loop"],
    },
    "OnePlus": {
        "patterns": [
            ("{n}", 1, 12),
            ("{n}T", 3, 11),
            ("{n} Pro", 1, 12),
            ("Nord {n}", 1, 5),
        ],
        "chips": ["Snapdragon 845", "Snapdragon 855", "Snapdragon 865",
                  "Snapdragon 870", "Snapdragon 888",
                  "Snapdragon 8 Gen 1", "Snapdragon 8 Gen 2"],
        "years": list(range(2016, 2025)),
        "issues": ["Display", "Battery", "Charging", "Camera"],
    },
    "Huawei": {
        "patterns": [
            ("P{n:02d}", 8, 60),
            ("Mate {n:02d}", 8, 60),
            ("Nova {n}", 1, 12),
            ("Y{n}", 5, 9),
        ],
        "chips": ["Kirin 710", "Kirin 810", "Kirin 820",
                  "Kirin 9000", "Kirin 990"],
        "years": list(range(2015, 2024)),
        "issues": ["Battery", "Display", "Charging", "Network"],
    },
    "Tecno": {
        "patterns": [
            ("Spark {n}", 1, 20),
            ("Camon {n}", 5, 20),
            ("Pova {n}", 1, 7),
        ],
        "chips": ["Helio A22", "Helio G35", "Helio G70",
                  "Helio G85", "Snapdragon 680"],
        "years": list(range(2018, 2025)),
        "issues": ["Charging", "Display", "Battery", "Speaker"],
    },
    "Itel": {
        "patterns": [
            ("A{n:02d}", 1, 80),
            ("P{n:02d}", 1, 55),
            ("S{n:02d}", 1, 23),
        ],
        "chips": ["Unisoc SC9863A", "Helio A22", "Helio G35",
                  "Unisoc T610"],
        "years": list(range(2018, 2025)),
        "issues": ["Charging", "Display", "Battery", "Software"],
    },
}

CLONES = [
    ("i13 Pro Max (fake)", "MT6580", 6, 2022),
    ("i14 Pro Max (fake)", "MT6580", 7, 2023),
    ("S22 Ultra (fake)", "MT6739", 8, 2022),
    ("S23 Ultra (fake)", "MT6761", 9, 2023),
    ("Note 12 Pro (fake)", "MT6580", 7, 2023),
    ("Reno 8 (fake)", "MT6580", 7, 2023),
    ("13 Pro (fake)", "MT6739", 8, 2023),
    ("14 Pro (fake)", "MT6761", 9, 2024),
]


def generate_devices():
    seen = set()
    idx = 0
    for brand, spec in BRANDS.items():
        for pattern, start, end in spec["patterns"]:
            for n in range(start, end + 1):
                try:
                    model = pattern.format(n=n)
                except (IndexError, KeyError, ValueError):
                    continue
                if not model or (brand, model) in seen:
                    continue
                seen.add((brand, model))
                idx += 1
                chip = spec["chips"][idx % len(spec["chips"])]
                year = spec["years"][idx % len(spec["years"])]
                android = str(min(15, max(8, 8 + (year - 2018) // 2)))
                yield {
                    "brand": brand, "model": model,
                    "codename": f"{brand.lower()}_{model.lower().replace(' ', '_')}",
                    "chipset": chip, "android_ver": android,
                    "release_year": year, "is_clone": 0,
                    "common_issues": json.dumps(spec["issues"]),
                    "hw_guide_path": f"guides/{brand.lower()}/{model.lower().replace(' ', '_')}.md",
                }
    for model, chip, av, year in CLONES:
        if ("Clone", model) in seen:
            continue
        seen.add(("Clone", model))
        yield {
            "brand": "Clone", "model": model,
            "codename": model.lower().replace(" ", "_"),
            "chipset": chip, "android_ver": str(av),
            "release_year": year, "is_clone": 1,
            "common_issues": json.dumps(["Fake build.prop",
                                          "No Google services"]),
            "hw_guide_path": f"guides/clone/{model.lower().replace(' ', '_')}.md",
        }


def seed(batch_size=500):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    added = 0
    batch = []
    for d in generate_devices():
        batch.append((
            d["brand"], d["model"], d["codename"], d["chipset"],
            d["android_ver"], d["release_year"], d["is_clone"],
            d["common_issues"], d["hw_guide_path"]
        ))
        if len(batch) >= batch_size:
            cur.executemany("""
                INSERT OR IGNORE INTO devices
                (brand, model, codename, chipset, android_ver,
                 release_year, is_clone, common_issues, hw_guide_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            added += cur.rowcount
            batch = []
    if batch:
        cur.executemany("""
            INSERT OR IGNORE INTO devices
            (brand, model, codename, chipset, android_ver,
             release_year, is_clone, common_issues, hw_guide_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        added += cur.rowcount
    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    clones = cur.execute("SELECT COUNT(*) FROM devices WHERE is_clone=1").fetchone()[0]
    conn.close()
    print("=" * 55)
    print("✅ Seed সম্পন্ন")
    print("=" * 55)
    print(f"➕ নতুন যোগ       : {added}")
    print(f"📱 মোট ডিভাইস    : {total}")
    print(f"🧬 ক্লোন মডেল    : {clones}")
    print("=" * 55)


if __name__ == "__main__":
    seed() 