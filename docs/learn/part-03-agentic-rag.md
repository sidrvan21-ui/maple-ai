# Part 3 — Agentic RAG

**Status: code is in. Live full pipeline not run yet (costs OpenAI).**  
Read this the night before an interview.

**Maple** = the PM copilot. **Porter** = sample research packet Maple reads. Not a concierge app.

**USP:** agentic RAG — retrieve → grade → rewrite → cite. Not naive top-k dump. Not “if empty, let the LLM invent.”

---

## Framework (how Part 3 fits Maple)

Nine product stages. Each stage may only read **admitted** research. A human unlocks the next folder (HITL, Part 4).

```
Part 0  raw notes on disk (9 folders)
Part 1  API + login
Part 2  GatePack shape (citations already defined)
Part 3  THIS — find evidence, decide keep/drop, return receipts
Part 4  next — stage node fills GatePack + human signs
```

Two engines:

| Engine | What | When |
|---|---|---|
| Part 3 | Agentic RAG (`pipeline.py`) | Now |
| App | 9 stage nodes + HITL | Part 4+ |

Admit is a **doorman**, not the engine.

---

## Whole RAG workflow (say it this way)

Discovery (or a test) **gives a mission** to agentic RAG. RAG **starts**. Discovery waits.

**Inside RAG, in order:**

1. **Decompose** — LLM breaks the mission into several questions. Does not read files. Does not see receipts (receipts do not exist yet).  
2. **For each question:**  
   - **Retrieve** — hybrid: vectors (embeddings) + words (BM25). Admit decides which files.  
   - **Grade** — LLM yes/no on each piece.  
   - **Rewrite** — only if all no. LLM new question. Retrieve + grade again (max 2).  
3. **Cite** — kept pieces become receipts (`c1`, file, quote).  
4. **Give receipts back** to Discovery.

Decompose is **first inside RAG**, not after receipts return.

LLM **calls** in RAG: decompose, embeddings, grade, rewrite. Same model, several jobs.

---

## Flow (easy)

Two piles:

- **Raw data** = files. We search these. They do not ask questions.
- **Mission** = the stage’s job, one sentence **we** pass in (later the Stage 1 node). Example: `"Run Discovery"` or `"What TAM numbers exist?"`

```
WE / stage node gives a mission
        ↓
decompose     LLM writes 4–8 search questions (does not read files)
        ↓
for each question:
        retrieve     hybrid search on admitted files only (~6 pieces)
        grade        each piece yes/no
        if all no    rewrite question → retrieve → grade (max 2)
        still empty  stop (Part 4: assumption). No web. No invented answer.
        ↓
citations     receipts (file + quote) + RagTrace
        ↓
STOP. No chat answer. No GatePack yet.
```

Stage 1 today: admit allows **16 files** = 3 textbook + 13 Discovery. Folders 2–9 stay closed. 9 = rooms. 16 = today’s papers.

---

## What each file does (code meaning)

| Path | Job |
|---|---|
| `backend/app/rag/admit.py` | `admitted_paths([1])` → allowed paths. Always `pm_knowledge`. Never `raw_inputs/README.md`. Never s2–s9 until unlocked. |
| `data/pm_knowledge/*.md` | Tiny method cards (jobs, don’t average TAM, SWOT frame). Always admitted. Not the course. |
| `vector_store.py` | Open those files → chunk (~1000 / overlap 150) → **hybrid** meaning (embeddings/FAISS) + keywords (BM25) → ~6 pieces. |
| `decompose.py` | Mission in → question list out. Does **not** open files. Fallback seed questions if LLM fails. |
| `self_correction.py` | `grade_documents` yes/no. `rewrite_query` = better **local** search string. Lazy LLM so tests don’t need a key at import. |
| `citations.py` | Kept chunks → Part 2 `Citation` (`c1`, path, span, why). `RagTrace` = questions, rewrite hops, dropped. |
| `pipeline.py` | `run_agentic_rag(mission)` = the run sheet. Returns `(citations, trace)`. |
| `tests/test_rag_admit.py` | Stage 1 has both TAM scraps; no s9; no spoiler README. **3 passed** with citation unit test. |

**Citations** = proof of where a fact came from (for GatePack / HITL).  
**Not** the PM lesson. Lesson = `teaching_note` in Part 4.  
**Not** `pm_knowledge` (that is search fuel for method).

**If grade keeps nothing:** rewrite + search again. Still nothing → empty for that question. LLM already used to grade/rewrite. LLM must **not** invent the TAM number.

---

## Vector store (one paragraph)

Chunking first. Then two searches: meaning (OpenAI embeddings, needs key) and same-words (BM25, no key). Hybrid merges, drops copies, returns ~6. That is **candidates**. Grade makes the list honest.

---

## Decompose (one paragraph)

Searcher takes **one** question. A stage job is bigger. We pass a mission. Decompose (LLM) **writes** several questions. Then each question hits retrieve/grade. It does not split files. Questions are not in the raw dump.

---

## How we made it

- Venv is `backend\.venv`. Install from `backend`.
- Root `.env` has `OPENAI_API_KEY`. `load_dotenv(repo_root() / ".env")`.
- No Tavily. No `generate_answer`.
- `pytest` from `backend`: admit + citation tests pass without calling the full pipeline.

```powershell
cd C:\Users\siddh\OneDrive\Desktop\maple.ai\backend
.\.venv\Scripts\python.exe -m pytest tests\test_rag_admit.py tests\test_rag_pipeline.py::test_to_citations_uses_source_path -q
.\.venv\Scripts\python.exe -m app.rag.pipeline
```

Second command spends OpenAI. Expect both `11_tam_scrap` and `12_tam_scrap`; never `s9_sunset`.

---

## Interview script

**What is agentic RAG here?** Retrieve, grade, rewrite locally, cite. The program decides. USP of Maple.

**Why not dump top-k?** Junk chunks and averaging fights. Grade drops junk. Two TAM scraps both stay.

**Why no web?** Would skip HITL and invent outside the dump.

**What does admit do?** File allow-list. Stage 1 = textbook + s1 only.

**Where do questions come from?** We (the stage) pass a mission. Decompose writes questions. Data does not ask.

**What do citations do?** Receipts for Part 4 `NumberedClaim` / HITL. Not teaching_note.

---

## Gotchas

- Save files before running (import reads disk).
- Lazy LLM: don’t construct ChatOpenAI at import.
- `get_store` builds FAISS once on **all nine folders** (cost). Admit is a **retrieve filter**, not a smaller index. If you only indexed stage 1, later rooms could never see their files.
- Tutorial rewrite was for Google. Ours is for local retrieve only.

---

## Parts left (whole Maple)

| Part | What | Status |
|---|---|---|
| 0 | Research dump | done |
| 1 | API scaffold | done |
| 2 | GatePack schemas | done |
| 3 | Agentic RAG | **done (code). Optional: run pipeline live** |
| 4 | Discovery node + fill GatePack + HITL sign-off | done |
| 5 | Sign-off website (FastAPI HTML) | done |
| 6 | All nine stage rooms (same door) | done |
| 7 | (folded into 6) | — |
| 8 | Export / persistence | later |

---

## On to next (Part 4)

Stage 1 **node** calls `run_agentic_rag` with a Discovery mission, fills a **GatePack** (decision, artifacts, teaching_note, our citations), waits for a **human** (product role) to sign. Sign → `admitted_stages` gains `2`. That is the app engine starting.
