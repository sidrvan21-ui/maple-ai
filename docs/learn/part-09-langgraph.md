# Part 9 — LangGraph wrapper (living notes)

**Status:** built. Nine room nodes. Each node calls `run_stage`. Catalog / RAG / vector / admit are not extra nodes.

---

## What it is

A **timetable** of rooms. One Run = one room. Sign still unlocks the next folder. Sign does **not** auto-run the next room (that would spend OpenAI).

```
START → pick current room → Discovery | Strategy | … | Sunset → END
```

Inside the room: same as before (`run_stage` → catalog mission → RAG → pile → admit → pack).

---

## What we created

| Path | Job |
|---|---|
| `backend/app/graph.py` | 9 nodes + `pick_room` + `run_current_room` |
| `routes_pages` / `stages/{n}/run` | Call the graph, not `run_stage` directly |
| `backend/tests/test_graph.py` | Nine names; pick Strategy when current is 2; mock Run |

---

## Do I memorize the code?

No. Say: *“LangGraph is the timetable. `run_stage` is the class. RAG and admit are inside the class.”*

---

## How to demo

Same workbench. **Run Discovery** now goes through the Discovery node. Tests do not need OpenAI (`run_stage` is mocked).

---

## Gotchas

- Sequential “Discovery then Strategy” is `current_stage` after Sign, then `pick_room`. We do not chain nine LLM calls in one invoke.  
- `MemorySaver` is not used. Our SQLite bag still holds progress.  
- `/discovery/run` still calls `run_discovery()` directly (old door). The page uses the graph.

---

## On to next

Notes after this: [part-10-later.md](part-10-later.md) — rails, Maple take, SSO/audit, Docker.

---

## `graph.py` line by line (what each line *does*)

Do not memorize. Use this if you open the file.

### Lines 1–10 — imports (names become usable; nothing runs yet)

- **L1** Docstring. Not executed.  
- **L3** `from typing import TypedDict` — bring in Python’s typed-dict class.  
- **L5** `from langgraph.graph import END, START, StateGraph` — LangGraph: empty map class + start/stop constants.  
- **L7** `from app.agents.catalog import SPECS` — our dict of 9 cards (already built in `catalog.py`).  
- **L8** `from app.agents.runner import run_stage` — import the function `(stage, admitted) → GatePack`. Not called yet.  
- **L9** `from app.hitl import put_in_review` — import “put pack on desk + save SQLite.”  
- **L10** `from app.session import get_state` — import “give me MapleState for this product_id.”

### Lines 12–16 — list + graph state shape

- **L12** `ROOM_ORDER = [SPECS[n].name for n in range(1, 10)]` — at import time, build `["Discovery", …, "Sunset"]`. `range(1,10)` is 1..9.  
- **L15–16** `class GraphState(TypedDict): product_id: str` — rule only: graph state is a dict with key `product_id` (string). Not the full bag.

### Lines 19–22 — `pick_room` (runs at START of each invoke)

- **L19** Define function. LangGraph will call it. Returns a string (node name).  
- **L20** Docstring.  
- **L21** `maple = get_state(state["product_id"])` — e.g. get bag for `"porter"`.  
- **L22** `return SPECS[maple["current_stage"]].name` — if `current_stage` is 2, return `"Strategy"`. That string is the next node id.

### Lines 25–33 — `_room_node` (factory; makes one node function)

- **L25** Define maker. Argument `stage` is 1..9.  
- **L26** Inner `node` closes over that `stage` (Discovery’s node always uses 1).  
- **L27** Load bag again.  
- **L28** **Call** `run_stage(stage, maple["admitted_stages"])` — RAG + briefing. Result is `pack`.  
- **L29** **Call** `put_in_review(maple, pack)` — in_review + SQLite.  
- **L30** `return state` — give `{product_id}` back to LangGraph. Pack is not on GraphState.  
- **L32** Set `node.__name__` to the room name (debug).  
- **L33** Return the function object so `add_node` can store it.

### Lines 36–47 — `build_graph` (wires the map; compile once)

- **L36** Define builder function.  
- **L37** `builder = StateGraph(GraphState)` — construct empty graph.  
- **L38–39** Loop `SPECS.items()`; `add_node(spec.name, _room_node(number))` — nine boxes. This **is** all nine nodes.  
- **L40–44** `add_conditional_edges(START, pick_room, {name: name, ...})` — from START, call `pick_room`; jump to the returned name. Dict is the allowed menu. Does not call `pick_room` now.  
- **L45–46** `add_edge(spec.name, END)` — after that room, stop. No auto next room.  
- **L47** `return builder.compile()` — runnable graph with `.invoke()`.

### Lines 50–62 — cache + Run button

- **L50** `_APP = None` — no compiled graph yet.  
- **L53–57** `get_graph`: first call runs `build_graph()` and stores it; later calls reuse. `global _APP` writes the module variable.  
- **L60–62** `run_current_room(product_id)` — page **Run** calls this. `get_graph().invoke({"product_id": product_id})` starts one run: START → pick_room → one node → END.

Sign is **not** in this file. `sign_pack` in `hitl.py` changes `current_stage` / `admitted_stages` and saves. Next invoke uses the new number.
