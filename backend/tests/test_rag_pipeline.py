import os

import pytest

from app.rag.citations import to_citations
from langchain_core.documents import Document


def test_to_citations_uses_source_path():
    doc = Document(
        page_content="248k is one input",
        metadata={"source_path": "data/raw_inputs/s1_discovery/11_tam_scrap_stats_can_units.md"},
    )
    cites = to_citations([doc])
    assert cites[0].id == "c1"
    assert "11_tam_scrap" in cites[0].source_path


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="needs OPENAI_API_KEY",
)
def test_pipeline_tam_keeps_both_scraps_and_blocks_s9():
    from app.rag.pipeline import run_agentic_rag

    cites, _trace = run_agentic_rag("What TAM numbers exist in the research dump?")
    paths = " ".join(c.source_path for c in cites)
    assert "11_tam_scrap" in paths
    assert "12_tam_scrap" in paths
    assert "s9_sunset" not in paths
