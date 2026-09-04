# Maple AI

Phase-gate product-management copilot. Agentic RAG + HITL on a simulated Vancouver launch (Porter).

## Run locally (no Docker)

```powershell
copy .env.example .env
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```

Workbench: http://localhost:8000

## Docker

Puts Maple in a box and starts uvicorn on port 8000.

```powershell
docker compose up --build
```

Open http://localhost:8000

## Learn notes

Interview walkthroughs: [docs/learn/](docs/learn/README.md)
