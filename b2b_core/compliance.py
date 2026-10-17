# b2b_core/compliance.py
def verify_legal_documents(docs_list):
    """Verifies if all required legal docs are present. If not, locks the system."""
    required_docs = ["company_reg", "b2b_agreement", "api_usage_policy"]
    missing = [doc for doc in required_docs if doc not in docs_list]
    if missing:
        return {"status": "LOCKED", "missing": missing}
    return {"status": "CLEARED"}
