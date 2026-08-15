"""
Stripe integration — fill this in.

settle_refunds: refund every product the workflow marked as eligible.
"""

from __future__ import annotations

from models.session import ProductWork


def settle_refunds(products: list[ProductWork]) -> tuple[str | None, str]:
    """Refund the given products. Return (provider_ref, message).

    TODO: Create Stripe refunds (or a single refund) for these line items.
    Use STRIPE_SECRET_KEY from config. Until then this is a fake success.
    """
    cents = sum(p.price_cents for p in products)
    if not products:
        return None, "No products eligible for refund"
    return (
        "re_placeholder",
        f"placeholder Stripe: would refund {cents} cents across {len(products)} product(s)",
    )
