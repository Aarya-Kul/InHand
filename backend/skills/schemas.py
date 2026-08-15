"""Structured objects the model must return. Field descriptions are part of the schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PlannedChallenge(BaseModel):
    kind: Literal["pose", "interact", "identify", "inspect"] = Field(
        description=(
            "pose = rotate/flip until a named side faces the camera. "
            "interact = briefly occlude or touch a named part with fingers. "
            "identify = show a real label/serial if the product has one. "
            "inspect = move the camera around the claimed defect or area."
        )
    )
    instruction: str = Field(
        description="One short sentence the customer hears. Specific and physical, not goofy."
    )
    success_criteria: str = Field(
        description="Observable, binary pass condition visible in the frames."
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
        description="True only if the success criteria are clearly visible. If unsure, false."
    )
    reason: str = Field(
        description="One short customer-facing sentence, derived only from observed/missing. Never accuse fraud."
    )
