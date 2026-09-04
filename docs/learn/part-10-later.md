# Part 10 — After the nine rooms (living notes)

**Status:** written so chat history is not the only copy. Keep this file if you tidy the repo.

---

## Plain English

Parts 0–9 built the cycle. After that we added: **rails** around the LLM, a **PM take** instead of a class card, **SSO + audit**, **Docker files**, and a **Cloudflare share link**. None of that changes the USP: cycle + agentic RAG.

---

## Why

Interview and a small team both need: “we did not invent a number,” “who signed,” and “how do I run this on another machine.”

---

## What we created

| Path | Job |
|---|---|
| `backend/app/guardrails.py` | No Run while `in_review`. No writer if RAG is empty. Receipt paths must be admitted. Draft ids must be real `c1` / assumptions. |
| `backend/app/agents/runner.py` `fill_pm_take` | Second LLM: stake, judgment, pushback, what Sign commits. Not JTBD textbook. |
| `GatePack.pm_take` | Stored on the pack. Old packs may be empty until you Re-run. |
| `backend/app/sso.py` | Google OAuth. Email → role. Optional `SSO_ALLOWED_DOMAIN`. |
| `audit_log` in SQLite | login / run / sign / reject / sso. Workbench **History** table. |
| `backend/Dockerfile` + `docker-compose.yml` | One box, uvicorn :8000, copies `data/`. Not started on this PC (no Docker Desktop). |
| Cloudflare quick tunnel | Public HTTPS → your laptop :8000. Code stays on your PC. |

Dev log in stays on until `ALLOW_DEV_LOGIN=false` **and** Google keys exist. Anyone with the share link can Dev log in today.

---

## How we made it

Order: empty OpenAI key → load `.env` → rails → PM take tab → SSO/audit → Docker files → `cloudflared tunnel --url http://127.0.0.1:8000`.

LangGraph **interrupt** was discussed and **not** built. HITL is still our bag. Sign does not auto-run the next room.

---

## Interview script

**Guardrails?** Admit in. Receipts before the writer. Ids after. No second Run in review. Not a middleware stack.

**Lesson tab?** Replaced by PM take. Catalog `lesson` still exists on the spec; the UI does not teach frameworks.

**SSO?** Google proves email. Same JWT cookie. Off until client id/secret. Dev form is the open door.

**Audit?** Who / action / when in SQLite. Not a legal-grade log.

**Docker vs tunnel?** Docker = box with the app. Tunnel = pipe to the app already running on your laptop.

**Can I hop back a room?** Read an old pack via the chip (`?view=`). Cannot unset Sign. Phase gate, not a chatbot.

---

## Gotchas

- First `get_store()` still embeds all nine folders.  
- `/discovery/run` still bypasses the graph (old API door). Page uses the graph.  
- Share URL dies if the laptop, uvicorn, or tunnel stops. New tunnel = new URL.  
- Do not commit `.env`.

---

## How to demo

1. Local: `backend` venv → uvicorn :8000 → login → Run → Citations → PM take → Sign.  
2. Share: keep uvicorn + cloudflared on; send the `trycloudflare.com` link to people you trust.  
3. Docker (if Desktop is installed): `docker compose up --build`.

---

## On to next

Night-before: [overview](overview-maple-workflow.md), part-03, part-06, part-09, this page. That is the whole process in easy language.
