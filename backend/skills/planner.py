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

The point of each challenge is that a pre-made photo or deepfake is hard
to match because the action is specific and was not known in advance:
a named rotation, a brief finger occlusion, a camera move around one area.

Return a ChallengePlan with exactly 4 challenges, one of each kind:
1. pose — rotate or flip until a named feature faces the camera
2. interact — briefly cover or hold a named part with fingers (natural, not silly)
3. identify — show a serial, model, IMEI, or size label ONLY if that kind of
   product usually has one; otherwise show a distinctive seam, port, or logo
4. inspect — slowly move the camera around the claimed issue (or the most
   relevant part if the claim is vague)

Style (good):
- "Rotate the headphones clockwise until the logo faces us."
- "Cover the right earcup with two fingers."
- "Turn them over and show the serial number."
- "Move the camera slowly around the left hinge."

Style (also good, more specific to the claim):
- "Tilt the kettle until the crack near the handle is closest to the camera."
- "Rest two fingers on the spacebar so we can see it is the real keycap."
- "Circle the camera around the scuffed corner you mentioned."

Bad (do not do):
- Wave, dance, smile, say a passphrase, "look like a real person"
- Vague: "show the damage" with no location, "rotate it" with no stop condition
- Impossible: internal boards, microscopic views, tools they don't have
- Inventing a serial if this product class wouldn't have one
- Asking them to break, peel, or disassemble anything

Each instruction is one sentence. success_criteria must be visible in a
10-second phone take (e.g. "the logo faces the camera" / "two fingers
cover the right earcup" / "the left hinge fills the frame").
""".strip()


def planner_user_message(product: ProductIn) -> str:
    sku = product.sku or "unknown"
    return (
        f"Product name: {product.name}\n"
        f"SKU: {sku}\n"
        f"Customer refund claim: {product.reason}\n\n"
        "Propose 4 challenges (pose, interact, identify, inspect) for this item. "
        "Make the inspect challenge about the claimed issue. "
        "Name real parts of this product (earcup, hinge, logo, port, sole, etc.)."
    )


def fallback_plan(product: ProductIn) -> ChallengePlan:
    name = product.name
    reason = product.reason
    return ChallengePlan(
        challenges=[
            PlannedChallenge(
                kind="pose",
                instruction=f"Rotate the {name} clockwise until the front logo or brand mark faces us.",
                success_criteria="The front logo or distinctive front of the item faces the camera.",
            ),
            PlannedChallenge(
                kind="interact",
                instruction=f"Cover one end or corner of the {name} with two fingers for a moment.",
                success_criteria="Two fingers briefly occlude a named part of the real object.",
            ),
            PlannedChallenge(
                kind="identify",
                instruction=f"Turn the {name} over and hold any serial, model, or size label in focus.",
                success_criteria="A printed identifier or, if none, a distinctive back/underside is in focus.",
            ),
            PlannedChallenge(
                kind="inspect",
                instruction=f"Move the camera slowly around the area you described: {reason}",
                success_criteria=f"The camera moves around the claimed area ({reason}) at close range.",
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
