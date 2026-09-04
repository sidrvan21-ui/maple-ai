"""LangGraph timetable: nine rooms. Homework stays in run_stage."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.catalog import SPECS
from app.agents.runner import run_stage
from app.guardrails import block_if_in_review
from app.hitl import put_in_review
from app.session import get_state

ROOM_ORDER = [SPECS[n].name for n in range(1, 10)]


class GraphState(TypedDict):
    product_id: str


def pick_room(state: GraphState) -> str:
    """Which class today? Read the bag, not a second card."""
    maple = get_state(state["product_id"])
    return SPECS[maple["current_stage"]].name


def _room_node(stage: int):
    def node(state: GraphState) -> GraphState:
        maple = get_state(state["product_id"])
        pack = run_stage(stage, maple["admitted_stages"])
        put_in_review(maple, pack)
        return state

    node.__name__ = SPECS[stage].name
    return node


def build_graph():
    builder = StateGraph(GraphState)
    for number, spec in SPECS.items():
        builder.add_node(spec.name, _room_node(number))
    builder.add_conditional_edges(
        START,
        pick_room,
        {spec.name: spec.name for spec in SPECS.values()},
    )
    for spec in SPECS.values():
        builder.add_edge(spec.name, END)
    return builder.compile()


_APP = None


def get_graph():
    global _APP
    if _APP is None:
        _APP = build_graph()
    return _APP


def run_current_room(product_id: str) -> None:
    """One Run = one room. Sign does not start the next room."""
    block_if_in_review(get_state(product_id))
    get_graph().invoke({"product_id": product_id})


def _run_error_message(exc: Exception) -> str:
    text = str(exc)
    if "OPENAI_API_KEY" in text or "api_key" in text.lower() or "credentials" in text.lower():
        return (
            "OPENAI_API_KEY in the repo .env is empty. "
            "Paste a real OpenAI key on that line, save, and restart the server."
        )
    return text[:280]
