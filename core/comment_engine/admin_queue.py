REVIEW = {"update_request", "feature_request", "complaint", "fault_report"}

def needs_admin_review(classification):
    return any(i in REVIEW for i in classification.get("intents", []))
