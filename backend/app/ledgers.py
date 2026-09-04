"""Cross-gate lists. Part 4 will persist these after HITL."""

from app.schemas.common import Assumption, Decision, Risk
from app.state import LedgersState, MapleState


def append_decision(state: MapleState, stage: int, decision: Decision) -> None:
    state["ledgers"]["decisions"].append(
        {"stage": stage, **decision.model_dump()}
    )


def merge_assumptions(state: MapleState, rows: list[Assumption]) -> None:
    existing = {a["id"] for a in state["ledgers"]["assumptions"] if "id" in a}
    for row in rows:
        if row.id not in existing:
            state["ledgers"]["assumptions"].append(row.model_dump())


def merge_risks(state: MapleState, rows: list[Risk]) -> None:
    existing = {r["id"] for r in state["ledgers"]["risks"] if "id" in r}
    for row in rows:
        if row.id not in existing:
            state["ledgers"]["risks"].append(row.model_dump())


def empty_ledgers() -> LedgersState:
    return LedgersState(decisions=[], assumptions=[], risks=[])
