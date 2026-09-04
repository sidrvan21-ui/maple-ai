from app.hitl import put_in_review
from app.schemas.common import PmTake
from app.session import forget_ram, get_state
from tests.test_hitl import _tiny_pack


def test_pm_take_survives_save():
    pack = _tiny_pack()
    pack.pm_take = PmTake(
        stake="two TAM scraps disagree",
        judgment="do not average; make finance pick a method",
        challenges=["which doors count"],
        sign_commits="Strategy may read s2; we still owe a market method",
        next_for_the_team="pricing analogs need the same door count",
    )
    put_in_review(get_state("pm-take"), pack)
    forget_ram()
    again = get_state("pm-take").get("gate_packs", {}).get(1)
    assert again is not None
    assert again.pm_take is not None
    assert again.pm_take.judgment.startswith("do not average")
