"""
Force Seed - Direct insert without assumptions
"""
import sqlite3, os, random

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "devices.db")
conn = sqlite3.connect(DB)
c = conn.cursor()

# Get schema
c.execute("PRAGMA table_info(devices)")
cols = [row[1] for row in c.fetchall()]
print("Columns:", cols)

c.execute("SELECT COUNT(*) FROM devices")
before = c.fetchone()[0]
print(f"Before: {before}")

BRANDS = ["Samsung","Xiaomi","Vivo","Oppo","Realme","OnePlus","Apple","Huawei",
          "Honor","Infinix","Tecno","itel","Nokia","Motorola","Google","Sony",
          "Nothing","Asus","Lenovo","LG","HTC","ZTE","Nubia","Alcatel","Gionee",
          "Meizu","Sharp","Panasonic","Blackview","Ulefone","Doogee","Oukitel",
          "Cubot","Umidigi","Lava","Micromax","Karbonn","Intex","Maximus","Okapia"]

CHIPS = ["Snapdragon 888","Snapdragon 870","Snapdragon 778G","Snapdragon 695",
         "Snapdragon 680","Exynos 2100","Exynos 1280","Dimensity 1200",
         "Dimensity 900","Helio G95","Helio G85","Kirin 9000","Apple A15",
         "Apple A14","Unisoc T612"]

ANDROID = ["9","10","11","12","13","14","15"]

added = 0
target = 10000
attempts = 0
max_attempts = 50000

while added < target and attempts < max_attempts:
    attempts += 1
    brand = random.choice(BRANDS)
    model = f"{brand[:3].upper()}-{random.randint(100, 9999)}{random.choice(['A','B','C','Pro','Max','Lite','5G',''])}"
    codename = f"{brand.lower()}_{model.lower().replace('-','_').replace(' ','_')}"
    chipset = random.choice(CHIPS)
    android = random.choice(ANDROID)
    year = random.randint(2015, 2025)
    issue = "Unknown - auto"
    guide = f"guides/{brand.lower()}/{codename}.md"

    try:
        c.execute(
            "INSERT INTO devices (brand, model, codename, chipset, android_ver, release_year, common_issues, hw_guide_path) VALUES (?,?,?,?,?,?,?,?)",
            (brand, model, codename, chipset, android, year, issue, guide)
        )
        added += 1
        if added % 1000 == 0:
            print(f"  Added: {added}")
    except Exception:
        pass

conn.commit()
c.execute("SELECT COUNT(*) FROM devices")
after = c.fetchone()[0]
conn.close()

print(f"✅ Added: {added}")
print(f"📊 After: {after}")
