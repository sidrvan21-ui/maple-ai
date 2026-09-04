# Part 5 — Workbench (living notes)

**Status:** HTML login + workbench on the same FastAPI process. Palette is beige-green page + beige-brown tabs. Run Discovery still spends OpenAI. Sign/reject page tests do not.

Maple = PM copilot. Workbench = the human screen for the Part 4 gate.

---

## What this part is

A PM opens `http://127.0.0.1:8000`, logs in as a role, runs Discovery, **reads the pack**, then Sign or Reject.

Same functions as the JSON API. New skin only. No new RAG. No Stage 2 node.

---

## Why it exists

Part 4 is the box. Part 5 is the display.

Interview people will not watch curl. HITL only counts if a person can click it.

Cookie holds the same JWT the API already issued. Browser sends it. We do not paste Bearer tokens.

---

## What we created

| Path | Job |
|---|---|
| `backend/app/auth.py` | `decode_token` + `principal_from_cookie` (`maple_token`) |
| `backend/app/templates/login.html` | Name + role form. Uses shared CSS. |
| `backend/app/templates/workbench.html` | Nine room chips + **Run {current room}** + pack tabs. Briefing is readable for **all 9** room shapes (not only Discovery JSON). |
| `backend/app/static/maple.css` | Shared look: beige-green page, beige-brown tabs, forest buttons |
| `backend/app/routes_pages.py` | HTML doors. Calls `run_discovery`, `sign_pack`, `reject_pack` |
| `backend/app/session.py` | In-memory product state + `reset_store` for tests |
| `backend/tests/test_pages_login.py` | Login cookie, lockout, sign unlocks 2, reject stays `[1]`, finance blocked, tabs after sign |

`main.py` mounts `pages_router` **before** the API router, then `/static`.

`main.py` mounts `pages_router` **before** the API router.

---

## Who calls whom

```
Browser GET /          → no cookie → /login
Browser POST /login    → JWT cookie → /p/porter
Browser POST /p/porter/run   → run_discovery() → put_in_review
Browser POST /p/porter/sign  → sign_pack(role) → folder 2 if product
Browser POST /p/porter/reject → reject_pack(role) → stay [1]
```

Page routes do **not** invent a second HITL. They call the same `hitl.py` as `/api/products/...`.

`{product_id}` = which product (`porter`). Not stage 1–9.

---

## How login works (easy)

1. Form posts name + role.  
2. `issue_token` makes the same JWT as `POST /api/auth/dev-login`.  
3. Server sets cookie `maple_token` (`httponly`, `samesite=lax`).  
4. Later HTML routes read `principal_from_cookie`. Missing/bad cookie → back to login.

JSON API still uses `Authorization: Bearer`. Two doors, one token shape.

---

## Look (easy)

Page paint is **beige-green** (`--bg: #dce6d0`). Tabs are **beige-brown** (`--tab: #d2b48c`), darker when selected. One CSS file so login and workbench match.

Tabs are **not** new stages. They only flip which part of the **same pack** you read. Sign is still once, on the whole pack.

---

## Interview line (30 seconds)

*“Part 4 is the API. Part 5 is the same HITL as HTML on FastAPI. Login puts the JWT in a cookie. Run / Sign / Reject call the same functions. Product unlocks folder 2. Finance cannot sign.”*

---

## How to demo

From `backend` (venv on):

```
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

1. Open `http://127.0.0.1:8000` → login.  
2. Role `product`, name `Siddharth` → workbench.  
3. **Run Discovery** (slow, OpenAI). Read briefing + citations + Maple take.  
4. **Sign** → Admitted shows `[1, 2]`.  
5. Log out. Log in as `finance`. Sign should fail (“role cannot sign”).  
6. Or reject instead of sign → still `[1]`.

Page tests (no OpenAI):

```
.\.venv\Scripts\python.exe -m pytest tests\test_pages_login.py -q
```

---

## Gotchas

- Shared `TestClient` keeps cookies. Each test must make its own client or the “no cookie” case looks logged in.  
- `_STORE` is process memory. Restart the server, packs vanish. Tests call `reset_store()`.  
- Run Discovery is the live RAG + draft path. Do not click it just to check login.  
- Jinja `TemplateResponse` wants `request` first on current Starlette.  
- Leftover `frontend/` is not this app.  
- Tabs need a pack. Empty workbench has no tabs.  
- `/static` is mounted last so it does not swallow API routes.

---

## On to next

Part 6 — all nine rooms on the same door (catalog + runner). Already built.
