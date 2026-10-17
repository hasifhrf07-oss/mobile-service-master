# b2b_core/limits.py
TEST_MODE = True
BASE_LIMIT = 100

def get_dynamic_limit(is_verified):
    """Scales limits only after verification."""
    if not TEST_MODE and is_verified:
        return BASE_LIMIT * 10
    return BASE_LIMIT
