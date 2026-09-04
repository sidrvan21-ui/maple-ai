from fastapi.testclient import TestClient

from app.hitl import put_in_review
from app.main import app
from app.schemas.common import Decision, TeachingNote
from app.schemas.gate import GatePack
from app.schemas.strategy import (
    Ansoff,
    Bmc,
    BusinessCase,
    Okr,
    PorterFiveForces,
    Roadmap,
    StrategyArtifacts,
    StrategyOption,
)
from app.session import get_state
from tests.test_pages_login import _login


def _strategy_pack() -> GatePack:
    return GatePack(
        stage=2,
        decision=Decision(asked="Play here?", recommendation="go", rationale="yes"),
        confidence=0.4,
        citations=[],
        required_approver_roles=["product"],
        artifacts=StrategyArtifacts(
            vision="Stay in Vancouver first",
            value_proposition="alerts that are not email",
            strategy_options=[StrategyOption(name="focus", note="one city", picked=True)],
            bmc=Bmc(
                customer_segments="strata",
                value_propositions="notice",
                channels="app",
                customer_relationships="pm",
                revenue_streams="per door",
                key_resources="push",
                key_activities="digest",
                key_partners="ios",
                cost_structure="sms",
            ),
            porter_five_forces=PorterFiveForces(
                rivalry="email",
                new_entrants="low",
                substitutes="facebook",
                buyer_power="high",
                supplier_power="apple",
            ),
            ansoff=Ansoff(
                today="van",
                product_development="digest",
                market_development="burnaby",
                diversification="no",
            ),
            okrs=[Okr(objective="trust", key_results=["open rate"])],
            north_star="alerts read",
            roadmap=Roadmap(now=["push"], next=["digest"], later=["sms off"]),
            business_case=BusinessCase(
                pricing_model="per_door",
                revenue_inputs=[],
                cost_inputs=[],
            ),
            charter_updates="narrow who",
            preliminary_launch="one building",
        ),
        teaching_note=TeachingNote(
            stage_name="Strategy",
            one_liner="o",
            pm_job="j",
            frameworks=["BMC"],
            must_produce=["m"],
            common_failure=["c"],
            questions_to_ask=["q"],
            how_this_gate_works="h",
            next_stage_teaser="n",
        ),
    )


def test_strategy_briefing_is_readable_not_json_wall():
    from app.session import reset_store

    reset_store()
    client = TestClient(app)
    _login(client)
    put_in_review(get_state("brief"), _strategy_pack())
    page = client.get("/p/brief?view=2")
    assert page.status_code == 200
    assert "Stay in Vancouver first" in page.text
    assert "Vision." in page.text
    assert "Maple take" in page.text
    assert "Lesson" in page.text
    assert "Pick the game before you write the backlog." in page.text
    assert "Ask around the table" in page.text
    assert "Where do we play?" in page.text
    assert "PM take" not in page.text
    assert '"vision":' not in page.text
