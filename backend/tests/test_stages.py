from fastapi import HTTPException
from langchain_core.documents import Document
import pytest

from app.agents.catalog import SPECS
from app.agents.runner import run_stage
from app.rag.admit import admitted_paths
from app.rag.vector_store import _source_path, filter_admitted
from app.session import reset_store, visible_pack
from app.state import initial_state


def test_catalog_has_nine_rooms():
    assert list(SPECS) == list(range(1, 10))
    assert SPECS[1].name == "Discovery"
    assert SPECS[9].name == "Sunset"


def test_admitted_two_sees_s2_not_s3():
    joined = "\n".join(p.as_posix() for p in admitted_paths([1, 2]))
    assert "s2_strategy" in joined
    assert "s3_scoping" not in joined
    assert "s9_sunset" not in joined


def test_filter_drops_locked_folders():
    real_s1 = _source_path(
        next(p for p in admitted_paths([1]) if "s1_discovery" in p.as_posix())
    )
    docs = [
        Document(page_content="tam", metadata={"source_path": real_s1}),
        Document(
            page_content="eol",
            metadata={
                "source_path": "data/raw_inputs/s9_sunset/01_deprecate_sms_noisy_sku.md"
            },
        ),
    ]
    kept = filter_admitted(docs, [1])
    assert len(kept) == 1
    assert "s1_discovery" in kept[0].metadata["source_path"]


def test_run_stage_two_blocked_before_sign():
    with pytest.raises(HTTPException) as exc:
        run_stage(2, admitted_stages=[1])
    assert exc.value.status_code == 403


def test_visible_pack_after_sign_shows_previous():
    reset_store()
    state = initial_state("vis")
    from tests.test_hitl import _tiny_pack
    from app.hitl import put_in_review, sign_pack

    put_in_review(state, _tiny_pack())
    sign_pack(state, "product")
    shown = visible_pack(state)
    assert shown is not None
    assert shown.stage == 1
    assert state["current_stage"] == 2
