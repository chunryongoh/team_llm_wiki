from team_llm_wiki.wiki_ingest.brief import generate_daily_brief, generate_weekly_brief


def test_generate_daily_brief_writes_dated_brief_and_latest_pointer(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "log.md").write_text(
        "# Log\n\n"
        "## [2026-05-26] ingest | old-packet\n\n"
        "- target: `wiki/sources/old-packet.md`\n\n"
        "## [2026-05-27] ingest | pkt-1\n\n"
        "- target: `wiki/sources/pkt-1.md`\n"
        "- run: `run-1`\n\n"
        "## [2026-05-27] run | benchmark-a\n\n"
        "- target: `wiki/experiments/benchmark-a.md`\n\n"
        "## [2026-05-28] ingest | future-packet\n\n"
        "- target: `wiki/sources/future-packet.md`\n",
        encoding="utf-8",
    )

    generated = generate_daily_brief(tmp_path, date="2026-05-27")

    assert generated == ["wiki/briefs/2026-05-27-daily.md", "wiki/briefs/latest.md"]
    dated = wiki / "briefs" / "2026-05-27-daily.md"
    latest = wiki / "briefs" / "latest.md"
    assert dated.exists()
    assert latest.exists()
    assert latest.read_text(encoding="utf-8") == "[[2026-05-27-daily]]\n"

    text = dated.read_text(encoding="utf-8")
    assert "date: 2026-05-27" in text
    assert "type: daily-brief" in text
    assert "# Daily Brief - 2026-05-27" in text
    assert "## New packets ingested" in text
    assert "## Score movement and target movement" in text
    assert "## Reusable features discovered" in text
    assert "## Failed ideas worth stopping" in text
    assert "## Leakage or validation warnings" in text
    assert "## Unresolved reviewer questions" in text
    assert "## Recommended next 3 actions" in text
    assert "[[latest-context]]" in text
    assert "pkt-1" in text
    assert "benchmark-a" in text
    assert "old-packet" not in text
    assert "future-packet" not in text


def test_generate_weekly_brief_writes_weekly_and_stale_claim_reports(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "log.md").write_text(
        "# Log\n\n"
        "## [2026-05-18] ingest | previous-week\n\n"
        "- target: `wiki/sources/previous-week.md`\n\n"
        "## [2026-05-25] ingest | pkt-1\n\n"
        "- target: `wiki/sources/pkt-1.md`\n\n"
        "## [2026-05-27] run | benchmark-a\n\n"
        "- target: `wiki/experiments/benchmark-a.md`\n\n",
        encoding="utf-8",
    )
    (wiki / "questions").mkdir()
    (wiki / "questions" / "old-hypothesis.md").write_text(
        "---\n"
        "claim_status: tentative\n"
        "date: 2026-05-01\n"
        "---\n"
        "# Old hypothesis\n",
        encoding="utf-8",
    )
    (wiki / "models").mkdir()
    (wiki / "models" / "superseded.md").write_text(
        "---\n"
        "claim_status: superseded\n"
        "date: 2026-05-20\n"
        "---\n"
        "# Superseded claim\n",
        encoding="utf-8",
    )
    (wiki / "features").mkdir()
    (wiki / "features" / "conflict-a.md").write_text("# A\n\n- supported: Same claim text\n", encoding="utf-8")
    (wiki / "features" / "conflict-b.md").write_text("# B\n\n- disputed: Same claim text\n", encoding="utf-8")

    generated = generate_weekly_brief(tmp_path, date="2026-05-27")

    assert generated == [
        "wiki/briefs/2026-W22-weekly.md",
        "wiki/briefs/2026-05-27-stale-claims.md",
        "wiki/briefs/latest.md",
    ]
    weekly = (wiki / "briefs" / "2026-W22-weekly.md").read_text(encoding="utf-8")
    stale = (wiki / "briefs" / "2026-05-27-stale-claims.md").read_text(encoding="utf-8")
    latest = (wiki / "briefs" / "latest.md").read_text(encoding="utf-8")
    assert "type: weekly-brief" in weekly
    assert "# Weekly Brief - 2026-W22" in weekly
    assert "## Leaderboard and maintained local line" in weekly
    assert "## Target deficit analysis" in weekly
    assert "## Best reusable preprocessing policies" in weekly
    assert "## Best reusable feature families" in weekly
    assert "## Model family comparison" in weekly
    assert "## Repeated failure modes" in weekly
    assert "## Decisions to accept or supersede" in weekly
    assert "## Next sprint backlog" in weekly
    assert "pkt-1" in weekly
    assert "benchmark-a" in weekly
    assert "previous-week" not in weekly
    assert "## Contradiction scan" in weekly
    assert "wiki/models/superseded.md" in weekly
    assert "Same claim text" in weekly
    assert "## Stale tentative claims" in weekly
    assert "wiki/questions/old-hypothesis.md" in weekly
    assert "type: stale-claim-report" in stale
    assert "wiki/questions/old-hypothesis.md" in stale
    assert latest == "[[2026-W22-weekly]]\n"
