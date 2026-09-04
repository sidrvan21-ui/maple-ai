from fastapi import HTTPException, status

from app.ledgers import append_decision, merge_assumptions, merge_risks
from app.persist import save_state
from app.schemas.common import Role
from app.schemas.gate import GatePack
from app.state import MapleState


def put_in_review(state: MapleState, pack: GatePack) -> None:
    state["gate_packs"][pack.stage] = pack
    state["hitl"] = "in_review"
    state["required_approver_roles"] = list(pack.required_approver_roles)
    save_state(state)


def sign_pack(state: MapleState, role: Role) -> MapleState:
    if state["hitl"] != "in_review":
        raise HTTPException(status.HTTP_409_CONFLICT, "pack is not in review")
    if role not in state["required_approver_roles"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "role cannot sign this pack")
    pack = state["gate_packs"].get(state["current_stage"])
    if pack is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no pack to sign")
    append_decision(state, pack.stage, pack.decision)
    merge_assumptions(state, pack.assumptions)
    merge_risks(state, pack.risks)
    state["hitl"] = "signed"
    nxt = pack.stage + 1
    if nxt <= 9 and nxt not in state["admitted_stages"]:
        state["admitted_stages"] = sorted([*state["admitted_stages"], nxt])
    state["current_stage"] = nxt if nxt <= 9 else pack.stage
    save_state(state)
    return state


def reject_pack(state: MapleState, role: Role) -> MapleState:
    if state["hitl"] != "in_review":
        raise HTTPException(status.HTTP_409_CONFLICT, "pack is not in review")
    if role not in state["required_approver_roles"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "role cannot reject this pack")
    state["hitl"] = "rejected"
    save_state(state)
    return state
