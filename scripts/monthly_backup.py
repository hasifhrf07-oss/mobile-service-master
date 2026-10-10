"""Monthly Backup — copies DB + users to backups/"""
import os
import shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
BACKUP_DIR = os.path.join(ROOT, "backups")


def run_backup():
    stamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, stamp)
    os.makedirs(dest, exist_ok=True)

    # Copy DB
    db_file = os.path.join(ROOT, "database", "devices.db")
    if os.path.exists(db_file):
        shutil.copy2(db_file, os.path.join(dest, "devices.db"))

    # Copy users
    users_file = os.path.join(ROOT, "users.json")
    if os.path.exists(users_file):
        shutil.copy2(users_file, os.path.join(dest, "users.json"))

    # Copy subscriptions
    subs_file = os.path.join(ROOT, "data", "subscriptions.json")
    if os.path.exists(subs_file):
        shutil.copy2(subs_file, os.path.join(dest, "subscriptions.json"))

    print(f"[BACKUP] {dest}")
    return dest


if __name__ == "__main__":
    run_backup()
