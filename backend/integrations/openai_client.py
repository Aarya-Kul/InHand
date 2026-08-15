"""
OpenAI integration — fill this in.

plan_challenges: given a product + refund reason, return viable live-camera challenges.
judge_recording: given the current challenge + the customer's recording, return pass/fail.
"""

from __future__ import annotations

from models.schemas import ProductIn


def plan_challenges(product: ProductIn) -> list[str]:
    """Return 2–4 short camera instructions for this product.

    TODO: Call OpenAI with product name, SKU, and reason. Keep instructions
    physical and specific (rotate, cover, show serial, show damaged area).
    """
    return [
        f"Hold the {product.name} up so the whole item is clearly in frame.",
        f"Slowly rotate the {product.name} until we can see every side.",
        f"Show the problem you described: {product.reason}",
    ]


def judge_recording(
    *,
    product_name: str,
    reason: str,
    instruction: str,
    video_bytes: bytes,
    content_type: str,
) -> tuple[bool, str]:
    """Return (passed, reason_for_ui).

    TODO: Sample 2–3 frames from video_bytes and send them + instruction to
    OpenAI vision. Return whether the customer satisfied THIS challenge.
    Do not decide session flow here — only pass/fail for the current challenge.
    """
    _ = (product_name, reason, instruction, video_bytes, content_type)
    return True, "placeholder judge: auto-pass (OpenAI not wired yet)"
