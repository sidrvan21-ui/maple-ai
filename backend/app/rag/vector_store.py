import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document

from app.rag.admit import admitted_paths, repo_root
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from rank_bm25 import BM25Okapi

load_dotenv(repo_root() / ".env")


def require_openai_key() -> None:
    if not (os.getenv("OPENAI_API_KEY") or "").strip():
        raise RuntimeError(
            "OPENAI_API_KEY in the repo .env is empty. "
            "Paste a real OpenAI key on that line, save the file, and restart the server."
        )

ALL_STAGES = list(range(1, 10))


def _source_path(path: Path) -> str:
    return path.resolve().relative_to(repo_root()).as_posix()


def allowed_source_paths(
    admitted_stages: list[int],
    product_id: str = "porter",
) -> set[str]:
    return {_source_path(p) for p in admitted_paths(admitted_stages, product_id)}


def filter_admitted(
    docs: list[Document],
    admitted_stages: list[int],
    product_id: str = "porter",
) -> list[Document]:
    allowed = allowed_source_paths(admitted_stages, product_id)
    return [d for d in docs if d.metadata.get("source_path") in allowed]


def load_documents(
    admitted_stages: list[int],
    product_id: str = "porter",
) -> list[Document]:
    docs: list[Document] = []
    for path in admitted_paths(admitted_stages, product_id):
        text = path.read_text(encoding="utf-8", errors="replace")
        docs.append(
            Document(
                page_content=text,
                metadata={"source_path": _source_path(path)},
            )
        )
    return docs


def chunk_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    return splitter.split_documents(docs)


class HybridStore:
    def __init__(self, chunks: list[Document]):
        self.chunks = chunks
        self._dense = FAISS.from_documents(chunks, OpenAIEmbeddings())
        words = [c.page_content.lower().split() for c in chunks]
        self._bm25 = BM25Okapi(words)

    def retrieve(self, query: str, k: int = 6) -> list[Document]:
        dense_hits = self._dense.similarity_search(query, k=k)
        scores = self._bm25.get_scores(query.lower().split())
        best = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        sparse_hits = [self.chunks[i] for i in best[:k] if scores[i] > 0]
        seen: set[tuple[str, str]] = set()
        out: list[Document] = []
        for doc in dense_hits + sparse_hits:
            key = (doc.metadata.get("source_path", ""), doc.page_content[:80])
            if key in seen:
                continue
            seen.add(key)
            out.append(doc)
            if len(out) >= k:
                break
        return out


_stores: dict[str, HybridStore] = {}


def drop_store(product_id: str | None = None) -> None:
    if product_id is None:
        _stores.clear()
        return
    _stores.pop(product_id, None)


def get_store(product_id: str = "porter") -> HybridStore:
    """Index once per product. Admit is applied in retrieve, not at index time."""
    key = product_id or "porter"
    if key not in _stores:
        require_openai_key()
        _stores[key] = HybridStore(chunk_documents(load_documents(ALL_STAGES, key)))
    return _stores[key]


def retrieve(
    query: str,
    k: int = 6,
    admitted_stages: list[int] | None = None,
    product_id: str = "porter",
) -> list[Document]:
    stages = admitted_stages or [1]
    raw = get_store(product_id).retrieve(query, k=max(k * 4, 24))
    return filter_admitted(raw, stages, product_id)[:k]
