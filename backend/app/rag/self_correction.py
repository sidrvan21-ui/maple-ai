from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.rag.admit import repo_root

_llm: ChatOpenAI | None = None


def _llm_client() -> ChatOpenAI:
    global _llm
    if _llm is None:
        load_dotenv(repo_root() / ".env")
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return _llm


class GradeDocument(BaseModel):
    binary_score: str = Field(description="Relevance score: 'yes' or 'no'")


class GradeResult(BaseModel):
    kept: list[Document]
    dropped: list[str]

    model_config = {"arbitrary_types_allowed": True}


def grade_documents(query: str, docs: list[Document]) -> GradeResult:
    """Keep pieces that answer the query. Drop the rest."""
    grader = _llm_client().with_structured_output(GradeDocument)
    prompt = ChatPromptTemplate.from_template(
        "You grade whether a text chunk helps answer the query.\n"
        "Query: {query}\n"
        "Chunk: {document}\n"
        "Answer yes or no only in binary_score."
    )
    kept: list[Document] = []
    dropped: list[str] = []
    for doc in docs:
        res = (prompt | grader).invoke(
            {"query": query, "document": doc.page_content}
        )
        label = (res.binary_score or "").strip().lower()
        path = doc.metadata.get("source_path", "unknown")
        if label == "yes":
            kept.append(doc)
        else:
            dropped.append(f"{path}: {doc.page_content[:80]}")
    return GradeResult(kept=kept, dropped=dropped)


def rewrite_query(query: str) -> str:
    """Make a better local search string. Not a web search."""
    prompt = ChatPromptTemplate.from_template(
        "Rewrite this as a better search query over local research notes. "
        "Do not answer the question. Output only the new query.\n"
        "Original: {query}"
    )
    res = (prompt | _llm_client()).invoke({"query": query})
    return str(res.content).strip()
