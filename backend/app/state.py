from typing import Literal, TypedDict

from app.schemas.common import Role
from app.schemas.gate import GatePack

HitlStatus = Literal["idle", "in_review", "signed", "rejected"]


class LedgersState(TypedDict):
    decisions: list[dict]
    assumptions: list[dict]
    risks: list[dict]


class MapleState(TypedDict, total=False):
    """LangGraph-shaped state. No graph runs in Part 2."""

    product_id: str
    current_stage: int
    hitl: HitlStatus
    admitted_stages: list[int]
    gate_packs: dict[int, GatePack]
    required_approver_roles: list[Role]
    ledgers: LedgersState


def initial_state(product_id: str) -> MapleState:
    return MapleState(
        product_id=product_id,
        current_stage=1,
        hitl="idle",
        admitted_stages=[1],
        gate_packs={},
        required_approver_roles=["product"],
        ledgers=LedgersState(decisions=[], assumptions=[], risks=[]),
    )
