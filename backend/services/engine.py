"""Own the cursor: which product, which challenge, and when we are done."""

from __future__ import annotations

from config import PRODUCT_PASS_MODE
from models.schemas import (
    ChallengeView,
    CurrentView,
    PaymentView,
    ProductOutcome,
    ProductView,
    SessionResponse,
    TerminalView,
)
from models.session import ProductWork, Session
from services.payments import settle


def current_product(session: Session) -> ProductWork:
    return session.products[session.product_index]


def product_passes(product: ProductWork) -> bool:
    results = [c.result == "pass" for c in product.challenges]
    if not results:
        return False
    if PRODUCT_PASS_MODE == "majority":
        return sum(results) > len(results) / 2
    return all(results)


def apply_challenge_result(session: Session, passed: bool) -> str:
    """Mark the current challenge and advance. Returns next_challenge | next_product | done."""
    if session.status == "done":
        return "done"

    product = current_product(session)
    challenge = product.challenges[product.challenge_index]
    challenge.result = "pass" if passed else "fail"
    session.last_result = challenge.result

    if product.challenge_index + 1 < len(product.challenges):
        product.challenge_index += 1
        return "next_challenge"

    product.status = "refund" if product_passes(product) else "no_refund"

    if session.product_index + 1 < len(session.products):
        session.product_index += 1
        nxt = current_product(session)
        nxt.status = "in_progress"
        nxt.challenge_index = 0
        return "next_product"

    session.status = "done"
    settle(session)
    return "done"


def to_response(session: Session, action: str) -> SessionResponse:
    terminal = None
    current = None

    if session.status == "done" and session.payment:
        terminal = TerminalView(
            payment=PaymentView(
                status=session.payment.status,  # type: ignore[arg-type]
                refunded_cents=session.payment.refunded_cents,
                provider_ref=session.payment.provider_ref,
                message=session.payment.message,
            ),
            products=[
                ProductOutcome(
                    id=p.id,
                    name=p.name,
                    refunded=p.status == "refund",
                    passed_challenges=sum(1 for c in p.challenges if c.result == "pass"),
                    total_challenges=len(p.challenges),
                    price_cents=p.price_cents,
                )
                for p in session.products
            ],
        )
    else:
        product = current_product(session)
        challenge = product.challenges[product.challenge_index]
        current = CurrentView(
            product=ProductView(
                id=product.id,
                name=product.name,
                reason=product.reason,
                index=session.product_index + 1,
                total=len(session.products),
                price_cents=product.price_cents,
            ),
            challenge=ChallengeView(
                id=challenge.id,
                instruction=challenge.instruction,
                index=product.challenge_index + 1,
                total=len(product.challenges),
            ),
        )

    return SessionResponse(
        session_id=session.id,
        status=session.status,  # type: ignore[arg-type]
        last_result=session.last_result,  # type: ignore[arg-type]
        action=action,  # type: ignore[arg-type]
        current=current,
        terminal=terminal,
    )
