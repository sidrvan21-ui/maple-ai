import pytest
from fastapi import HTTPException

from app.hitl import put_in_review, reject_pack, sign_pack
from app.schemas.common import Decision, TeachingNote
from app.schemas.discovery import (
    Competitor,
    DiscoveryArtifacts,
    FourBigRisks,
    Jtbd,
    ProductConcept,
    ProjectCharter,
    Swot,
    TamSamSom,
)
from app.schemas.gate import GatePack
from app.state import initial_state


def _tiny_pack() -> GatePack:
    return GatePack(
        stage=1,
        decision=Decision(
            asked="Go to strategy?",
            recommendation="go",
            rationale="enough evidence",
        ),
        confidence=0.5,
        citations=[],
        required_approver_roles=["product"],
        artifacts=DiscoveryArtifacts(
            elevator_pitch="test",
            smart_goals=["g"],
            product_concept=ProductConcept(
                problem="p",
                who="w",
                job="j",
                why_now="n",
                kotler_level="core",
            ),
            project_charter=ProjectCharter(
                purpose="p",
                in_scope=["a"],
                out_scope=["b"],
                success="s",
            ),
            internal_assessment=["i"],
            external_assessment=["e"],
            swot=Swot(
                strengths=["s"],
                weaknesses=["w"],
                opportunities=["o"],
                threats=["t"],
            ),
            personas=[],
            jtbd=[
                Jtbd(
                    functional="f",
                    emotional="e",
                    social="s",
                    evidence="x",
                )
            ],
            voc_themes=[],
            tam_sam_som=TamSamSom(inputs=[], method="list inputs"),
            competitors=[Competitor(name="n", note="n")],
            four_big_risks=FourBigRisks(
                value="v",
                usability="u",
                feasibility="f",
                viability="vi",
            ),
            team_notes="t",
        ),
        teaching_note=TeachingNote(
            stage_name="Discovery",
            one_liner="o",
            pm_job="j",
            frameworks=["JTBD"],
            must_produce=["m"],
            common_failure=["c"],
            questions_to_ask=["q"],
            how_this_gate_works="h",
            next_stage_teaser="n",
        ),
    )


def test_sign_unlocks_stage_2():
    state = initial_state("p1")
    put_in_review(state, _tiny_pack())
    sign_pack(state, "product")
    assert state["hitl"] == "signed"
    assert 2 in state["admitted_stages"]


def test_finance_cannot_sign():
    state = initial_state("p1")
    put_in_review(state, _tiny_pack())
    with pytest.raises(HTTPException) as exc:
        sign_pack(state, "finance")
    assert exc.value.status_code == 403


def test_reject_does_not_unlock_s2():
    state = initial_state("p1")
    put_in_review(state, _tiny_pack())
    reject_pack(state, "product")
    assert state["hitl"] == "rejected"
    assert state["admitted_stages"] == [1]
