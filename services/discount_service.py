def calculate_discount(
    *,
    original_amount: float,
    discount_type: str,
    discount_value: float,
    max_cap: float | None = None,
):
    """
    Pure deterministic discount calculator.

    Supports:
    - percentage
    - flat
    - optional caps
    """

    if original_amount <= 0:
        raise ValueError("Invalid original amount")

    if discount_type == "percentage":
        discount = original_amount * (discount_value / 100)

    elif discount_type == "flat":
        discount = discount_value

    else:
        raise ValueError("Unsupported discount type")

    if max_cap is not None:
        discount = min(discount, max_cap)

    discounted_amount = max(original_amount - discount, 0)

    return {
        "discounted_amount": round(discounted_amount, 2),
        "discount_value": round(discount, 2),
    }
