from team_llm_wiki.wiki_ingest.brief import generate_daily_brief


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
    assert latest.read_text(encoding="utf-8") == dated.read_text(encoding="utf-8")

    text = dated.read_text(encoding="utf-8")
    assert "date: 2026-05-27" in text
    assert "type: daily-brief" in text
    assert "# Daily Brief - 2026-05-27" in text
    assert "## New packets ingested" in text
    assert "[[latest-context]]" in text
    assert "pkt-1" in text
    assert "benchmark-a" in text
    assert "old-packet" not in text
    assert "future-packet" not in text
