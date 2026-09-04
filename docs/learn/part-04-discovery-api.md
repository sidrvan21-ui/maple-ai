# Part 4 — Discovery node (living notes)

**Status:** Discovery node + HITL API on disk. HTML workbench is Part 5. Full `discovery/run` spends OpenAI (not required for unit tests).

Maple = PM copilot. Discovery = Stage 1 briefing + one human sign.

---

## What Discovery does in the app

Maple’s first homework: **what is this product about?**  
It reads Stage 1 notes and writes **one pack** (briefing + go/revise/no-go + citations + a generic lesson). The PM signs **once**. Sign unlocks Stage 2. Reject stays here.

Not two approvals. Not a chatbot. Not “show RAG then later LLM.”

---

## Who calls whom (memorize this)

Discovery **starts**. RAG does not send itself first.

```
Discovery gives MISSION to agentic RAG
        ↓
INSIDE RAG (Discovery is waiting):
   decompose (LLM)  →  breaks mission into questions
   for each question:
      retrieve (hybrid: vector + words)
      grade (LLM)
      if all no → rewrite (LLM) → retrieve + grade again
   cite  →  receipts
        ↓
RAG gives RECEIPTS back to Discovery
        ↓
Discovery gives receipts to a SECOND LLM job (fill briefing)
        ↓
that LLM gives a DRAFT back
        ↓
Discovery glues pack = receipts + draft + our hardcoded lesson
        ↓
route puts pack in_review → PM sign or reject
```

Decompose does **not** start after receipts. It is the first step **inside** RAG.

Two **jobs** (usually one model): (1) RAG: decompose / grade / rewrite / embeddings (2) Discovery: write the draft from receipts.

- **Mission** = we wrote it. Goes to RAG first.  
- **Raw data** = the team’s full notes on disk (`s1` today).  
- **Receipts** = small kept scraps from those notes (`c1`, file, quote). Not the whole dump. Not “PM cycle theory.” Not Maple’s stage progress.  
- **Draft** = LLM fills briefing + decision from receipts only.  
- **Lesson** = we wrote `DISCOVERY_LESSON` in code. Not LLM. Not `pm_knowledge`.  
- **Pack** = receipts + draft + lesson. PM signs **once**.

---

## Where the code lives

| Path | What |
|---|---|
| `backend/app/agents/__init__.py` | Empty. Marks the folder as a package. |
| `backend/app/agents/discovery.py` | Stage 1 brain: RAG → LLM → pack. |
| `backend/app/rag/pipeline.py` | Already built. Discovery only *calls* it. |
| `backend/app/schemas/discovery.py` | Shape of the briefing (already built Part 2). |
| `backend/app/schemas/gate.py` | Shape of the pack (already built). |

---

## Developer plan — how to remember this

Do **not** memorize every line. Memorize **jobs**, then one function name each.

**Say this in an interview (60 seconds)**

1. Stage 1 node calls agentic RAG with a Discovery mission.  
2. RAG returns citations from admitted files only.  
3. A second LLM fills Discovery artifacts from those citations. Do not average TAM.  
4. We attach a fixed teaching_note and return a GatePack.  
5. Product role signs once. That unlocks folder 2.

**What to drill (20 minutes)**

| Remember | Forget until you open the file |
|---|---|
| `gather_evidence` → `run_agentic_rag` | Prompt wording |
| `fill_briefing` → structured `DiscoveryDraft` | Every artifact field |
| `run_discovery` glues pack | RACI empty for now |
| Mission goes to RAG; receipts go to LLM | Import list |
| One sign on the pack | JWT details |

**How to study as a developer**

1. Draw the 6-arrow flow on paper (no code).  
2. Open `discovery.py` and only find those **three function names**.  
3. Open `pipeline.py` and say: “this is who gather_evidence calls.”  
4. Open `gate.py` and say: “this is what run_discovery returns.”  
5. Night before: read this note + Part 3 flow. Do not reread HybridStore.

---

## The discovery.py code in easy lines

### Part A — ask RAG

`from ... pipeline import run_agentic_rag`  
Use the Part 3 controller. Discovery does not search files itself.

`DISCOVERY_MISSION = "..."`  
The one goal we give RAG (jobs, market fights, competitors, privacy).

`def gather_evidence():`  
First step: get receipts.

`return run_agentic_rag(DISCOVERY_MISSION, admitted_stages=[1])`  
Search only textbook + s1. Come back with citations + trace.

### Part B — fixed lesson

`DISCOVERY_LESSON = TeachingNote(...)`  
Generic “what Discovery is.” No 248k. The LLM does not write this.

### Part C — ask LLM to write the briefing

`class DiscoveryDraft`  
The form: decision, artifacts, assumptions, risks, confidence.

`def fill_briefing(citations):`  
Second step. In: receipts. Out: briefing body.

`receipt_text = join c.id, path, span`  
Turn receipts into a readable list (`c1 | file | quote`).

`with_structured_output(DiscoveryDraft)`  
LLM must fill the form, not a chat paragraph.

Prompt: only use receipts; list both market numbers; every number needs `citation_id` or `assumption_id`.

### Part D — one pack

`def run_discovery() -> GatePack:`  
The one button.

`citations, trace = gather_evidence()`  
Call RAG.

`draft = fill_briefing(citations)`  
Call LLM.

`return GatePack(...)`  
Glue: stage 1, decision, citations from RAG, artifacts from LLM, lesson from Part B, trace from RAG, approver = product.

That pack is what the PM later signs.

---

## What we implemented

| Path | Job |
|---|---|
| `backend/app/agents/discovery.py` | `gather_evidence` → `fill_briefing` → `run_discovery` |
| `backend/app/session.py` | In-memory state per product id |
| `backend/app/hitl.py` | in_review, sign (unlock s2), reject (stay on 1) |
| `backend/app/routes_discovery.py` | API below |
| `backend/tests/test_hitl.py` | Sign unlocks 2; finance 403; reject no s2 |

**API** (login first, then Bearer token):

- `POST /api/products/{id}/discovery/run` — RAG + LLM + pack → `in_review`  
- `GET /api/products/{id}/state`  
- `GET /api/products/{id}/gate-pack`  
- `POST /api/products/{id}/hitl/sign` — product role only  
- `POST /api/products/{id}/hitl/reject`

**Still not Part 4:** website (Part 5). Live run of Discovery needs `OPENAI_API_KEY` and time/money.

---

## `routes_discovery.py` — what it is

Not the Discovery brain. **Doorbells (URLs).** Browser/curl hits a path; the path calls `run_discovery` / `sign_pack` / `get_state`.

`APIRouter(prefix="/api/products/{product_id}")` — all routes start like `/api/products/porter/...`.

`_public_state` — turn MapleState into JSON (pack keys as strings).

`Depends(principal_from_token)` — must be logged in. 401 if no JWT.

| Route | Does |
|---|---|
| POST `.../discovery/run` | `run_discovery()`, `put_in_review`, return state. Slow, costs OpenAI. `del principal` = we required login but do not use role yet. |
| GET `.../state` | Read memory only. |
| GET `.../gate-pack` | Stage 1 pack or 404. |
| POST `.../hitl/sign` | Uses `principal.role`. Product only. Unlock s2. |
| POST `.../hitl/reject` | Product only. Stay on `[1]`. |

---

## Interview framework (this is the right shape)

You do **not** need to recite every line. An AI engineer interview wants:

1. **Problem** — PM copilot, stage-gated, no hallucinated numbers.  
2. **Agentic RAG** — retrieve, grade, rewrite locally, cite. USP. Not naive top-k. Not “LLM invents if empty.”  
3. **Grounding** — schema (`NumberedClaim`) + citations. Guardrail in types, not only in the prompt.  
4. **HITL** — model drafts, human gates. Role-based. Sign unlocks the next folder.  
5. **Separation** — RAG finds receipts; stage node writes the pack; routes are just HTTP.

That **is** a solid AI-engineer story: retrieval + structured output + evaluation-ish grade + human-in-the-loop + product constraint (stage leak).

What you still add later (also interview gold): traces, evals, LangGraph checkpointer — Parts 5–8.

**60-second script**

*“Maple is a stage-gated PM copilot. Discovery calls agentic RAG on admitted files, then a second LLM fills a GatePack from citations only. A product role signs once; that admits the next folder. Routes are FastAPI over that. I remember the jobs, not every line.”*

---

## On to next

Part 5 — HTML workbench so a human can see the pack and click sign.
