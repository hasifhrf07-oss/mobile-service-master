"""Comment Engine — Smart classification + auto-reply + learning"""
from .classifier import classify_comment
from .auto_reply import generate_reply
from .learning_log import log_comment, retrain, get_stats
from .admin_queue import needs_admin_review

__all__ = [
    "classify_comment",
    "generate_reply",
    "log_comment",
    "retrain",
    "get_stats",
    "needs_admin_review",
]
