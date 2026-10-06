import os

files = [
    "core/analyzer.py",
    "core/clone_checker.py",
    "core/consent.py",
    "core/detector.py",
    "core/updater.py",
    "core/voice.py",
    "ui/tab_detect.py",
    "ui/tab_diagnose.py",
    "ui/tab_history.py",
    "ui/tab_settings.py",
    "ui/tab_update.py",
    "ui/main_window.py",
    "ui/style.py",
    "data/db.py",
]

fixed = 0
for f in files:
    if not os.path.exists(f):
        print("SKIP (not found): " + f)
        continue

    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()

    stripped = content.lstrip()
    if stripped.startswith('"""') or stripped.startswith("'''"):
        print("OK: " + f)
        continue

    lines = content.split("\n")
    first = lines[0] if lines else ""
    if not first.strip():
        print("SKIP (empty first line): " + f)
        continue

    new_content = '"""\n' + first + '\n"""\n' + "\n".join(lines[1:])
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(new_content)
    print("FIXED: " + f)
    fixed += 1

print("")
print("Total fixed: " + str(fixed))