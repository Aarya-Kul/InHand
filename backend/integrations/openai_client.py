"""OpenAI calls. Prompts and output shapes live in skills/. Teammate: add OPENAI_API_KEY."""

from __future__ import annotations

import base64

from config import OPENAI_API_KEY, OPENAI_MODEL
from integrations.frames import extract_jpeg_frames
from models.schemas import ProductIn
from skills.judge import JUDGE_SYSTEM, judge_user_message, no_frames_verdict
from skills.planner import PLANNER_SYSTEM, cap_for_demo, fallback_plan, planner_user_message
from skills.schemas import ChallengePlan, JudgeVerdict, PlannedChallenge


def _has_key() -> bool:
    return bool(OPENAI_API_KEY and OPENAI_API_KEY.strip())


def _client():
    from openai import OpenAI

    return OpenAI(api_key=OPENAI_API_KEY)


def plan_challenges(product: ProductIn) -> list[PlannedChallenge]:
    if not _has_key():
        return cap_for_demo(fallback_plan(product).challenges)
    try:
        completion = _client().chat.completions.parse(
            model=OPENAI_MODEL,
            temperature=0.7,
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM},
                {"role": "user", "content": planner_user_message(product)},
            ],
            response_format=ChallengePlan,
        )
        plan = completion.choices[0].message.parsed
        if plan is None or not plan.challenges:
            return cap_for_demo(fallback_plan(product).challenges)
        return cap_for_demo(plan.challenges)
    except Exception:
        return cap_for_demo(fallback_plan(product).challenges)


def judge_recording(
    *,
    product_name: str,
    reason: str,
    instruction: str,
    video_bytes: bytes,
    content_type: str,
    success_criteria: str = "",
    kind: str = "",
) -> tuple[bool, str]:
    if not _has_key():
        return True, "placeholder judge: auto-pass (OPENAI_API_KEY not set)"

    criteria = success_criteria or instruction
    frames = extract_jpeg_frames(video_bytes, content_type)
    if not frames:
        verdict = no_frames_verdict()
        return verdict.passed, verdict.reason

    content: list[dict] = [
        {
            "type": "text",
            "text": judge_user_message(
                product_name=product_name,
                reason=reason,
                instruction=instruction,
                success_criteria=criteria,
                kind=kind,
            ),
        }
    ]
    for jpeg in frames:
        b64 = base64.standard_b64encode(jpeg).decode("ascii")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )

    try:
        completion = _client().chat.completions.parse(
            model=OPENAI_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": content},
            ],
            response_format=JudgeVerdict,
        )
        verdict = completion.choices[0].message.parsed
        if verdict is None:
            return False, "We couldn't score this take. Please try again."
        return _ground(verdict)
    except Exception:
        return False, "Verification is temporarily unavailable. Please try that challenge again."


def _ground(verdict: JudgeVerdict) -> tuple[bool, str]:
    """Refuse a pass that isn't backed by an observation."""
    observed = (verdict.observed or "").strip()
    reason = (verdict.reason or "").strip() or "We couldn't confirm that challenge from this take."
    if verdict.passed and len(observed) < 8:
        return False, "We couldn't confirm that challenge from this take."
    return verdict.passed, reason[:180]
