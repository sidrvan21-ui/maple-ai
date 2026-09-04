import pytest
from pydantic import ValidationError

from app.schemas.common import (
    Assumption,
    Citation,
    Decision,
    TeachingNote,
)
from app.schemas.discovery import (
    DiscoveryArtifacts,
    FourBigRisks,
    ProductConcept,
    ProjectCharter,
    Swot,
    TamInput,
    TamSamSom,
)
from app.schemas.gate import GatePack
from app.schemas.common import NumberedClaim
from app.state import initial_state


def _teaching() -> TeachingNote:
    return TeachingNote(
        stage_name="Ideation & Discovery",
        one_liner="Learn who has the job and whether the market is real.",
        pm_job="Turn messy research into a concept and charter.",
        frameworks=["JTBD", "SWOT", "TAM/SAM/SOM"],
        must_produce=["concept", "charter", "SWOT"],
        common_failure=["average conflicting TAM into one fake number"],
        questions_to_ask=["Whose job is this?", "What evidence conflicts?"],
        how_this_gate_works="Approve means Strategy may use this charter.",
        next_stage_teaser="Strategy funds the bet; do not skip to a PRD.",
    )


def _artifacts(*, tam_grounded: bool) -> DiscoveryArtifacts:
    claim_kwargs = (
        {"citation_id": "c1"}
        if tam_grounded
        else {}
    )
    return DiscoveryArtifacts(
        elevator_pitch="Shutoff arrives before the tap coughs.",
        smart_goals=["Two Vancouver betas in 90 days"],
        product_concept=ProductConcept(
            problem="Residents miss building notices",
            who="Strata residents and council",
            job="Get the shutoff before morning",
            why_now="WhatsApp is muted",
            kotler_level="expected product",
        ),
        project_charter=ProjectCharter(
            purpose="Notice layer for Vancouver stratas",
            in_scope=["instant", "digests"],
            out_scope=["packages"],
            success="Publish under 60s; skip empty daily",
        ),
        internal_assessment=["Two-person eng"],
        external_assessment=["BuildingLink is the PM default"],
        swot=Swot(
            strengths=["Vancouver-first"],
            weaknesses=["No PM distribution"],
            opportunities=["Email PDF incumbent"],
            threats=["Notification fatigue"],
        ),
        personas=[],
        jtbd=[],
        voc_themes=[],
        tam_sam_som=TamSamSom(
            inputs=[
                TamInput(
                    source_label="Ravi scrap A",
                    what_it_counts="apartments Metro, method unclear",
                    claim=NumberedClaim(value=248000, unit="doors", **claim_kwargs),
                )
            ],
            method="list conflicts; do not average",
        ),
        competitors=[],
        four_big_risks=FourBigRisks(
            value="Missed shutoff is the job",
            usability="Daily vs owner off",
            feasibility="Push + dirty unit roll",
            viability="Helen $1200 vs per-door",
        ),
        team_notes="VoC file incomplete",
        pipa_flags=["no unit numbers in blasts"],
    )


def _pack(*, tam_grounded: bool) -> dict:
    return {
        "stage": 1,
        "decision": Decision(
            asked="Approve Discovery and enter Strategy",
            recommendation="go",
            rationale="Job is clear; TAM is not a single number",
        ),
        "confidence": 0.6,
        "citations": [
            Citation(
                id="c1",
                source_path="data/raw_inputs/s1_discovery/11_tam_scrap_stats_can_units.md",
                span="248,000 apartments",
                why_kept="founder's TAM scrap",
            )
        ],
        "assumptions": [
            Assumption(
                id="a1",
                claim="Beachhead is Vancouver 80-400 door stratas",
                kill_criterion="No council will publish in-app",
                owner="product",
            )
        ],
        "required_approver_roles": ["product"],
        "artifacts": _artifacts(tam_grounded=tam_grounded),
        "teaching_note": _teaching(),
    }


def test_valid_discovery_gatepack() -> None:
    pack = GatePack.model_validate(_pack(tam_grounded=True))
    assert pack.stage == 1
    assert pack.artifacts.tam_sam_som.inputs[0].claim.value == 248000


def test_tam_without_citation_or_assumption_fails() -> None:
    with pytest.raises(ValidationError, match="citation_id or assumption_id"):
        GatePack.model_validate(_pack(tam_grounded=False))


def test_initial_state_admits_stage_one_only() -> None:
    state = initial_state("porter")
    assert state["current_stage"] == 1
    assert state["admitted_stages"] == [1]
    assert state["gate_packs"] == {}
