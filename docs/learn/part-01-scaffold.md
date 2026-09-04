# Part 1 — Scaffold (I typed this; you re-walk it)

**Process miss:** you wanted to create these files. I wrote them. From Part 2 on: I spec, you type, I review.

## Plain English

Empty building only. Kitchen (FastAPI) and dining room (Next.js). Waiter contract (OpenAPI at `/docs`). Bouncer (dev JWT + role). Compose to start both. **No LangGraph, no RAG, no Porter index.**

## Why

So later parts plug into a real process (ports, CORS, roles) instead of a notebook script. Interviewers ask “how do you run this?” — this is the answer.

## What I created (every path)

| Path | Why |
|---|---|
| `.gitignore` | Ignore `.env`, venv, `node_modules`, `.next`, sqlite later |
| `.env.example` | `JWT_SECRET`, `CORS_ORIGINS`, empty `OPENAI_API_KEY` / LangSmith. **You still copy to `.env` — I did not create `.env`** |
| `backend/requirements.txt` | fastapi, uvicorn, pydantic v2, pydantic-settings, PyJWT, python-multipart |
| `backend/app/__init__.py` | Makes `app` a package so `uvicorn app.main:app` works |
| `backend/app/config.py` | Reads env. `cors_origin_list` splits the comma string |
| `backend/app/auth.py` | Roles: product, finance, engineering, exec, growth, legal. `issue_token` HS256 12h. `principal_from_token` or 401 |
| `backend/app/main.py` | CORS; `GET /health`; `GET /ready` (same as health for now); `POST /api/auth/dev-login`; `GET /api/me` |
| `backend/Dockerfile` | python:3.12-slim, pip, uvicorn :8000 |
| `frontend/package.json` | next 15, react 19, `next dev --port 3000` |
| `frontend/next.config.ts` | `output: "standalone"` for the Docker image |
| `frontend/tsconfig.json` | Strict TS, Next plugin |
| `frontend/next-env.d.ts` | Next type refs |
| `frontend/app/layout.tsx` | Title + paper background |
| `frontend/app/page.tsx` | Fetch `/health`; role dropdown; dev-login; store JWT; call `/api/me` |
| `frontend/Dockerfile` | multi-stage node 22, standalone server |
| `docker-compose.yml` | `api` :8000, `web` :3000, `depends_on` api, CORS localhost:3000 |
| `README.md` | How to run |

## How you would have made it (do this once so your hands know)

```powershell
cd c:\Users\siddh\OneDrive\Desktop\maple.ai
copy .env.example .env

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Other terminal:

```powershell
cd c:\Users\siddh\OneDrive\Desktop\maple.ai\frontend
npm install
npm run dev
```

Open http://localhost:8000/docs and http://localhost:3000. Click **Dev login**. Health should be `ok`. Session should show `Siddharth · product`.

Docker (optional): `docker compose up --build` after `.env` exists.

## Interview script

**Kitchen vs dining room?** FastAPI vs Next. UI can die; curl still works.

**OpenAPI?** `/docs` is generated from the FastAPI routes and Pydantic models.

**Why JWT now?** HITL is role-gated. SSO later still puts `role` on the token.

**health vs ready?** health = process. ready = later checkpointer + index. Part 1 they match.

**What never goes in git?** `.env` with real keys.

**CORS?** Browser on :3000 calling :8000 is cross-origin. Without CORS the UI looks “broken.”

## Gotchas I left for you

- `.env` is **not** on disk until you `copy .env.example .env`
- Frontend `node_modules` is **not** installed until you `npm install`
- Backend venv is **not** created until you make it
- Compose `env_file: .env` will fail if you skip the copy
- `NEXT_PUBLIC_API_URL` is baked at **frontend build** time in Docker; local `next dev` reads it at runtime (defaults to `http://localhost:8000`)

## I ran this / what I saw

- Copied `.env.example` → `.env` at repo root.
- Created `backend/.venv`, installed `requirements.txt` (includes pytest).
- `GET http://127.0.0.1:8000/health` → `{"status":"ok"}`.
- `POST /api/auth/dev-login` `{name: Siddharth, role: product}` → JWT `access_token`.
- `frontend`: `npm install` completed (`node_modules` now present). Start `npm run dev` yourself for the page on :3000.

## On to next

Part 2 — Pydantic `GatePack` + 9 artifact models + `state.py`. See [part-02-schemas-state.md](part-02-schemas-state.md).
