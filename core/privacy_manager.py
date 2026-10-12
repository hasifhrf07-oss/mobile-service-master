"""Privacy Manager — 30-day auto-cleanup"""
import os
import shutil
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(__file__))
UPLOADS = os.path.join(ROOT, "static", "uploads")


def cleanup_old_images(days=30):
    if not os.path.isdir(UPLOADS):
        return 0
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    for item in os.listdir(UPLOADS):
        path = os.path.join(UPLOADS, item)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                deleted += 1
        except Exception:
            continue
    return deleted


def cleanup_job_folder(job_id):
    folder = os.path.join(UPLOADS, job_id)
    if not os.path.isdir(folder):
        return False
    try:
        shutil.rmtree(folder)
        return True
    except Exception:
        return False


def get_retention_policy():
    return {
        "images_days": 30,
        "text_days": 30,
        "auto_delete_on_completion": False,
        "policy": "Client data auto-deleted after 30 days",
    }
