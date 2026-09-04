from app.hitl import put_in_review
from app.schemas.common import MapleTake
from app.schemas.gate import GatePack
from app.session import forget_ram, get_state
from tests.test_hitl import _tiny_pack


def test_maple_take_survives_save():
    pack = _tiny_pack()
    pack.maple_take = MapleTake(
        stake="two TAM scraps disagree",
        judgment="do not average; make finance pick a method",
        challenges=["which doors count"],
        sign_commits="Strategy may read s2; we still owe a market method",
        next_for_the_team="pricing analogs need the same door count",
    )
    put_in_review(get_state("maple-take"), pack)
    forget_ram()
    again = get_state("maple-take").get("gate_packs", {}).get(1)
    assert again is not None
    assert again.maple_take is not None
    assert again.maple_take.judgment.startswith("do not average")


def test_old_pm_take_json_still_loads():
    pack = _tiny_pack()
    raw = pack.model_dump()
    raw.pop("maple_take", None)
    raw["pm_take"] = {
        "stake": "privacy",
        "judgment": "do not ship push without the DPA",
        "challenges": [],
        "sign_commits": "qualify stays blocked",
        "next_for_the_team": "legal thread",
    }
    loaded = GatePack.model_validate(raw)
    assert loaded.maple_take is not None
    assert "DPA" in loaded.maple_take.judgment
