"""Refund every product that cleared the challenge threshold."""

from __future__ import annotations

from integrations.stripe_client import settle_refunds
from models.session import PaymentInfo, ProductWork, Session


def eligible_products(session: Session) -> list[ProductWork]:
    return [p for p in session.products if p.status == "refund"]


def settle(session: Session) -> PaymentInfo:
    refunded = eligible_products(session)
    total = len(session.products)
    cents = sum(p.price_cents for p in refunded)

    if not refunded:
        status = "none"
    elif len(refunded) == total:
        status = "full"
    else:
        status = "partial"

    ref, message = settle_refunds(refunded)
    session.payment = PaymentInfo(
        status=status,
        refunded_cents=cents,
        provider_ref=ref,
        message=message,
    )
    return session.payment
