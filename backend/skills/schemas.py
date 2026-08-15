"""Structured objects the model must return. Field descriptions are part of the schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PlannedChallenge(BaseModel):
    kind: Literal["pose", "interact", "identify", "inspect"] = Field(
        description=(
            "pose = hold a named side toward the camera. "
            "interact = touch a named part with fingers while still gripping the item. "
            "identify = show a real label/serial if the product has one, else a large mark. "
            "inspect = close-up of the customer's claimed issue (stain, crack, etc.)."
        )
    )
    instruction: str = Field(
        description="One short sentence the customer hears. Specific and physical, not goofy."
    )
    success_criteria: str = Field(
        description=(
            "Observable pass condition in stills. For interact, gripping fingers "
            "are allowed. For inspect, name the claimed defect (stain, crack, etc.)."
        )
    )


class ChallengePlan(BaseModel):
    challenges: list[PlannedChallenge] = Field(
        min_length=3,
        max_length=4,
        description="Propose 4 (pose, interact, identify, inspect). The app will keep 3.",
    )


class JudgeVerdict(BaseModel):
    observed: str = Field(
        description="Only what is visible in the frames. No guesses. If dark, blurry, or empty, say that."
    )
    missing: str = Field(
        description="What the success criteria required that is not clearly visible. Empty string if nothing is missing."
    )
    passed: bool = Field(
        description=(
            "True if the product is in hand and the challenge is roughly visible. "
            "Do not fail interact because extra fingers are gripping the item. "
            "For inspect, true if the claimed area is shown close-up."
        )
    )
    reason: str = Field(
        description="One short customer-facing sentence, derived only from observed/missing. Never accuse fraud."
    )
