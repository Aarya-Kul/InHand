"""Request/response shapes the frontend should use. Keep this file stable."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProductIn(BaseModel):
    id: str
    name: str
    reason: str
    price_cents: int = 0
    sku: str | None = None


class StartSessionRequest(BaseModel):
    products: list[ProductIn] = Field(min_length=1)


class ChallengeView(BaseModel):
    id: str
    instruction: str
    index: int
    total: int


class ProductView(BaseModel):
    id: str
    name: str
    reason: str
    index: int
    total: int
    price_cents: int = 0


class CurrentView(BaseModel):
    product: ProductView
    challenge: ChallengeView


class ProductOutcome(BaseModel):
    id: str
    name: str
    refunded: bool
    passed_challenges: int
    total_challenges: int
    price_cents: int = 0


class PaymentView(BaseModel):
    status: Literal["full", "partial", "none"]
    refunded_cents: int
    provider_ref: str | None = None
    message: str


class TerminalView(BaseModel):
    payment: PaymentView
    products: list[ProductOutcome]


class SessionResponse(BaseModel):
    session_id: str
    status: Literal["in_progress", "done"]
    last_result: Literal["pass", "fail"] | None = None
    action: Literal["show_challenge", "next_challenge", "next_product", "done"]
    current: CurrentView | None = None
    terminal: TerminalView | None = None
