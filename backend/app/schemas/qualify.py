from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import RaciRow


class LaunchReadiness(BaseModel):
    marketing: str
    sales_channel: str
    ops: str
    support: str
    docs: str
    pipa: str


class QualifyArtifacts(BaseModel):
    qualify_raci: list[RaciRow]
    beta_results: list[str]
    launch_readiness: LaunchReadiness
    launch_decision: Literal["go", "no-go", "scoped-go"]
    pricing_for_launch: str
    enablement_notes: str
    blockers: list[str] = Field(default_factory=list)
