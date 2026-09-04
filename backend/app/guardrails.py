"""Maple rails: admit / receipts / ids. Not generic LLM safety."""

from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel

from app.rag.vector_store import allowed_source_paths
from app.schemas.common import Citation
from app.state import MapleState

_CITE_KEYS = ("citation_id", "story_points_citation_id")
_ASSUME_KEYS = ("assumption_id", "story_points_assumption_id")


def block_if_in_review(state: MapleState) -> None:
    """Do not spend another Run while a pack is waiting for Sign."""
    if state.get("hitl") == "in_review":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "pack is in review — Sign or Reject before running again",
        )


def require_receipts(citations: list[Citation]) -> None:
    """No receipts → no writer. Empty pack is not a briefing."""
    if not citations:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "no admitted receipts — writer was not called",
        )


def receipts_are_admitted(
    citations: list[Citation],
    admitted_stages: list[int],
) -> None:
    allowed = allowed_source_paths(admitted_stages)
    leaked = [c.source_path for c in citations if c.source_path not in allowed]
    if leaked:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "receipt path is not admitted",
        )


def _walk_ids(payload: Any, cite_ids: set[str], assume_ids: set[str]) -> None:
    if isinstance(payload, BaseModel):
        _walk_ids(payload.model_dump(), cite_ids, assume_ids)
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in _CITE_KEYS and value:
                cite_ids.add(str(value))
            elif key in _ASSUME_KEYS and value:
                assume_ids.add(str(value))
            else:
                _walk_ids(value, cite_ids, assume_ids)
        return
    if isinstance(payload, list):
        for item in payload:
            _walk_ids(item, cite_ids, assume_ids)


def draft_ids_exist(draft: BaseModel, citations: list[Citation]) -> None:
    """Every id the writer used must be a real receipt or its own assumption."""
    used_cites: set[str] = set()
    used_assumptions: set[str] = set()
    _walk_ids(draft, used_cites, used_assumptions)
    known_cites = {c.id for c in citations}
    known_assumptions = {
        str(row.get("id") if isinstance(row, dict) else row.id)
        for row in getattr(draft, "assumptions", []) or []
    }
    if used_cites - known_cites or used_assumptions - known_assumptions:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "draft cited an id that is not in the receipts",
        )
