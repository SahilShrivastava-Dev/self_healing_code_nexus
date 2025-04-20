import os

# Simple subscription‑level gating
def get_subscription_level(user_id: str) -> str:
    # In production you'd query a user‑service or JWT claim.
    # Here we read an env var per user for demo:
    return os.getenv(f"USER_{user_id}_TIER", "free")  # free, pro, enterprise

def feature_enabled(feature: str, tier: str) -> bool:
    """
    Define which tiers unlock which features.
    """
    tier_map = {
        "free":    {"lint",},
        "pro":     {"lint", "testgen", "fallback", "analytics"},
        "enterprise": {"lint", "testgen", "fallback", "analytics", "autopr", "realtime"}
    }
    return feature in tier_map.get(tier, set())
