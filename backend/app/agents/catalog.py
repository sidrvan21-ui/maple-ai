from dataclasses import dataclass

from pydantic import BaseModel

from app.schemas.common import TeachingNote
from app.schemas.development import DevelopmentArtifacts
from app.schemas.discovery import DiscoveryArtifacts
from app.schemas.growth import GrowthArtifacts
from app.schemas.launch import LaunchArtifacts
from app.schemas.maturity import MaturityArtifacts
from app.schemas.qualify import QualifyArtifacts
from app.schemas.scoping import ScopingArtifacts
from app.schemas.strategy import StrategyArtifacts
from app.schemas.sunset import SunsetArtifacts

GATE = "Human signs one pack. That unlocks the next research folder."

# Short board brief for the workbench side. Not a class card.
GATE_BRIEF = {
    1: {
        "decide": "Is the opportunity real enough to fund a strategy?",
        "avoid": "Do not average conflicting market numbers.",
        "next": "Sign unlocks Strategy.",
    },
    2: {
        "decide": "Where do we play, and how do we win?",
        "avoid": "Do not treat a feature list as strategy. Do not invent LTV or CAC.",
        "next": "Sign unlocks Scoping.",
    },
    3: {
        "decide": "What ships in this cut — and what is out?",
        "avoid": "Do not hide the won't list or collapse RICE into one fake score.",
        "next": "Sign unlocks Development.",
    },
    4: {
        "decide": "Can we beta with a known defect list and a rollback?",
        "avoid": "Do not mark work done without evidence.",
        "next": "Sign unlocks Qualify.",
    },
    5: {
        "decide": "Go, scoped-go, or no-go. Launch is a call, not a date.",
        "avoid": "Do not ship around an open blocker.",
        "next": "Sign unlocks Launch.",
    },
    6: {
        "decide": "What actually happened in week one?",
        "avoid": "Do not hide missed alerts or treat press as adoption.",
        "next": "Sign unlocks Growth.",
    },
    7: {
        "decide": "Is there a repeatable loop, or only a story?",
        "avoid": "Do not invent conversion rates.",
        "next": "Sign unlocks Maturity.",
    },
    8: {
        "decide": "Sustain, harvest, or prepare to sunset?",
        "avoid": "Do not average NPS quotes into one score.",
        "next": "Sign unlocks Sunset.",
    },
    9: {
        "decide": "Can we retire with notice, export, and a survivor?",
        "avoid": "Do not shut down silently or invent legal dates.",
        "next": "Sign closes the cycle.",
    },
}


def _lesson(
    stage_name: str,
    one_liner: str,
    pm_job: str,
    frameworks: list[str],
    must_produce: list[str],
    common_failure: list[str],
    questions_to_ask: list[str],
    next_stage_teaser: str,
) -> TeachingNote:
    return TeachingNote(
        stage_name=stage_name,
        one_liner=one_liner,
        pm_job=pm_job,
        frameworks=frameworks,
        must_produce=must_produce,
        common_failure=common_failure,
        questions_to_ask=questions_to_ask,
        how_this_gate_works=GATE,
        next_stage_teaser=next_stage_teaser,
    )


@dataclass(frozen=True)
class StageSpec:
    number: int
    name: str
    mission: str
    lesson: TeachingNote
    artifacts_cls: type[BaseModel]
    writer_rules: str


SPECS: dict[int, StageSpec] = {
    1: StageSpec(
        number=1,
        name="Discovery",
        mission=(
            "Run Discovery on the admitted research. "
            "Find jobs, conflicting market-size numbers, competitors, and privacy constraints."
        ),
        lesson=_lesson(
            "Discovery",
            "Understand the opportunity before you pick a strategy.",
            "Turn messy research into a clear problem, user, and market picture.",
            ["JTBD", "TAM/SAM/SOM inputs", "SWOT", "personas"],
            ["problem and who", "jobs", "competing options", "market-size inputs that may conflict"],
            ["averaging two market numbers", "starting with features"],
            ["Whose job is this?", "What numbers disagree?", "What would kill this?"],
            "Strategy comes next: where we play and how we win.",
        ),
        artifacts_cls=DiscoveryArtifacts,
        writer_rules="If two market numbers appear, list both. Do not average.",
    ),
    2: StageSpec(
        number=2,
        name="Strategy",
        mission=(
            "Run Strategy on admitted research. "
            "Find where we play, how we win, pricing analogs, and strategy options."
        ),
        lesson=_lesson(
            "Strategy",
            "Pick the game before you write the backlog.",
            "Choose a vision, a playing field, and a way to win.",
            ["BMC", "Porter five forces", "Ansoff", "OKRs"],
            ["vision", "options with one pick", "business-case inputs", "now/next/later"],
            ["writing features as strategy", "inventing LTV or CAC"],
            ["Where do we play?", "How do we win?", "What number is only a napkin?"],
            "Scoping comes next: what ships in this cut.",
        ),
        artifacts_cls=StrategyArtifacts,
        writer_rules="Revenue and cost numbers must be grounded. Do not invent LTV or CAC.",
    ),
    3: StageSpec(
        number=3,
        name="Scoping",
        mission=(
            "Run Scoping on admitted research. "
            "Find the cut: MRD/PRD, MoSCoW fights, RICE inputs, and privacy constraints."
        ),
        lesson=_lesson(
            "Scoping",
            "A cut is a decision, not a wishlist.",
            "Turn strategy into what is in, out, and later.",
            ["MRD", "PRD", "MoSCoW", "RICE inputs"],
            ["market problem", "product requirements", "must/should/could/wont", "open fights"],
            ["scoring RICE as one fake number", "hiding the won't list"],
            ["What is out?", "Which fight is still open?", "What would slip the cut?"],
            "Development comes next: build and learn in the open.",
        ),
        artifacts_cls=ScopingArtifacts,
        writer_rules="List RICE inputs separately. Do not collapse them into one score.",
    ),
    4: StageSpec(
        number=4,
        name="Development",
        mission=(
            "Run Development on admitted research. "
            "Find sprint reality, defects, usability, and beta-plan questions."
        ),
        lesson=_lesson(
            "Development",
            "The plan meets the build.",
            "Track what changed, what is broken, and whether beta can start.",
            ["checklist", "beta plan", "usability", "agile"],
            ["checklist", "open defects", "usability findings", "beta who/questions"],
            ["green-shifting defects", "beta with no rollback"],
            ["What slipped?", "What blocks beta?", "What did users fail to do?"],
            "Qualify comes next: is this launchable?",
        ),
        artifacts_cls=DevelopmentArtifacts,
        writer_rules="Do not mark items done unless a receipt says so. Story points need a citation or assumption.",
    ),
    5: StageSpec(
        number=5,
        name="Qualify",
        mission=(
            "Run Qualify on admitted research. "
            "Find beta results, launch blockers, PIPA readiness, and go/no-go signals."
        ),
        lesson=_lesson(
            "Qualify",
            "Launch is a decision, not a date.",
            "Judge readiness across product, ops, support, and privacy.",
            ["beta results", "launch readiness", "RACI"],
            ["beta evidence", "blockers", "go / no-go / scoped-go", "PIPA check"],
            ["shipping around a blocker", "calling beta a launch"],
            ["What is still red?", "Who owns the launch call?", "Can we export user data?"],
            "Launch comes next: the first week in market.",
        ),
        artifacts_cls=QualifyArtifacts,
        writer_rules="If a blocker is named, keep it. Do not smooth a no-go into a go.",
    ),
    6: StageSpec(
        number=6,
        name="Launch",
        mission=(
            "Run Launch on admitted research. "
            "Find day-0 metrics, missed alerts, demand-gen honesty, and first-week sentiment."
        ),
        lesson=_lesson(
            "Launch",
            "The first week teaches more than the plan.",
            "Record what actually happened, not the war-room slide.",
            ["launch plan", "day-0 metrics", "sentiment"],
            ["what shipped", "what missed", "what people said", "next actions"],
            ["hiding missed alerts", "treating a press note as adoption"],
            ["What failed on day 0?", "Who did we not reach?", "What do we fix this week?"],
            "Growth comes next: loops, not one-off push.",
        ),
        artifacts_cls=LaunchArtifacts,
        writer_rules="Keep missed alerts and complaints. Do not invent open rates.",
    ),
    7: StageSpec(
        number=7,
        name="Growth",
        mission=(
            "Run Growth on admitted research. "
            "Find AARRR notes, experiments, cohorts, and whether PLG is real."
        ),
        lesson=_lesson(
            "Growth",
            "Growth is a loop you can measure, or it is hope.",
            "Separate experiments that moved a number from stories.",
            ["AARRR", "experiments", "cohorts"],
            ["funnel notes", "experiment results", "retention clues", "growth risks"],
            ["calling one A/B a growth engine", "ignoring churn stories"],
            ["Which loop repeats?", "What did the experiment actually change?", "Who churned?"],
            "Maturity comes next: cost, debt, and stay-or-decline.",
        ),
        artifacts_cls=GrowthArtifacts,
        writer_rules="Do not invent conversion rates. Quote experiment results as written.",
    ),
    8: StageSpec(
        number=8,
        name="Maturity",
        mission=(
            "Run Maturity on admitted research. "
            "Find cost-to-serve, NPS quotes, tech debt, and sustain vs decline."
        ),
        lesson=_lesson(
            "Maturity",
            "A mature product can still be the wrong product.",
            "Weigh cost, debt, and whether the job is still being done.",
            ["cost-to-serve", "NPS qualitative", "tech debt"],
            ["cost picture", "qualitative NPS", "debt list", "sustain or decline"],
            ["averaging NPS quotes into a fake score", "adding SKUs to hide decline"],
            ["What does one building cost?", "Did we become email again?", "Is this decline?"],
            "Sunset comes next: how we leave without harm.",
        ),
        artifacts_cls=MaturityArtifacts,
        writer_rules="Keep NPS as quotes. Do not invent a single NPS number.",
    ),
    9: StageSpec(
        number=9,
        name="Sunset",
        mission=(
            "Run Sunset on admitted research. "
            "Find why to retire, notice/export duties, and what must survive."
        ),
        lesson=_lesson(
            "Sunset",
            "Ending well is a product job.",
            "Retire with notice, export, and a clear survivor.",
            ["EOL plan", "notice", "data export"],
            ["reasons", "timeline words", "90-day notice", "what survives"],
            ["silent shutdown", "keeping data with no purpose"],
            ["Who must be told?", "What data leaves with the user?", "What do we keep?"],
            "This is the last gate. Sign closes the cycle.",
        ),
        artifacts_cls=SunsetArtifacts,
        writer_rules="Do not invent legal dates. Use the words in the receipts.",
    ),
}


def spec_for(stage: int) -> StageSpec:
    if stage not in SPECS:
        raise ValueError(f"unknown stage {stage}")
    return SPECS[stage]
