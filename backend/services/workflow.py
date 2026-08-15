"""Turn selected products + refund reasons into a challenge plan per product."""

from __future__ import annotations

import uuid

from integrations.openai_client import plan_challenges
from models.schemas import ProductIn
from models.session import Challenge, ProductWork, Session


def create_session(products: list[ProductIn]) -> Session:
    planned: list[ProductWork] = []
    for product in products:
        instructions = plan_challenges(product)
        if not instructions:
            instructions = [f"Show the {product.name} clearly in frame."]
        challenges = [
            Challenge(id=f"ch_{uuid.uuid4().hex[:8]}", instruction=text)
            for text in instructions
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
