# Part 8 — Save / export (living notes)

**Status:** built. One SQLite file, one row per product. Stages 7–9 nodes were already Part 6.

---

## Problem

Restart the server → RAM `_STORE` is empty → gates vanish.

---

## Fix

SQLite file `data/maple.db`. One row = the whole bag (`porter`): room, open rooms, every pack, Sign/Reject, ledgers.

Python already has `sqlite3`. No extra install. No nine tables.

---

## What we created

| Path | Job |
|---|---|
| `backend/app/persist.py` | save / load / JSON bag |
| `backend/app/session.py` | RAM first; if empty, load from SQLite |
| `backend/app/hitl.py` | after run-in-review / sign / reject → `save_state` |
| `GET /api/products/{id}/export` | same bag as JSON |
| `backend/tests/test_persist.py` | wipe RAM, load again, Stage 2 still open |
| `backend/tests/conftest.py` | tests use a temp db file |

---

## Locked picture

| Thing | Holds |
|---|---|
| SQLite | the bag (progress) |
| Vector store | raw notes + pm_knowledge chunks |
| Catalog | missions / lessons |

SQLite does **not** store fieldwork. It does **not** unlock rooms. Sign still unlocks. SQLite only **remembers**.

---

## How to demo

1. Run Discovery → Sign.  
2. Stop uvicorn. Start it again.  
3. Open workbench: pack still there, **Run Strategy**, sunset still locked.

Tests:

```
.\.venv\Scripts\python.exe -m pytest tests\test_persist.py tests\test_hitl.py tests\test_pages_login.py -q
```

---

## Gotchas

- `data/maple.db` is gitignored.  
- Tests set `MAPLE_DB_PATH` to a temp file so pytest does not wipe your demo db.  
- `forget_ram()` = fake restart. Disk stays.  
- This is **not** LangGraph `SqliteSaver`. Same idea (disk), our table.

---

## On to next

Pretty briefing tabs per room, or Docker polish. Not more stage brains.
