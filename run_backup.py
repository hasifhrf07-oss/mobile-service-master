import subprocess
import time
import os

BACKUP_DIR = r"D:\iPhone_13_Pro_Max_Backup"

def check_device():
    try:
        res = subprocess.run(["pymobiledevice3", "usbmux", "list"], capture_output=True, text=True, timeout=5)
        return "Identifier" in res.stdout or "UDID" in res.stdout or "DeviceName" in res.stdout
    except Exception:
        return False

os.makedirs(BACKUP_DIR, exist_ok=True)
print("\n=============================================")
print(" AUTO-RESUME BACKUP STARTED TO: ", BACKUP_DIR)
print("=============================================")
print("⚠️ DO NOT UNPLUG THE USB CABLE! KEEP PHONE UNLOCKED.\n")

while True:
    if not check_device():
        print(f"[{time.strftime('%H:%M:%S')}] Waiting for iPhone connection... Please plug in and Trust.")
        time.sleep(5)
        continue

    print(f"[{time.strftime('%H:%M:%S')}] iPhone Connected! Starting/Resuming backup...")
    try:
        process = subprocess.Popen(["pymobiledevice3", "backup2", "backup", "--full", BACKUP_DIR])
        process.wait()

        if process.returncode == 0:
            print("\n✅ BACKUP COMPLETED SUCCESSFULLY! Check D Drive.")
            break
        else:
            print("\n⚠️ Connection Lost! Backup paused.")
            print("Please plug the USB back in. It will resume automatically from the same point...\n")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nBackup stopped by user.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
