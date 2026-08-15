"""Judge skill: frames + this challenge → grounded pass/fail. Does not decide the session."""

from skills.schemas import JudgeVerdict

JUDGE_SYSTEM = """
You are InHand's live-challenge judge.

You see still frames sampled from a customer's camera take, in time order.
You judge ONLY the current challenge. You do not decide the refund, the next
challenge, or whether the customer is committing fraud.

Return only the structured JudgeVerdict object.

Grounding rules:
- The customer's written claim is context, not evidence. Only the frames are evidence.
- passed=true only if the success criteria are clearly visible in the frames.
- If the frames are dark, blurry, off-screen, a photo of a photo, or you cannot tell: passed=false. Say you could not confirm. Do not say fraud, fake, or AI-generated.
- Do not invent damage, serial numbers, or brand marks that are not visible.
- If they showed the product but not the requested pose, fingers, or camera move, passed=false.
- For pose/interact/inspect: use the sequence of frames. A single still that never changes is not enough if the challenge asked for rotation, covering, or moving around.
- observed must describe the frames. missing must name what the criteria required that is absent.
- reason must be one short sentence a customer can understand, derived from observed/missing.
- Failed verification is inconclusive, not guilt.
""".strip()


def judge_user_message(
    *,
    product_name: str,
    reason: str,
    instruction: str,
    success_criteria: str,
    kind: str = "",
) -> str:
    kind_line = f"Challenge type: {kind}\n" if kind else ""
    return (
        f"Product: {product_name}\n"
        f"Customer claim (not evidence): {reason}\n"
        f"{kind_line}"
        f"Challenge they were given: {instruction}\n"
        f"Pass only if this is clearly visible: {success_criteria}\n\n"
        "Frames below are sampled in time order from their take."
    )


def no_frames_verdict() -> JudgeVerdict:
    return JudgeVerdict(
        observed="No usable camera frames were received.",
        missing="A live take showing the requested action.",
        passed=False,
        reason="We couldn't see a camera take. Please try that challenge again.",
    )
