from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Challenge:
    id: str
    instruction: str
    result: str | None = None  # pass | fail | None


@dataclass
class ProductWork:
    id: str
    name: str
    reason: str
    price_cents: int
    sku: str | None
    challenges: list[Challenge]
    challenge_index: int = 0
    status: str = "pending"  # pending | in_progress | refund | no_refund


@dataclass
class PaymentInfo:
    status: str  # full | partial | none
    refunded_cents: int
    provider_ref: str | None
    message: str


@dataclass
class Session:
    id: str
    products: list[ProductWork]
    product_index: int = 0
    status: str = "in_progress"  # in_progress | done
    payment: PaymentInfo | None = None
    last_result: str | None = None
