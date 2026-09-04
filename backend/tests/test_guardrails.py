import pytest
from fastapi import HTTPException
from pydantic import BaseModel

from app.graph import run_current_room
from app.guardrails import (
    block_if_in_review,
    draft_ids_exist,
    receipts_are_admitted,
    require_receipts,
)
from app.hitl import put_in_review
from app.schemas.common import Assumption, Citation, NumberedClaim
from app.session import get_state
from tests.test_hitl import _tiny_pack


def _cite(cid: str = "c1", path: str = "data/pm_knowledge/jtbd.md") -> Citation:
    return Citation(id=cid, source_path=path, span="span", why_kept="test")


def test_in_review_blocks_second_run():
    state = get_state("guard-review")
    put_in_review(state, _tiny_pack())
    with pytest.raises(HTTPException) as exc:
        block_if_in_review(state)
    assert exc.value.status_code == 409


def test_run_current_room_blocked_while_in_review(monkeypatch):
    put_in_review(get_state("guard-graph"), _tiny_pack())

    def boom(*_args, **_kwargs):
        raise AssertionError("run_stage must not run")

    monkeypatch.setattr("app.graph.run_stage", boom)
    with pytest.raises(HTTPException) as exc:
        run_current_room("guard-graph")
    assert exc.value.status_code == 409


def test_empty_receipts_block_writer():
    with pytest.raises(HTTPException) as exc:
        require_receipts([])
    assert exc.value.status_code == 422


def test_sunset_path_rejected_on_discovery_admit():
    with pytest.raises(HTTPException) as exc:
        receipts_are_admitted(
            [_cite(path="data/raw_inputs/s9_sunset/01_deprecate_sms_noisy_sku.md")],
            [1],
        )
    assert exc.value.status_code == 422


def test_pm_knowledge_receipt_is_admitted():
    receipts_are_admitted([_cite()], [1])


def test_draft_rejects_unknown_citation():
    class Draft(BaseModel):
        claim: NumberedClaim
        assumptions: list[Assumption] = []

    draft = Draft(claim=NumberedClaim(value=1, citation_id="c99"))
    with pytest.raises(HTTPException) as exc:
        draft_ids_exist(draft, [_cite("c1")])
    assert exc.value.status_code == 422


def test_draft_accepts_receipt_and_own_assumption():
    class Draft(BaseModel):
        claim: NumberedClaim
        assumptions: list[Assumption]

    draft = Draft(
        claim=NumberedClaim(value=2, assumption_id="a1"),
        assumptions=[
            Assumption(id="a1", claim="x", kill_criterion="k", owner="product"),
        ],
    )
    draft_ids_exist(draft, [_cite("c1")])
