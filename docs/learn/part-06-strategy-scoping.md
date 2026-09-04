# Part 6 — All nine rooms (living notes)

**Status:** built. One door, nine room cards. Live **Run** still spends OpenAI. Unit tests do not.

Maple = PM copilot. This part = Stages 2–9 use the same process as Discovery.

---

## Aim

Do not copy-paste eight Discovery files. Put nine **room cards** in one catalog. One runner walks the same path:

```
mission → agentic RAG (admitted folders only) → receipts
      → LLM fills THAT room’s artifacts
      → hardcoded lesson
      → GatePack
      → one human sign
      → next folder admitted
```

---

## What

| Stage | Name | Question |
|---|---|---|
| 1 | Discovery | What is the opportunity? |
| 2 | Strategy | Which game do we play? |
| 3 | Scoping | What ships in this cut? |
| 4 | Development | What is true in the build? |
| 5 | Qualify | Can we launch? |
| 6 | Launch | What happened in week one? |
| 7 | Growth | Is there a loop? |
| 8 | Maturity | Sustain or decline? |
| 9 | Sunset | How do we leave well? |

Workbench shows nine beige-brown room chips. Locked chips have no pack yet. **Run {room}** runs `current_stage` only. Pack tabs are still Decision / Briefing / Citations / Lesson / Risks — slices of one pack, not stages.

---

## Why

The product is the **door**. If only Stage 1 works, Maple is a demo. Admit must still hide `s9` from Stage 1, `s3` from Stage 2, and so on.

---

## Locked picture (say it this way)

Do not mix these four. This is the Q&A we locked.

| Thing | Holds | Does not hold |
|---|---|---|
| **Catalog** | 9 homework cards: mission, lesson, pack shape, writer rules | Raw notes. `pm_knowledge`. Receipts. |
| **Vector store** | Chunks of **all** `s1`–`s9` files + `pm_knowledge` | Receipts. Missions. The admit list. |
| **Admit filter** | Nothing. It is a bouncer. It **reads** `admitted_stages` | Per-stage memory. Knowledge. |
| **Pack** | Receipts (`c1`…) + briefing + lesson | The whole dump. |

**Who gives raw data?** We did, in Part 0. Files on disk. Not the LLM. A real company would drop their notes in the same folders.

**Who writes the card?** Human **Sign**. `admitted_stages` starts `[1]`. Sign Discovery → `[1, 2]`. Admit only maps those numbers to folders.

**Catalog → RAG:** only the **mission** goes in. The lesson stays off RAG and is glued on the pack after.

**RAG → vector store:** RAG asks for chunks. Store searches the whole house. Admit drops locked rooms. Survivors can become receipts.

**Stage 1 is allowed to use:** `s1_discovery` + `pm_knowledge`. The pile still has sunset. The bouncer throws it away.

Wrong sentences to avoid:

- “Catalog stores knowledge / Discovery for every stage.” → Catalog stores **homework**, not notes. Sheet 2 is Strategy, not Discovery again.  
- “Vector store keeps receipts.” → Vector store keeps **raw chunks**. Receipts live on the **pack**.  
- “Admit holds per-stage info.” → State holds the list. Admit only checks it.

---

## What we created

| Path | Job |
|---|---|
| `backend/app/agents/catalog.py` | Nine missions, lessons, artifact shapes, writer rules |
| `backend/app/agents/runner.py` | `run_stage(n, admitted)` — the door |
| `backend/app/agents/discovery.py` | Thin alias: `run_stage(1, [1])` |
| `backend/app/rag/vector_store.py` | Index **all** folders once; `filter_admitted` on retrieve |
| `backend/app/routes_discovery.py` | `POST /stages/{n}/run` + old `/discovery/run` |
| `backend/app/routes_pages.py` | Run current room; `?view=` to re-read an old pack |
| `backend/tests/test_stages.py` | Nine rooms, admit s2≠s3, filter drops s9, stage 2 blocked |

---

## How we made it

1. Catalog, not eight files — same process, different homework.  
2. Index all nine folders so Strategy can see `s2` after sign.  
3. Filter retrieve by `admitted_paths` so sunset cannot leak into Discovery.  
4. HITL unchanged: `sign_pack` already unlocks `stage + 1`.  
5. Product still signs every room. Finance still cannot.

---

## Do I memorize the code?

**No.** Memorize **jobs**. If someone opens a file, know what it is for. Do not recite lines.

Practice this sentence:

*“Nine rooms, one runner. We index the whole dump. Retrieve only keeps admitted folders. Sign unlocks the next folder.”*

If they say “show me,” open `runner.py` and `retrieve()` — two functions, not nine files.

---

## Walk the files (easy)

Read this the night before. Small parts. Job first, then what the lines mean.

### 1. `admit.py` — the doorman

Job: turn a list like `[1]` or `[1, 2]` into **real file paths**.

```
STAGE_FOLDERS = {1: "s1_discovery", 2: "s2_strategy", ... 9: "s9_sunset"}

def admitted_paths(admitted_stages):
    always add data/pm_knowledge/*.md
    for each number on the list:
        add that folder’s *.md
    skip raw_inputs/README.md
```

Easy: `[1]` = Discovery notes + tiny textbook cards. `[1, 2]` = those plus Strategy notes. Sunset is on disk. It is **not** in the list until `9` is on the card.

This is a **filter**, not a prompt. We do not tell the LLM “please ignore sunset.” We never hand it those files.

---

### 2. `vector_store.py` — big pile, then a lock

Job: two moments.

**Moment A — index (once)**

```
ALL_STAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9]

def get_store():
    if we have not built the pile yet:
        load ALL nine folders
        chunk them
        put them in FAISS + BM25
    return that pile
```

Easy: all books go on the library shelves so later rooms *can* be found. If we only shelved room 1, Strategy could never see `s2` even after you sign.

**Moment B — retrieve (every question)**

```
def retrieve(query, admitted_stages=[1]):
    search the big pile (ask for extra hits)
    filter_admitted(...)   # drop files not on the card
    return the first few that remain
```

```
def filter_admitted(docs, admitted_stages):
    allowed = paths from admitted_paths(...)
    keep a doc only if its source_path is in allowed
```

Easy: search might *touch* a sunset page. We **throw it away** before it becomes a receipt. The model never sees it.

Say: *“We index the house. We only hand over keys to open rooms.”*

---

### 3. `pipeline.py` — same RAG you already know

Job: mission → questions → retrieve / grade / rewrite → receipts.

The only new bit: it **forwards the card**.

```
def run_agentic_rag(mission, admitted_stages=None):
    stages = admitted_stages or [1]
    ...
    hits = retrieve(q, admitted_stages=stages)
```

Easy: RAG does not invent the lock. It just passes `admitted_stages` into `retrieve`. Default is `[1]` so old tests still mean Discovery-only.

---

### 4. `catalog.py` — nine homework sheets

Job: not nine apps. Nine **cards**.

```
class StageSpec:
    number          # 1..9
    name            # Discovery, Strategy, ...
    mission         # what we ask RAG
    lesson          # hardcoded teaching note (not LLM)
    artifacts_cls   # which pack shape to fill
    writer_rules    # extra “don’t average TAM”
```

`SPECS` is a dict: `1` → Discovery card, `2` → Strategy card, … `9` → Sunset card.

Easy: you already know Discovery. Strategy is the same object with different words. **Do not memorize the lesson paragraphs.**

`_lesson(...)` only fills the TeachingNote so we do not repeat “human signs one pack” nine times.

---

### 5. `runner.py` — the one door

Job: any room walks the same path.

```
def run_stage(stage, admitted_stages):
    if stage not in admitted_stages:
        stop (403)                    # room locked
    spec = that room’s card
    citations = run_agentic_rag(spec.mission, admitted_stages)
    draft = fill_briefing(spec, citations)   # LLM, receipts only
    return GatePack(..., teaching_note=spec.lesson)
```

Easy:

1. Not on the card? Door stays shut.  
2. Take that room’s homework.  
3. Same RAG. Same receipts.  
4. Second LLM writes **that** room’s briefing.  
5. We glue on **our** lesson (not the LLM).

`fill_briefing` still says: only use receipts; every number needs `c1` or an assumption.

---

### 6. `discovery.py` — nickname for room 1

```
def run_discovery():
    return run_stage(1, admitted_stages=[1])
```

Easy: old name still works. Discovery is not a second brain.

---

### 7. `hitl.py` — who adds the next key

Job: RAG does not unlock folders. The human does.

```
def sign_pack(state, role):
    must be in_review
    role must be allowed (product)
    hitl = signed
    next = this stage + 1
    add next to admitted_stages   # [1] → [1, 2]
    current_stage = next
```

Easy: Sign Discovery → card becomes `[1, 2]`. Next Run may read `s2`. Still not `s3`.

Reject: stay in this room. Card does not grow.

---

### 8. `session.py` — memory + which pack to show

```
get_state(product_id)     # one MapleState per product (porter)
reset_store()             # tests only

visible_pack(state, view):
    if they clicked an old chip (?view=2), show that pack
    else show pack for current room
    else show the pack they just signed (current - 1)
```

Easy: after Sign, you are in room 2 but you have not Run Strategy yet. We still show the Discovery pack until the next Run.

---

### 9. `routes_discovery.py` — JSON doors

| URL | Job |
|---|---|
| `POST .../discovery/run` | old door; still runs room 1 |
| `POST .../stages/{n}/run` | run room `n` only if `n` is `current_stage` |
| `GET .../state` | where we are + admitted list |
| `GET .../gate-pack` | the visible pack |
| `POST .../hitl/sign` | same `sign_pack` |
| `POST .../hitl/reject` | same `reject_pack` |

Easy: pages and JSON call the **same** runner and HITL. Two skins, one door.

---

### 10. `routes_pages.py` — the screen

Job: cookie login (already Part 5). New bits:

- Room chips from `SPECS` (locked / here / has a pack).  
- Button text = `Run {current room name}`.  
- **Run** calls `run_stage(current_stage, admitted_stages)` — not always Discovery.  
- `?view=3` re-reads an old pack.

Easy: the HTML does not invent a second gate. It presses the same door.

---

### Order to open files if someone asks

1. `catalog.py` — “nine cards”  
2. `runner.py` — “one walk”  
3. `vector_store.py` `get_store` + `retrieve` — “index all, filter out”  
4. `hitl.py` `sign_pack` — “Sign adds the next number”  

Skip: CSS, HTML, every schema field, lesson text.

---

## How to demo

1. Login as product. Nine chips; only Discovery admitted.  
2. **Run Discovery** (OpenAI) → Sign → chip 2 unlocks, button becomes **Run Strategy**.  
3. Repeat through Sunset. After each sign, the next folder is readable.  
4. Before a sign, `admitted_paths` for that room must not include the next folder.

Tests (no OpenAI):

```
.\.venv\Scripts\python.exe -m pytest tests\test_stages.py tests\test_rag_admit.py tests\test_pages_login.py tests\test_hitl.py -q
```

---

## Gotchas

- First `get_store()` embeds every file. Slow / costs tokens. Admit is not a smaller index.  
- `run_stage(2, [1])` is 403 — folder not admitted.  
- API `POST /stages/{n}/run` only accepts `n == current_stage`.  
- After sign, workbench still shows the last pack until you run the next room.  
- Briefing is pretty for all 9 rooms. Maple take is a later LLM memo, not the catalog lesson.  
- Parts 7–8 stage work is folded in. Save/export is Part 8 (built).

---

## On to next

Part 8 — **save / export** is built. SQLite remembers the bag. Notes: `part-08-growth-sunset.md`.
