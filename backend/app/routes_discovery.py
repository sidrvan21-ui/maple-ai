from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.discovery import run_discovery
from app.audit import log
from app.auth import Principal, principal_from_token
from app.graph import run_current_room
from app.guardrails import block_if_in_review
from app.hitl import put_in_review, reject_pack, sign_pack
from app.schemas.gate import GatePack
from app.session import get_state, visible_pack
from app.state import MapleState

router = APIRouter(prefix="/api/products/{product_id}", tags=["stages"])


def _public_state(state: MapleState) -> dict:
    packs = {
        str(k): v.model_dump() if hasattr(v, "model_dump") else v
        for k, v in state.get("gate_packs", {}).items()
    }
    return {
        "product_id": state["product_id"],
        "current_stage": state["current_stage"],
        "hitl": state["hitl"],
        "admitted_stages": state["admitted_stages"],
        "required_approver_roles": state["required_approver_roles"],
        "gate_packs": packs,
        "ledgers": state["ledgers"],
    }


@router.post("/discovery/run")
def discovery_run(
    product_id: str,
    principal: Principal = Depends(principal_from_token),
) -> dict:
    del principal
    state = get_state(product_id)
    block_if_in_review(state)
    pack = run_discovery()
    put_in_review(state, pack)
    return _public_state(state)


@router.post("/stages/{stage}/run")
def stage_run(
    product_id: str,
    stage: int,
    principal: Principal = Depends(principal_from_token),
) -> dict:
    del principal
    state = get_state(product_id)
    if stage != state["current_stage"]:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "run the current stage only",
        )
    run_current_room(product_id)
    return _public_state(get_state(product_id))


@router.get("/state")
def product_state(
    product_id: str,
    principal: Principal = Depends(principal_from_token),
) -> dict:
    del principal
    return _public_state(get_state(product_id))


@router.get("/gate-pack", response_model=GatePack)
def get_gate_pack(
    product_id: str,
    principal: Principal = Depends(principal_from_token),
    stage: int | None = None,
) -> GatePack:
    del principal
    pack = visible_pack(get_state(product_id), stage)
    if pack is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no pack yet")
    return pack


@router.get("/export")
def export_product(
    product_id: str,
    principal: Principal = Depends(principal_from_token),
) -> dict:
    """Same bag as SQLite. For a demo download."""
    del principal
    return _public_state(get_state(product_id))


@router.post("/hitl/sign")
def hitl_sign(
    product_id: str,
    principal: Principal = Depends(principal_from_token),
) -> dict:
    state = get_state(product_id)
    sign_pack(state, principal.role)
    log(principal, "sign", product_id, detail="api")
    return _public_state(state)


@router.post("/hitl/reject")
def hitl_reject(
    product_id: str,
    principal: Principal = Depends(principal_from_token),
) -> dict:
    state = get_state(product_id)
    reject_pack(state, principal.role)
    log(principal, "reject", product_id, detail="api")
    return _public_state(state)
