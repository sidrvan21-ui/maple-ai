from fastapi import HTTPException, status
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, create_model

from app.agents.catalog import StageSpec, spec_for
from app.guardrails import draft_ids_exist, receipts_are_admitted, require_receipts
from app.rag.pipeline import run_agentic_rag
from app.schemas.common import Assumption, Citation, Decision, MapleTake, Risk
from app.schemas.gate import GatePack


def _draft_model(spec: StageSpec) -> type[BaseModel]:
    return create_model(
        f"{spec.artifacts_cls.__name__}Draft",
        decision=(Decision, ...),
        artifacts=(spec.artifacts_cls, ...),
        assumptions=(list[Assumption], Field(default_factory=list)),
        risks=(list[Risk], Field(default_factory=list)),
        open_questions=(list[str], Field(default_factory=list)),
        confidence=(float, Field(ge=0, le=1)),
    )


def fill_briefing(spec: StageSpec, citations: list[Citation]) -> BaseModel:
    writer = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(
        _draft_model(spec)
    )
    receipt_text = "\n".join(
        f"{c.id} | {c.source_path} | {c.span}" for c in citations
    )
    prompt = ChatPromptTemplate.from_template(
        "Fill a {stage} briefing using ONLY these receipts.\n"
        "{rules}\n"
        "Every number must use citation_id like c1 or an assumption_id.\n\n"
        "Receipts:\n{receipts}\n"
    )
    return (prompt | writer).invoke(
        {
            "stage": spec.name,
            "rules": spec.writer_rules,
            "receipts": receipt_text,
        }
    )


def fill_maple_take(spec: StageSpec, citations: list[Citation], draft: BaseModel) -> MapleTake:
    """Maple's gate memo. Judgment, not a class card and not a human PM."""
    writer = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(
        MapleTake
    )
    receipt_text = "\n".join(
        f"{c.id} | {c.source_path} | {c.span}" for c in citations
    )
    prompt = ChatPromptTemplate.from_template(
        "You are Maple writing a gate memo for product, finance, and engineering "
        "in a {stage} review. Show business judgment. Do not teach "
        "frameworks. Do not define JTBD or SWOT. Do not invent numbers.\n"
        "This is Maple's take, not a staff PM's. "
        "Facts only from receipts (cite c1) or from the draft.\n\n"
        "Decision: {decision}\n"
        "Draft: {draft}\n"
        "Receipts:\n{receipts}\n"
    )
    return (prompt | writer).invoke(
        {
            "stage": spec.name,
            "decision": draft.decision.model_dump_json(),
            "draft": draft.model_dump_json(),
            "receipts": receipt_text,
        }
    )


def run_stage(
    stage: int,
    admitted_stages: list[int],
    product_id: str = "porter",
) -> GatePack:
    """RAG → briefing → Maple take → pack."""
    if stage not in admitted_stages:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "stage folder is not admitted",
        )
    spec = spec_for(stage)
    citations, trace = run_agentic_rag(
        spec.mission,
        admitted_stages=admitted_stages,
        product_id=product_id,
    )
    require_receipts(citations)
    receipts_are_admitted(citations, admitted_stages, product_id)
    draft = fill_briefing(spec, citations)
    draft_ids_exist(draft, citations)
    take = fill_maple_take(spec, citations, draft)
    return GatePack(
        stage=spec.number,  # type: ignore[arg-type]
        decision=draft.decision,
        confidence=draft.confidence,
        open_questions=draft.open_questions,
        citations=citations,
        assumptions=draft.assumptions,
        risks=draft.risks,
        raci=[],
        required_approver_roles=["product"],
        artifacts=draft.artifacts,
        teaching_note=spec.lesson,
        maple_take=take,
        rag_trace=trace,
    )
