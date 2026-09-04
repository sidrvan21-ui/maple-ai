from pydantic import BaseModel, Field


class Aarrr(BaseModel):
    acquire: str
    activate: str
    retain: str
    refer: str
    revenue: str


class Experiment(BaseModel):
    name: str
    result: str


class GrowthArtifacts(BaseModel):
    aarrr: Aarrr
    experiments: list[Experiment]
    cohorts: list[str]
    plg_verdict: str
    heart_or_north_star_score: str
    growth_risks: list[str] = Field(default_factory=list)
