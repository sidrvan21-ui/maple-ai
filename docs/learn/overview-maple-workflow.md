# Maple AI — overall workflow

**Maple** = the PM copilot we coded.  
**Porter** = sample research notes Maple reads. Not a product we ship.

Read this first. Then open part notes if you need one piece.

---

## What Maple does in one sentence

A human walks nine product rooms. Each room: find evidence → write a pack → human Signs → next folder unlocks. Restart does not wipe that.

---

## The cycle (repeats for every stage)

```
1. Log in (cookie JWT). Dev: pick a role. Google SSO if keys are set.
2. Click Run (blocked if a pack is already in_review)
3. LangGraph picks the current room (Discovery, then Strategy, …)
4. That room calls run_stage
      catalog  → mission + pack shape
      RAG      → decompose → retrieve → grade → rewrite → receipts
      retrieve → search the vector pile (all s1–s9 + pm_knowledge)
      admit    → drop chunks from locked folders
      rails    → no receipts → no writer; citation ids must exist
      LLM      → briefing from receipts only
      LLM      → Maple take (Maple's memo, not a textbook lesson)
5. Pack sits in_review (SQLite saves the bag). Audit logs Run.
6. Human Sign  → admitted_stages grows, current_stage + 1, audit row
   or Reject   → stay in this room, audit row
7. Click Run again → step 3 uses the new room number
8. Repeat until Sunset
```

Sign does **not** run the next room. The next **Run** does.

---

## Who holds what

| Piece | Holds | Does not hold |
|---|---|---|
| Disk `data/raw_inputs/` + `pm_knowledge/` | Raw notes we wrote (Part 0) | Packs, missions |
| Vector store | Chunks of those files (all 9 folders + knowledge) | Receipts, the admit list |
| Admit | Nothing. Reads `admitted_stages` and filters chunks | Memory of its own |
| Catalog `SPECS` | 9 cards: mission, class lesson (unused on the tab), shape, writer rules | Raw notes |
| RAG pipeline | Makes receipts from allowed chunks | GatePack |
| `guardrails.py` | in_review block, receipts, admitted paths, real ids | HTTP middleware |
| `run_stage` | One room’s walk + Maple take | The timetable |
| LangGraph `graph.py` | 9 room boxes + pick_room | RAG / catalog / admit copies |
| `MapleState` bag | Room number, open folders, packs, HITL | The raw dump |
| SQLite `data/maple.db` | Bag + `audit_log` | Fieldwork files |
| Workbench | Run/Sign, tabs, History table | A second gate |

---

## One Run, in order of code

```
Browser POST /p/porter/run
  → routes_pages.page_run
  → graph.run_current_room("porter")
  → get_graph().invoke({product_id: "porter"})
  → START → pick_room → e.g. "Discovery"
  → Discovery node
       get_state("porter")
       run_stage(1, [1])
       put_in_review  (also save_state → SQLite)
  → END
  → page reloads, you see the pack
```

After Sign (`hitl.sign_pack`): bag is room 2, card `[1, 2]`. Next invoke → `pick_room` returns `"Strategy"` → `run_stage(2, [1, 2])`.

---

## Interview (60 seconds)

1. Nine rooms, one runner.  
2. Agentic RAG only; admit is a file filter, not a prompt.  
3. Index the whole dump; retrieve drops locked folders.  
4. One human sign per pack; Sign unlocks the next folder.  
5. LangGraph is the timetable; homework is `run_stage`.  
6. SQLite stores the bag so restart does not fake-reset the gate.  
7. Rails: no second Run in review; empty RAG does not write.  
8. Maple take is Maple's memo, not a human PM. Audit is who/what/when.

---

## Part files

| File | What |
|---|---|
| [part-00](part-00-research-dump.md) | Porter notes on disk |
| [part-01](part-01-scaffold.md) | FastAPI + login API |
| [part-02](part-02-schemas-state.md) | GatePack + state |
| [part-03](part-03-agentic-rag.md) | RAG loop |
| [part-04](part-04-discovery-api.md) | Stage 1 + HITL |
| [part-05](part-05-workbench.md) | HTML gate |
| [part-06](part-06-strategy-scoping.md) | All nine rooms + locked picture |
| [part-08](part-08-growth-sunset.md) | SQLite bag |
| [part-09](part-09-langgraph.md) | Graph + **line-by-line `graph.py`** |
| [part-10](part-10-later.md) | Guardrails, Maple take, SSO/audit, Docker, share link |
