from app.hitl import put_in_review, sign_pack
from app.session import forget_ram, get_state
from tests.test_hitl import _tiny_pack


def test_sign_survives_ram_wipe():
    state = get_state("keep")
    put_in_review(state, _tiny_pack())
    sign_pack(state, "product")
    forget_ram()
    again = get_state("keep")
    assert again["current_stage"] == 2
    assert again["admitted_stages"] == [1, 2]
    assert again["hitl"] == "signed"
    assert 1 in again["gate_packs"]
    assert again["gate_packs"][1].decision.recommendation == "go"


def test_new_product_starts_fresh():
    state = get_state("brand-new")
    assert state["admitted_stages"] == [1]
    assert state["gate_packs"] == {}
