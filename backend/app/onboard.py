"""Company onboarding copy: nine rooms + empty zip kit."""

from __future__ import annotations

import io
import re
import zipfile

from app.agents.catalog import SPECS
from app.rag.admit import STAGE_FOLDERS

FOLDER_ALIASES: dict[str, int] = {}
for n, folder in STAGE_FOLDERS.items():
    FOLDER_ALIASES[folder] = n
    FOLDER_ALIASES[SPECS[n].name.lower()] = n
    FOLDER_ALIASES[str(n)] = n
    FOLDER_ALIASES[f"{n}_{SPECS[n].name.lower()}"] = n

ROOM_SORT = {
    1: {
        "put": [
            "Interviews, call notes, surveys",
            "Competitor write-ups",
            "Market-size spreadsheets (keep two numbers if they fight)",
            "Privacy or legal notes about the problem",
        ],
        "skip": ["Sprint tickets", "Launch-week metrics", "Sunset / EOL drafts"],
    },
    2: {
        "put": [
            "Where we sell, how we win",
            "Pricing notes, even napkin math",
            "OKRs, business-model slides, exec strategy email",
        ],
        "skip": ["User-story dumps", "Beta diaries"],
    },
    3: {
        "put": [
            "Feature lists, must / should / won't fights",
            "Stories and PRD drafts for this cut",
            "Constraints (time, legal) that bound the cut",
        ],
        "skip": ["Live defect trackers", "Day-0 launch numbers"],
    },
    4: {
        "put": [
            "Sprint notes, standups, change requests",
            "Bugs, usability sessions",
            "Beta plan and rollback talk",
        ],
        "skip": ["Go / no-go launch thread", "Growth experiment logs"],
    },
    5: {
        "put": [
            "Beta results",
            "Go / no-go emails",
            "Support, sales, privacy-export checklists",
        ],
        "skip": ["App-store quotes from week one", "Sunset notices"],
    },
    6: {
        "put": [
            "What happened in week one",
            "Missed alerts, ads, what people said",
        ],
        "skip": ["Old discovery interviews", "Cost-to-serve models"],
    },
    7: {
        "put": [
            "Funnel / cohort notes",
            "Experiment logs, referrals, churn stories",
        ],
        "skip": ["EOL legal", "Brand-new discovery interviews"],
    },
    8: {
        "put": [
            "Cost to serve, support load",
            "NPS quotes (do not average them)",
            "Tech debt, finance reviews",
        ],
        "skip": ["Research for a different product"],
    },
    9: {
        "put": [
            "Why we might turn it off",
            "Notice drafts, export requests, what must survive",
        ],
        "skip": ["Wishlists for the next product (that is Discovery)"],
    },
}


def rooms_for_page() -> list[dict]:
    out = []
    for n, spec in SPECS.items():
        guide = ROOM_SORT[n]
        out.append(
            {
                "n": n,
                "name": spec.name,
                "folder": STAGE_FOLDERS[n],
                "one_liner": spec.lesson.one_liner,
                "job": spec.lesson.pm_job,
                "put": guide["put"],
                "skip": guide["skip"],
                "ask": spec.lesson.questions_to_ask,
            }
        )
    return out


def slug_product(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug[:60] or "product"


def _norm_folder(part: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", part.strip().lower()).strip("_")


def stage_from_path(name: str) -> int | None:
    for part in name.replace("\\", "/").split("/"):
        key = _norm_folder(part)
        if key in FOLDER_ALIASES:
            return FOLDER_ALIASES[key]
    return None


def parse_room(raw: str) -> int:
    if raw in {"", "unsure", "0"}:
        return 1
    try:
        n = int(raw)
    except ValueError:
        return 1
    return n if n in STAGE_FOLDERS else 1


def template_zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "README.md",
            "Optional kit. Drop files into a folder if you already know the room.\n"
            "If you do not, upload loose files on the Onboard page — Maple puts them in Discovery.\n"
            "Anything is fine: Word, PDF, Excel, slides, text, zip of a messy folder.\n",
        )
        for room in rooms_for_page():
            lines = [
                f"# {room['n']}. {room['name']}",
                "",
                room["one_liner"],
                "",
                "## Put here",
                *[f"- {p}" for p in room["put"]],
                "",
                "## Skip",
                *[f"- {s}" for s in room["skip"]],
                "",
            ]
            zf.writestr(f"{room['folder']}/README.md", "\n".join(lines))
    return buf.getvalue()
