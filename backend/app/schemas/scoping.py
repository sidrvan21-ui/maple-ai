from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import NumberedClaim


class Mrd(BaseModel):
    market_problem: str
    segments: list[str]
    needs: list[str]


class Prd(BaseModel):
    problem: str
    scope: str
    non_goals: list[str]
    requirements: list[str]
    success: str


class Moscow(BaseModel):
    must: list[str]
    should: list[str]
    could: list[str]
    wont: list[str]


class RiceInput(BaseModel):
    item: str
    reach: NumberedClaim
    impact: NumberedClaim
    confidence: NumberedClaim
    effort: NumberedClaim


class KanoItem(BaseModel):
    feature: str
    guess: Literal["must-be", "one-dimensional", "attractive", "indifferent", "reverse"]


class UserStory(BaseModel):
    story: str
    acceptance: str


class NowNextLater(BaseModel):
    now: list[str]
    next: list[str]
    later: list[str]


class ScopingArtifacts(BaseModel):
    mrd: Mrd
    prd: Prd
    moscow: Moscow
    rice_inputs: list[RiceInput]
    kano: list[KanoItem]
    user_stories: list[UserStory]
    ux_brief: str
    now_next_later: NowNextLater
    open_fights: list[str] = Field(default_factory=list)
