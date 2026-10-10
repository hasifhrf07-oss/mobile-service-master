"""Privacy Cleanup — auto-delete 30-day-old images"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run():
    deleted = 0
    try:
        from core.privacy_manager import cleanup_old_images
        deleted = cleanup_old_images(days=30)
    except ImportError:
        # core.privacy_manager not yet created — fallback
        uploads = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "static", "uploads"
        )
        if os.path.isdir(uploads):
            import shutil
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=30)
            for item in os.listdir(uploads):
                path = os.path.join(uploads, item)
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

    print(f"[PRIVACY] Deleted {deleted} items older than 30 days")
    return deleted


if __name__ == "__main__":
    run()
