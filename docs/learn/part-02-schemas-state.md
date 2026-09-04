# Part 2 — GatePack schemas + state

## Plain English

The **order slip**. Every later LLM call must fill a `GatePack`. If a TAM number has no citation and no assumption, Pydantic rejects it. No RAG, no OpenAI.

## Why it exists

The schema is the guardrail, not the prompt. HITL never sees an invalid pack.

## What we created

| Path | What it does |
|---|---|
| `backend/app/schemas/common.py` | Citation, Assumption, Risk, RACI, Decision, TeachingNote, **NumberedClaim** (must have `citation_id` or `assumption_id`) |
| `backend/app/schemas/discovery.py` … `sunset.py` | Nine Porter artifact models |
| `backend/app/schemas/gate.py` | `GatePack` envelope: decision + citations + teaching_note + artifacts |
| `backend/app/state.py` | `MapleState`: stage 1, admitted `[1]`, empty packs |
| `backend/app/ledgers.py` | Append decisions / assumptions / risks (used in Part 4) |
| `backend/tests/test_gatepack.py` | Valid pack passes; 248k TAM ungrounded fails; initial state admits s1 only |
| `backend/pytest.ini` | `pythonpath = .` |

## How we made it

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_gatepack.py -q
```

Result: **3 passed**.

`teaching_note` has no Porter door counts. Product numbers live in `artifacts` only.

## Interview script

**What is a GatePack?** One JSON envelope every stage returns.

**Why NumberedClaim?** A number without a source is a hallucination. Schema fails before HITL.

**Why list TAM inputs instead of one TAM?** Priya/Helen/Ravi/Samir disagree. Averaging is malpractice.

**What is teaching_note?** Generic PM lesson for the Learn pane.

**What is state?** `current_stage`, `admitted_stages=[1]`, `hitl`. Graph comes in Part 4.

## Gotchas

- Run pytest from `backend` so `app` imports.
- `NumberedClaim` is the rule for TAM/RICE/money. Plain strings can still lie — later evals catch that.
- Union artifacts: Pydantic picks the matching model from the JSON shape.

## How to demo

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_gatepack.py -q
```

Expect 3 passed. Open `discovery.py` and show `TamSamSom.inputs`.

## On to next

Part 3 — agentic RAG, admit `s1_discovery` only. You type unless you say otherwise.
