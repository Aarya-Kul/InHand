"""Stripe test-mode refunds. On pass we charge a test card, then refund it."""

from __future__ import annotations

from config import STRIPE_SECRET_KEY
from models.session import ProductWork

_MIN_USD_CENTS = 50  # Stripe's USD minimum


def settle_refunds(products: list[ProductWork]) -> tuple[str | None, str]:
    cents = sum(p.price_cents for p in products)
    if not products:
        return None, "No products eligible for refund"

    if not STRIPE_SECRET_KEY.strip():
        return (
            "re_placeholder",
            f"placeholder Stripe: would refund {cents} cents across {len(products)} product(s)",
        )

    amount = max(cents, _MIN_USD_CENTS)
    try:
        import stripe

        stripe.api_key = STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method="pm_card_visa",
            confirm=True,
            automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            description="InHand demo — original order (test card)",
            metadata={
                "inhand": "demo_charge",
                "products": ",".join(p.id for p in products),
            },
        )
        refund = stripe.Refund.create(
            payment_intent=intent.id,
            reason="requested_by_customer",
            metadata={"inhand": "returnless_refund"},
        )
        return (
            refund.id,
            f"Stripe refunded {amount} cents on PaymentIntent {intent.id}",
        )
    except Exception as exc:
        return None, f"Stripe error: {exc}"
