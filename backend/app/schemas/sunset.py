from pydantic import BaseModel, Field


class EolTimeline(BaseModel):
    nsc: str
    eos: str
    eoe: str
    eom: str
    eol: str


class SunsetArtifacts(BaseModel):
    reasons_to_retire: list[str]
    eol_plan: str
    eol_checklist: list[str]
    timeline: EolTimeline
    internal_impacts: list[str]
    external_impacts: list[str]
    notice_90_day: str
    pipa_export: str
    what_survives: str
    notes: str = Field(default="")
