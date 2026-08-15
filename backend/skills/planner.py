"""Planner skill: product + refund reason → 4 candidate challenges, demo keeps 3."""

from __future__ import annotations

from config import MAX_CHALLENGES, MIN_CHALLENGES
from models.schemas import ProductIn
from skills.schemas import ChallengePlan, PlannedChallenge

PLANNER_SYSTEM = """
You are InHand's challenge planner.

Customers are returning a real product. Ask them to do a short, ordinary
inspection on camera — the kind a careful support agent would request —
not a goofy test and not "prove you aren't a fraudster."

A vision model will score ~8 stills from an 8-second phone take. Write
challenges that stills can actually confirm.

Two jobs, split across the 4 kinds:
- Prove it is the real item in their hands right now (pose, interact, identify).
- Confirm the refund claim they typed (inspect). Inspect MUST use their
  exact issue: stain → show the stain; crack → the crack; broken hinge →
  that hinge. Do not swap in a generic "damage" check.

Return a ChallengePlan with exactly 4 challenges, one of each kind:
1. pose — rotate or flip until a named LARGE side/feature faces the camera
2. interact — touch or point at a named part with one or two fingers.
   They MUST keep holding the item with their other fingers. That grip is
   expected. Do not ask them to isolate two fingers with nothing else
   touching the object.
3. identify — show a serial, model, IMEI, or size label ONLY if that kind of
   product usually has one; otherwise show a distinctive seam, port, or logo
4. inspect — hold the claimed defect close to the camera and slowly move
   around it. Name the defect in their words (stain, crack, scuff, tear).

Style (good):
- "Hold the phone case so the outside back fills the camera."
- "While holding the case, rest two fingers on the bottom edge."
- "Turn the case over so the inside faces us."
- "Hold the stained area close to the camera and move slowly around the stain."

Style (also good):
- "Tilt the kettle until the crack near the handle is closest to the camera."
- "While gripping the keyboard, rest two fingers on the spacebar."
- "Circle the camera around the scuffed corner you mentioned."

Bad (do not do):
- Wave, dance, smile, say a passphrase, "look like a real person"
- Vague: "show the damage" with no location, "rotate it" with no stop condition
- Inspect that ignores their claim (e.g. they said stained, you ask about a hinge)
- Interact that assumes no other fingers may touch the item
- Impossible: internal boards, microscopic views, tools they don't have
- Inventing a serial if this product class wouldn't have one
- Asking them to break, peel, or disassemble anything

Each instruction is one sentence. success_criteria must be visible in stills
(e.g. "the back of the case faces the camera" / "fingers touching the bottom
edge while the case is held" / "the stained area is close and in frame").
""".strip()


def planner_user_message(product: ProductIn) -> str:
    sku = product.sku or "unknown"
    return (
        f"Product name: {product.name}\n"
        f"SKU: {sku}\n"
        f"Customer refund claim (inspect MUST match this): {product.reason}\n\n"
        "Propose 4 challenges (pose, interact, identify, inspect) for this item. "
        "Inspect = confirm that specific claim (stain, crack, etc.), close-up. "
        "Pose/interact/identify = prove a real object is in their hand. "
        "For interact, they will also be gripping the item; that is fine. "
        "Name real parts of this product (back, camera cutout, corner, logo, port)."
    )


def fallback_plan(product: ProductIn) -> ChallengePlan:
    name = product.name
    reason = product.reason
    return ChallengePlan(
        challenges=[
            PlannedChallenge(
                kind="pose",
                instruction=f"Hold the {name} so its front or most recognizable side fills the camera.",
                success_criteria="The item is in frame and a distinct side faces the camera.",
            ),
            PlannedChallenge(
                kind="interact",
                instruction=(
                    f"While holding the {name} in place, rest two fingers on one edge or corner."
                ),
                success_criteria=(
                    "The item is being held, and fingers are touching an edge or corner. "
                    "Other gripping fingers are expected."
                ),
            ),
            PlannedChallenge(
                kind="identify",
                instruction=f"Turn the {name} over and hold the back or inside toward the camera.",
                success_criteria="The opposite side of the item (back or inside) faces the camera.",
            ),
            PlannedChallenge(
                kind="inspect",
                instruction=(
                    f"Hold the area you described close to the camera and move slowly around it: {reason}"
                ),
                success_criteria=(
                    f"The claimed area ({reason}) is close to the camera and visible in the stills."
                ),
            ),
        ]
    )


def cap_for_demo(challenges: list[PlannedChallenge]) -> list[PlannedChallenge]:
    """Keep pose + interact + inspect (or identify). Hard cap 3, never below 2."""
    by_kind: dict[str, PlannedChallenge] = {}
    for item in challenges:
        by_kind.setdefault(item.kind, item)

    picked: list[PlannedChallenge] = []
    for kind in ("pose", "interact"):
        if kind in by_kind:
            picked.append(by_kind.pop(kind))

    if "inspect" in by_kind:
        picked.append(by_kind.pop("inspect"))
    elif "identify" in by_kind:
        picked.append(by_kind.pop("identify"))

    for item in challenges:
        if len(picked) >= MAX_CHALLENGES:
            break
        if item not in picked:
            picked.append(item)

    if len(picked) < MIN_CHALLENGES:
        picked.extend(challenges[len(picked) : MIN_CHALLENGES])
    return picked[:MAX_CHALLENGES]
