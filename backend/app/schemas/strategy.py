from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import NumberedClaim


class StrategyOption(BaseModel):
    name: str
    note: str
    picked: bool = False


class Bmc(BaseModel):
    customer_segments: str
    value_propositions: str
    channels: str
    customer_relationships: str
    revenue_streams: str
    key_resources: str
    key_activities: str
    key_partners: str
    cost_structure: str


class PorterFiveForces(BaseModel):
    rivalry: str
    new_entrants: str
    substitutes: str
    buyer_power: str
    supplier_power: str


class Ansoff(BaseModel):
    today: str
    product_development: str
    market_development: str
    diversification: str


class Okr(BaseModel):
    objective: str
    key_results: list[str]


class Roadmap(BaseModel):
    now: list[str]
    next: list[str]
    later: list[str]


class BusinessCase(BaseModel):
    pricing_model: Literal["per_building", "per_door", "hybrid"]
    revenue_inputs: list[NumberedClaim]
    cost_inputs: list[NumberedClaim]


class StrategyArtifacts(BaseModel):
    vision: str
    value_proposition: str
    strategy_options: list[StrategyOption]
    bmc: Bmc
    porter_five_forces: PorterFiveForces
    ansoff: Ansoff
    okrs: list[Okr]
    north_star: str
    roadmap: Roadmap
    business_case: BusinessCase
    charter_updates: str
    preliminary_launch: str
    risk_register_delta: list[str] = Field(default_factory=list)
