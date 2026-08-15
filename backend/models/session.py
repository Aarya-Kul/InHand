from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Challenge:
    id: str
    instruction: str
    success_criteria: str = ""
    kind: str = ""
    result: str | None = None  # pass | fail | None
    attempts: int = 0


@dataclass
class ProductWork:
    id: str
    name: str
    reason: str
    price_cents: int
    sku: str | None
    challenges: list[Challenge]
    challenge_index: int = 0
    takes: int = 0
    consecutive_fails: int = 0
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
    last_reason: str | None = None
    last_completed_product: ProductWork | None = None
