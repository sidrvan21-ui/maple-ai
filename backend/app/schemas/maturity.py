from typing import Literal

from pydantic import BaseModel, Field


class MaturityArtifacts(BaseModel):
    cost_per_building: str
    nps_qualitative: list[str]
    email_again_verdict: str
    tech_debt: list[str]
    support_load: str
    portfolio: list[str]
    sustain_vs_decline: Literal["sustain", "decline"]
    notes: str = Field(default="")
