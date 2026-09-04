from pathlib import Path

STAGE_FOLDERS = {
    1: "s1_discovery",
    2: "s2_strategy",
    3: "s3_scoping",
    4: "s4_development",
    5: "s5_qualify",
    6: "s6_launch",
    7: "s7_growth",
    8: "s8_maturity",
    9: "s9_sunset",
}


def repo_root() -> Path:
    # this file is backend/app/rag/admit.py → three parents up is maple.ai
    return Path(__file__).resolve().parents[3]


def admitted_paths(admitted_stages: list[int]) -> list[Path]:
    """Files the retriever may read. Admit is a filter, not a prompt."""
    root = repo_root()
    raw = root / "data" / "raw_inputs"
    blocked = (raw / "README.md").resolve()
    out: list[Path] = []

    pm = root / "data" / "pm_knowledge"
    if pm.is_dir():
        out.extend(sorted(pm.glob("*.md")))

    for stage in admitted_stages:
        name = STAGE_FOLDERS.get(stage)
        if not name:
            continue
        folder = raw / name
        if folder.is_dir():
            out.extend(sorted(folder.glob("*.md")))

    return [p for p in out if p.resolve() != blocked]
