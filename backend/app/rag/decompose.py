from dotenv import load_dotenv
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

SEED_QUESTIONS = [
    "What jobs are people hiring this product for?",
    "Which market-size numbers appear and do they conflict?",
    "Who are the competitors and substitutes mentioned?",
    "What privacy or legal constraints are stated?",
]


class QuestionList(BaseModel):
    questions: list[str] = Field(description="4 to 8 search questions")


def decompose(mission: str) -> list[str]:
    """Turn one mission into several search questions."""
    prompt = ChatPromptTemplate.from_template(
        "Break this product-discovery mission into 4 to 8 short search questions.\n"
        "Cover jobs, market-size fights, competitors, and constraints.\n"
        "Mission: {mission}"
    )
    try:
        res = (prompt | _llm_client().with_structured_output(QuestionList)).invoke(
            {"mission": mission}
        )
        qs = [q.strip() for q in res.questions if q.strip()]
        if qs:
            return qs[:8]
    except Exception:
        pass
    return [mission, *SEED_QUESTIONS]
