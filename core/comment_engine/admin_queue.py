"""Admin Queue — flag comments needing human review"""

REVIEW_INTENTS = {"update_request", "feature_request", "complaint", "fault_report"}


def needs_admin_review(classification):
    intents = classification.get("intents", [])
    return any(i in REVIEW_INTENTS for i in intents)
