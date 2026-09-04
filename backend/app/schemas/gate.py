from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import (
    Assumption,
    Citation,
    Decision,
    PmTake,
    RaciRow,
    RagTrace,
    Role,
    TeachingNote,
    Risk,
)
from app.schemas.development import DevelopmentArtifacts
from app.schemas.discovery import DiscoveryArtifacts
from app.schemas.growth import GrowthArtifacts
from app.schemas.launch import LaunchArtifacts
from app.schemas.maturity import MaturityArtifacts
from app.schemas.qualify import QualifyArtifacts
from app.schemas.scoping import ScopingArtifacts
from app.schemas.strategy import StrategyArtifacts
from app.schemas.sunset import SunsetArtifacts


class ComputedBlock(BaseModel):
    rice_scores: dict[str, float] = Field(default_factory=dict)
    ltv: float | None = None
    cac: float | None = None
    roi: float | None = None
    notes: str = ""


class GatePack(BaseModel):
    stage: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9]
    decision: Decision
    confidence: float = Field(ge=0, le=1)
    open_questions: list[str] = Field(default_factory=list)
    citations: list[Citation]
    assumptions: list[Assumption] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    raci: list[RaciRow] = Field(default_factory=list)
    required_approver_roles: list[Role]
    artifacts: (
        DiscoveryArtifacts
        | StrategyArtifacts
        | ScopingArtifacts
        | DevelopmentArtifacts
        | QualifyArtifacts
        | LaunchArtifacts
        | GrowthArtifacts
        | MaturityArtifacts
        | SunsetArtifacts
    )
    teaching_note: TeachingNote
    pm_take: PmTake | None = None
    computed: ComputedBlock | None = None
    rag_trace: RagTrace = Field(default_factory=RagTrace)
