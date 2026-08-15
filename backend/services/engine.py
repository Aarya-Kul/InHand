"""Own the cursor: which product, which challenge, and when we are done."""

from __future__ import annotations

from config import MAX_CONSECUTIVE_FAILS, MAX_TAKES_PER_PRODUCT, PRODUCT_PASS_MODE
from models.schemas import (
    ChallengeView,
    CurrentView,
    LastView,
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


def _outcome(product: ProductWork) -> ProductOutcome:
    return ProductOutcome(
        id=product.id,
        name=product.name,
        refunded=product.status == "refund",
        passed_challenges=sum(1 for c in product.challenges if c.result == "pass"),
        total_challenges=len(product.challenges),
        price_cents=product.price_cents,
    )


def _finish_product(session: Session, refunded: bool) -> str:
    product = current_product(session)
    product.status = "refund" if refunded else "no_refund"
    session.last_completed_product = product
    if session.product_index + 1 < len(session.products):
        session.product_index += 1
        nxt = current_product(session)
        nxt.status = "in_progress"
        nxt.challenge_index = 0
        return "next_product"
    session.status = "done"
    settle(session)
    return "done"


def apply_challenge_result(session: Session, passed: bool, reason: str | None = None) -> str:
    """Score this take. Retry once on fail; two fails in a row or 4 takes ends the product."""
    if session.status == "done":
        return "done"

    product = current_product(session)
    challenge = product.challenges[product.challenge_index]
    product.takes += 1
    challenge.attempts += 1
    session.last_result = "pass" if passed else "fail"
    session.last_reason = reason
    session.last_completed_product = None

    if passed:
        challenge.result = "pass"
        product.consecutive_fails = 0
        last_challenge = product.challenge_index + 1 >= len(product.challenges)
        if last_challenge:
            return _finish_product(session, refunded=product_passes(product))
        if product.takes >= MAX_TAKES_PER_PRODUCT:
            return _finish_product(session, refunded=False)
        product.challenge_index += 1
        return "next_challenge"

    challenge.result = "fail"
    product.consecutive_fails += 1
    if product.consecutive_fails >= MAX_CONSECUTIVE_FAILS:
        return _finish_product(session, refunded=False)
    if product.takes >= MAX_TAKES_PER_PRODUCT:
        return _finish_product(session, refunded=False)
    return "retry_challenge"


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
            products=[_outcome(p) for p in session.products],
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
                attempt=challenge.attempts + 1,
            ),
        )

    last = None
    if session.last_result in ("pass", "fail"):
        finished = session.last_completed_product
        last = LastView(
            challenge=session.last_result,  # type: ignore[arg-type]
            reason=session.last_reason,
            product=("pass" if finished.status == "refund" else "fail") if finished else None,
            completed_product=_outcome(finished) if finished else None,
        )

    return SessionResponse(
        session_id=session.id,
        status=session.status,  # type: ignore[arg-type]
        last_result=session.last_result,  # type: ignore[arg-type]
        last=last,
        action=action,  # type: ignore[arg-type]
        current=current,
        terminal=terminal,
    )
