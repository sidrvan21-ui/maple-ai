"""One SQLite file. One row per product. The whole bag, not nine tables."""

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.rag.admit import repo_root
from app.schemas.gate import GatePack
from app.state import LedgersState, MapleState


def db_path() -> Path:
    raw = os.environ.get("MAPLE_DB_PATH")
    if raw:
        return Path(raw)
    return repo_root() / "data" / "maple.db"


def _connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            at TEXT NOT NULL,
            actor TEXT NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            product_id TEXT NOT NULL,
            detail TEXT NOT NULL
        )
        """
    )
    return conn


def state_to_payload(state: MapleState) -> str:
    packs = {
        str(k): v.model_dump() if hasattr(v, "model_dump") else v
        for k, v in (state.get("gate_packs") or {}).items()
    }
    return json.dumps(
        {
            "product_id": state["product_id"],
            "current_stage": state["current_stage"],
            "hitl": state["hitl"],
            "admitted_stages": state["admitted_stages"],
            "required_approver_roles": list(state.get("required_approver_roles") or []),
            "gate_packs": packs,
            "ledgers": state.get("ledgers")
            or {"decisions": [], "assumptions": [], "risks": []},
        }
    )


def payload_to_state(raw: str) -> MapleState:
    data = json.loads(raw)
    packs = {
        int(k): GatePack.model_validate(v) for k, v in (data.get("gate_packs") or {}).items()
    }
    ledgers = data.get("ledgers") or {}
    return MapleState(
        product_id=data["product_id"],
        current_stage=int(data["current_stage"]),
        hitl=data["hitl"],
        admitted_stages=[int(n) for n in data["admitted_stages"]],
        required_approver_roles=list(data.get("required_approver_roles") or ["product"]),
        gate_packs=packs,
        ledgers=LedgersState(
            decisions=list(ledgers.get("decisions") or []),
            assumptions=list(ledgers.get("assumptions") or []),
            risks=list(ledgers.get("risks") or []),
        ),
    )


def save_state(state: MapleState) -> None:
    payload = state_to_payload(state)
    now = datetime.now(UTC).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO products (product_id, payload, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = excluded.updated_at
            """,
            (state["product_id"], payload, now),
        )


def load_state(product_id: str) -> MapleState | None:
    if not db_path().exists():
        return None
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload FROM products WHERE product_id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        return None
    return payload_to_state(row[0])


def append_audit(
    *,
    actor: str,
    role: str,
    action: str,
    product_id: str = "",
    detail: str = "",
) -> None:
    now = datetime.now(UTC).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_log (at, actor, role, action, product_id, detail)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (now, actor, role, action, product_id, detail),
        )


def list_audit(product_id: str, limit: int = 40) -> list[dict]:
    if not db_path().exists():
        return []
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT at, actor, role, action, product_id, detail
            FROM audit_log
            WHERE product_id = ? OR product_id = ''
            ORDER BY id DESC
            LIMIT ?
            """,
            (product_id, limit),
        ).fetchall()
    out = []
    for r in rows:
        raw = r[0]
        try:
            dt = datetime.fromisoformat(raw)
            when = dt.strftime("%d %b %Y · %H:%M")
        except ValueError:
            when = raw[:16]
        out.append(
            {
                "at": raw,
                "when": when,
                "actor": r[1],
                "role": r[2],
                "action": r[3],
                "product_id": r[4],
                "detail": r[5],
            }
        )
    return out


def clear_all() -> None:
    """Wipe rows. Do not delete the file (Windows keeps SQLite locked)."""
    if not db_path().exists():
        return
    with _connect() as conn:
        conn.execute("DELETE FROM products")
        conn.execute("DELETE FROM audit_log")
        conn.commit()
