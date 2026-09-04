from pydantic import BaseModel, Field

from app.schemas.common import NumberedClaim


class ProductConcept(BaseModel):
    problem: str
    who: str
    job: str
    why_now: str
    kotler_level: str


class ProjectCharter(BaseModel):
    purpose: str
    in_scope: list[str]
    out_scope: list[str]
    success: str


class Swot(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]


class Persona(BaseModel):
    name: str
    role: str
    note: str
    citation_id: str | None = None


class Jtbd(BaseModel):
    functional: str
    emotional: str
    social: str
    evidence: str
    citation_id: str | None = None


class VocTheme(BaseModel):
    theme: str
    evidence: str
    citation_id: str | None = None


class TamInput(BaseModel):
    source_label: str
    what_it_counts: str
    claim: NumberedClaim


class TamSamSom(BaseModel):
    """Conflicting inputs stay as a list. Do not average."""

    inputs: list[TamInput]
    method: str
    tam: NumberedClaim | None = None
    sam: NumberedClaim | None = None
    som: NumberedClaim | None = None


class Competitor(BaseModel):
    name: str
    note: str
    citation_id: str | None = None


class FourBigRisks(BaseModel):
    value: str
    usability: str
    feasibility: str
    viability: str


class DiscoveryArtifacts(BaseModel):
    elevator_pitch: str
    smart_goals: list[str]
    product_concept: ProductConcept
    project_charter: ProjectCharter
    internal_assessment: list[str]
    external_assessment: list[str]
    swot: Swot
    personas: list[Persona]
    jtbd: list[Jtbd]
    voc_themes: list[VocTheme]
    tam_sam_som: TamSamSom
    competitors: list[Competitor]
    four_big_risks: FourBigRisks
    team_notes: str
    pipa_flags: list[str] = Field(default_factory=list)
