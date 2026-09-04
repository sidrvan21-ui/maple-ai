from app.persist import clear_all, load_state
from app.schemas.gate import GatePack
from app.state import MapleState, initial_state

_STORE: dict[str, MapleState] = {}


def get_state(product_id: str) -> MapleState:
    if product_id not in _STORE:
        loaded = load_state(product_id)
        _STORE[product_id] = loaded if loaded is not None else initial_state(product_id)
    return _STORE[product_id]


def forget_ram() -> None:
    """Tests: pretend the server restarted. Disk is kept."""
    _STORE.clear()


def reset_store() -> None:
    """Tests only. Wipe RAM and the SQLite file."""
    _STORE.clear()
    clear_all()


def visible_pack(state: MapleState, view: int | None = None) -> GatePack | None:
    packs = state.get("gate_packs") or {}
    if view is not None and view in packs:
        return packs[view]
    cur = state["current_stage"]
    if cur in packs:
        return packs[cur]
    prev = cur - 1
    if prev in packs:
        return packs[prev]
    return None
