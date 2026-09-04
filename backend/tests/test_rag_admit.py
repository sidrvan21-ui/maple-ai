from app.rag.admit import admitted_paths


def test_stage_1_includes_discovery_and_textbook():
    paths = [p.as_posix() for p in admitted_paths([1])]
    joined = "\n".join(paths)
    assert any("s1_discovery" in p for p in paths)
    assert any("pm_knowledge" in p for p in paths)
    assert "s9_sunset" not in joined
    assert not any(p.endswith("raw_inputs/README.md") for p in paths)


def test_all_nine_folders_when_fully_admitted():
    joined = "\n".join(p.as_posix() for p in admitted_paths(list(range(1, 10))))
    for folder in (
        "s1_discovery",
        "s2_strategy",
        "s3_scoping",
        "s4_development",
        "s5_qualify",
        "s6_launch",
        "s7_growth",
        "s8_maturity",
        "s9_sunset",
    ):
        assert folder in joined


def test_stage_1_has_both_tam_scraps():
    names = [p.name for p in admitted_paths([1])]
    assert "11_tam_scrap_stats_can_units.md" in names
    assert "12_tam_scrap_pm_contracts_CONFLICTS.md" in names
