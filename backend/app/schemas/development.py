from pydantic import BaseModel, Field


class ChecklistItem(BaseModel):
    item: str
    done: bool


class BetaPlan(BaseModel):
    who: str
    questions: list[str]
    success: str
    rollback: str


class AgilePack(BaseModel):
    backlog: list[str]
    sprint_goal: str
    story_points_sum: int | None = None
    story_points_citation_id: str | None = None
    story_points_assumption_id: str | None = None
    burndown_note: str


class Defect(BaseModel):
    id: str
    severity: str
    note: str


class DevelopmentArtifacts(BaseModel):
    develop_checklist: list[ChecklistItem]
    requirements_changes: list[str]
    beta_plan: BetaPlan
    usability_findings: list[str]
    agile: AgilePack
    defects_open: list[Defect]
    launch_planning_early: list[str] = Field(default_factory=list)
