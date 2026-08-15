"""Turn selected products + refund reasons into a challenge plan per product."""

from __future__ import annotations

import uuid

from integrations.openai_client import plan_challenges
from models.schemas import ProductIn
from models.session import Challenge, ProductWork, Session
from skills.planner import cap_for_demo, fallback_plan


def create_session(products: list[ProductIn]) -> Session:
    planned: list[ProductWork] = []
    for product in products:
        planned_challenges = cap_for_demo(plan_challenges(product) or fallback_plan(product).challenges)
        challenges = [
            Challenge(
                id=f"ch_{uuid.uuid4().hex[:8]}",
                instruction=item.instruction,
                success_criteria=item.success_criteria,
                kind=item.kind,
            )
            for item in planned_challenges
        ]
        planned.append(
            ProductWork(
                id=product.id,
                name=product.name,
                reason=product.reason,
                price_cents=product.price_cents,
                sku=product.sku,
                challenges=challenges,
            )
        )
    planned[0].status = "in_progress"
    return Session(id=f"ses_{uuid.uuid4().hex[:12]}", products=planned)
