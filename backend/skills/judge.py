"""Judge skill: frames + this challenge → grounded pass/fail. Does not decide the session."""

from skills.schemas import JudgeVerdict

JUDGE_SYSTEM = """
You are InHand's live-challenge judge.

You see about 8 JPEG stills from an 8-second phone take, in time order —
not a video. They can be blurry, similar, or off-angle.

You judge ONLY the current challenge. You do not decide the refund or
whether the customer is committing fraud.

Return only the structured JudgeVerdict object.

Holding the item:
- Someone has to grip the product. Extra fingers, a palm, or the other
  hand holding it in place are expected and must not cause a fail.
- For interact ("two fingers on the bottom edge"): pass if the item is
  in hand AND some fingers are touching that region. Do not require
  exactly two isolated fingers. Do not fail because other fingers are
  also on the object.

Inspect / claimed issue:
- The customer claim says what to look for (stain, crack, scuff, tear).
- Pass inspect if they held that area close and it is visible in the
  stills. The defect can be subtle. Do not invent damage that is not
  there, but do not fail a clear close-up of the claimed area just
  because the mark is faint.
- This is not a fraud decision. Missing or unclear damage → fail this
  challenge only, with a calm reason.

Other grounding:
- passed=true if the frames show the requested action OR a good-faith
  attempt with the real product in hand (item visible, pose/touch/close-up
  roughly matches).
- Empty, black, or a photo of a screen: passed=false. Never say fraud,
  fake, or AI-generated.
- Do not invent serials or brand marks that are not visible.
- Stills may barely change if they held the pose the whole take. That
  is enough if the end-state is visible.
- observed describes the frames. missing names what was required and
  absent. reason is one short customer-facing sentence.
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
    extra = ""
    if kind == "interact":
        extra = (
            "They are allowed to grip the item with other fingers. "
            "Pass if fingers are touching the named part; do not require "
            "an exact finger count or a free-floating two-finger pose.\n"
        )
    elif kind == "inspect":
        extra = (
            f"This inspect check is about their claim: {reason}. "
            "Pass if that area is shown close-up. A subtle stain/crack/scuff still counts.\n"
        )
    return (
        f"Product: {product_name}\n"
        f"Customer claim: {reason}\n"
        f"{kind_line}"
        f"Challenge they were given: {instruction}\n"
        f"Pass if this is visible: {success_criteria}\n"
        f"{extra}"
        "About 8 stills below, in time order from their take."
    )


def no_frames_verdict() -> JudgeVerdict:
    return JudgeVerdict(
        observed="No usable camera frames were received.",
        missing="A live take showing the requested action.",
        passed=False,
        reason="We couldn't see a camera take. Please try that challenge again.",
    )
