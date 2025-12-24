from datetime import datetime, timezone

def validate_entitlement(
    *,
    user_id,
    merchant_id,
    timestamp: datetime,
):
    """
    Determines whether a user is entitled to an offer at a merchant.

    Returns:
        (allowed: bool, reason_code: str | None)

    This mirrors issuer-side eligibility checks.
    """

    # --- Rule 1: User exists & verified ---
    # (Stubbed for prototype)
    if user_id is None:
        return False, "user_not_found"

    # In real system:
    # if not user.is_verified:
    #     return False, "user_not_verified"

    # --- Rule 2: Offer exists & active ---
    # (Stubbed: assume merchant has active offer)
    offer_active = True
    if not offer_active:
        return False, "offer_inactive"

    # --- Rule 3: Offer not already used today ---
    # (Stubbed — real version queries redemptions table)
    used_today = False
    if used_today:
        return False, "offer_already_used_today"

    # --- Rule 4: Time window check ---
    current_hour = timestamp.hour
    if current_hour < 6 or current_hour > 23:
        return False, "outside_offer_time_window"

    return True, None
