from app.rag.citations import make_trace, to_citations
from app.rag.decompose import decompose
from app.rag.self_correction import grade_documents, rewrite_query
from app.rag.vector_store import retrieve
from app.schemas.common import Citation, RagTrace

MAX_REWRITE_HOPS = 2


def run_agentic_rag(
    mission: str,
    admitted_stages: list[int] | None = None,
) -> tuple[list[Citation], RagTrace]:
    """Retrieve, grade, rewrite locally. Stop at citations. No web. No GatePack."""
    stages = admitted_stages or [1]
    questions = decompose(mission)
    kept_docs = []
    dropped: list[str] = []
    hops = 0

    for question in questions:
        q = question
        hits = retrieve(q, admitted_stages=stages)
        result = grade_documents(q, hits)
        dropped.extend(result.dropped)

        local_hops = 0
        while not result.kept and local_hops < MAX_REWRITE_HOPS:
            q = rewrite_query(q)
            hops += 1
            local_hops += 1
            hits = retrieve(q, admitted_stages=stages)
            result = grade_documents(q, hits)
            dropped.extend(result.dropped)

        kept_docs.extend(result.kept)

    unique = []
    seen: set[tuple[str, str]] = set()
    for doc in kept_docs:
        key = (doc.metadata.get("source_path", ""), doc.page_content[:80])
        if key in seen:
            continue
        seen.add(key)
        unique.append(doc)

    return to_citations(unique), make_trace(questions, hops, dropped)


if __name__ == "__main__":
    cites, trace = run_agentic_rag(
        "What TAM numbers exist in the research dump?"
    )
    print("citations", [c.source_path for c in cites])
    print("questions", trace.questions)
    print("rewrite_hops", trace.rewrite_hops)
    print("dropped", len(trace.chunks_dropped))
