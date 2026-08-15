"""Pass/fail for the current challenge. Does not move the session cursor."""

from __future__ import annotations

from config import JUDGE_MODE
from integrations.openai_client import judge_recording
from models.session import ProductWork, Challenge


def judge(
    product: ProductWork,
    challenge: Challenge,
    video_bytes: bytes,
    content_type: str,
    demo_result: str | None = None,
    stills: list[bytes] | None = None,
) -> tuple[bool, str]:
    if demo_result in ("pass", "fail"):
        passed = demo_result == "pass"
        return passed, f"demo override: {demo_result}"

    if JUDGE_MODE == "always_pass":
        return True, "judge mode always_pass"
    if JUDGE_MODE == "always_fail":
        return False, "judge mode always_fail"

    return judge_recording(
        product_name=product.name,
        reason=product.reason,
        instruction=challenge.instruction,
        success_criteria=challenge.success_criteria,
        kind=challenge.kind,
        video_bytes=video_bytes,
        content_type=content_type,
        stills=stills or [],
    )
