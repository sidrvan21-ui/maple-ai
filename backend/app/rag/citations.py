from langchain_core.documents import Document

from app.schemas.common import Citation, RagTrace


def to_citations(docs: list[Document]) -> list[Citation]:
    """Turn kept chunks into Part 2 Citation objects."""
    out: list[Citation] = []
    for i, doc in enumerate(docs, start=1):
        out.append(
            Citation(
                id=f"c{i}",
                source_path=doc.metadata.get("source_path", "unknown"),
                span=doc.page_content[:240],
                why_kept="grader marked this chunk relevant",
            )
        )
    return out


def make_trace(
    questions: list[str],
    rewrite_hops: int,
    dropped: list[str],
) -> RagTrace:
    return RagTrace(
        questions=questions,
        rewrite_hops=rewrite_hops,
        chunks_dropped=dropped,
    )
