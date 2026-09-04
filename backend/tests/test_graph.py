from app.agents.catalog import SPECS
from app.graph import ROOM_ORDER, build_graph, pick_room, run_current_room
from app.session import get_state
from tests.test_hitl import _tiny_pack


def test_graph_has_nine_named_rooms():
    app = build_graph()
    for name in ROOM_ORDER:
        assert name in app.nodes
    assert ROOM_ORDER == [SPECS[n].name for n in range(1, 10)]


def test_pick_room_follows_current_stage():
    state = get_state("graph-pick")
    assert pick_room({"product_id": "graph-pick"}) == "Discovery"
    state["current_stage"] = 2
    assert pick_room({"product_id": "graph-pick"}) == "Strategy"


def test_run_current_room_calls_run_stage_once(monkeypatch):
    calls: list[tuple[int, list[int]]] = []

    def fake_run(stage, admitted_stages):
        calls.append((stage, list(admitted_stages)))
        return _tiny_pack()

    monkeypatch.setattr("app.graph.run_stage", fake_run)
    run_current_room("graph-run")
    assert calls == [(1, [1])]
    maple = get_state("graph-run")
    assert maple["hitl"] == "in_review"
