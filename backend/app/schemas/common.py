from typing import Literal

from pydantic import BaseModel, Field, model_validator

Role = Literal["product", "finance", "engineering", "exec", "growth", "legal"]
Recommendation = Literal["go", "revise", "no-go"]
Likelihood = Literal["low", "medium", "high"]


class Citation(BaseModel):
    id: str
    source_path: str
    span: str
    why_kept: str


class Assumption(BaseModel):
    id: str
    claim: str
    kill_criterion: str
    owner: str


class Risk(BaseModel):
    id: str
    statement: str
    likelihood: Likelihood
    impact: Likelihood
    mitigation: str
    residual: str


class RaciRow(BaseModel):
    activity: str
    responsible: str
    accountable: str
    consulted: str
    informed: str


class Decision(BaseModel):
    asked: str
    recommendation: Recommendation
    rationale: str
    alternatives: list[str] = Field(default_factory=list)


class TeachingNote(BaseModel):
    """Generic PM lesson. No product-specific numbers. Kept for old packs."""

    stage_name: str
    one_liner: str
    pm_job: str
    frameworks: list[str]
    must_produce: list[str]
    common_failure: list[str]
    questions_to_ask: list[str]
    how_this_gate_works: str
    next_stage_teaser: str


class MapleTake(BaseModel):
    """Maple's memo for the room. Not a human PM. Not a textbook."""

    stake: str
    judgment: str
    challenges: list[str] = Field(default_factory=list)
    sign_commits: str
    next_for_the_team: str


class NumberedClaim(BaseModel):
    """Any number in artifacts must be grounded."""

    value: float
    unit: str = ""
    citation_id: str | None = None
    assumption_id: str | None = None

    @model_validator(mode="after")
    def must_be_grounded(self) -> "NumberedClaim":
        if not self.citation_id and not self.assumption_id:
            raise ValueError(
                "numeric claim needs citation_id or assumption_id"
            )
        return self


class RagTrace(BaseModel):
    questions: list[str] = Field(default_factory=list)
    rewrite_hops: int = 0
    chunks_dropped: list[str] = Field(default_factory=list)
