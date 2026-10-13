"""Comment Engine"""
try:
    from .classifier import classify_comment
    from .auto_reply import generate_reply
    from .learning_log import log_comment, retrain, get_stats
    from .admin_queue import needs_admin_review
except ImportError:
    pass
