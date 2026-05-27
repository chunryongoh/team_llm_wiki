import json

from team_llm_wiki.wiki_ingest.health import check_wiki_health


def seed_clean(root):
    (root / "wiki").mkdir()
    (root / "wiki" / "index.md").write_text(
        "# Index\n\n<!-- wiki-ingest:index:start -->\n- [Overview](overview.md)\n<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )
    (root / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (root / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "wiki" / "latest-context.md").write_text(
        "[[index]] [[overview]] [[log]]\n"
        "<!-- wiki-ingest:latest:start -->\n"
        "<!-- wiki-ingest:latest:end -->\n",
        encoding="utf-8",
    )


def test_health_clean_report(tmp_path):
    seed_clean(tmp_path)

    report = check_wiki_health(tmp_path)

    assert report.ok is True
    assert report.errors == []


def test_health_detects_broken_links_unbalanced_block_and_incomplete_latest_context(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("<!-- wiki-ingest:index:start -->\n", encoding="utf-8")
    (tmp_path / "wiki" / "latest-context.md").write_text("[[index]]\n[[missing]]\n", encoding="utf-8")

    report = check_wiki_health(tmp_path)

    assert report.ok is False
    assert any(error.code == "unbalanced_generated_block" for error in report.errors)
    assert any(error.code == "missing_required_latest_link" for error in report.errors)
    assert any(error.code == "broken_wiki_link" for error in report.errors)


def test_health_detects_unbalanced_latest_context_generated_block(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "latest-context.md").write_text(
        "[[index]] [[overview]] [[log]]\n<!-- wiki-ingest:latest:start -->\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert any(error.code == "unbalanced_generated_block" for error in report.errors)


def test_health_detects_wiki_link_escape(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "overview.md").write_text("[[../AGENTS]]\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")

    report = check_wiki_health(tmp_path)

    assert any(error.code == "path_escape" for error in report.errors)


def test_health_writes_json_report(tmp_path):
    seed_clean(tmp_path)
    report_path = tmp_path / "health.json"

    report = check_wiki_health(tmp_path, report_path=report_path)

    assert report.ok is True
    assert json.loads(report_path.read_text(encoding="utf-8"))["ok"] is True


def test_health_detects_orphan_wiki_page(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "features").mkdir()
    (tmp_path / "wiki" / "features" / "unindexed.md").write_text("# Unindexed\n", encoding="utf-8")

    report = check_wiki_health(tmp_path)

    assert any(error.code == "orphan_wiki_page" for error in report.errors)


def test_health_accepts_indexed_wiki_link_without_md(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "features").mkdir()
    (tmp_path / "wiki" / "features" / "indexed.md").write_text("# Indexed\n", encoding="utf-8")
    (tmp_path / "wiki" / "index.md").write_text(
        "# Index\n\n"
        "<!-- wiki-ingest:index:start -->\n"
        "- [[features/indexed]]\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert not any(error.code == "orphan_wiki_page" for error in report.errors)


def test_health_excludes_section_readme_landing_page_from_orphan_checks(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "performance").mkdir()
    (tmp_path / "wiki" / "performance" / "README.md").write_text("# Performance\n", encoding="utf-8")

    report = check_wiki_health(tmp_path)

    assert not any(error.code == "orphan_wiki_page" for error in report.errors)


def test_health_detects_supported_claim_missing_raw(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "models").mkdir()
    (tmp_path / "wiki" / "models" / "claim.md").write_text(
        "---\n"
        "claim_status: supported\n"
        "date: 2026-05-20\n"
        "---\n"
        "# Claim\n\n"
        "이 결론은 지원됨 상태다.\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki" / "index.md").write_text(
        "# Index\n\n"
        "<!-- wiki-ingest:index:start -->\n"
        "- [Claim](models/claim.md)\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert any(error.code == "supported_claim_missing_raw" for error in report.errors)


def test_health_detects_stale_tentative_claim(tmp_path, monkeypatch):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "questions").mkdir()
    (tmp_path / "wiki" / "questions" / "old.md").write_text(
        "---\n"
        "claim_status: tentative\n"
        "date: 2026-05-01\n"
        "---\n"
        "# Old hypothesis\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki" / "index.md").write_text(
        "# Index\n\n"
        "<!-- wiki-ingest:index:start -->\n"
        "- [[questions/old]]\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )

    class FrozenDate:
        @classmethod
        def today(cls):
            return cls(2026, 5, 27)

        @classmethod
        def fromisoformat(cls, value):
            from datetime import date

            return date.fromisoformat(value)

        def __new__(cls, *args):
            from datetime import date

            return date(*args)

    monkeypatch.setattr("team_llm_wiki.wiki_ingest.health.date", FrozenDate, raising=False)

    report = check_wiki_health(tmp_path)

    assert any(error.code == "stale_tentative_claim" for error in report.errors)


def test_health_detects_performance_metric_unverified(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "performance").mkdir(exist_ok=True)
    (tmp_path / "wiki" / "performance" / "leaderboard.md").write_text(
        "---\n"
        "type: performance\n"
        "date: 2026-05-20\n"
        "---\n"
        "# Leaderboard\n\n"
        "## Metrics\n\n"
        "- accuracy: 0.91\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki" / "index.md").write_text(
        "# Index\n\n"
        "<!-- wiki-ingest:index:start -->\n"
        "- [Leaderboard](performance/leaderboard.md)\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert any(error.code == "performance_metric_unverified" for error in report.errors)


def test_health_detects_unverified_metrics_on_indexed_non_performance_page(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "models").mkdir()
    (tmp_path / "wiki" / "models" / "candidate.md").write_text(
        "---\n"
        "type: model\n"
        "date: 2026-05-20\n"
        "---\n"
        "# Candidate model\n\n"
        "## Metrics\n\n"
        "- accuracy: 0.91\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki" / "index.md").write_text(
        "# Index\n\n"
        "<!-- wiki-ingest:index:start -->\n"
        "- [Candidate](models/candidate.md)\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert any(error.code == "performance_metric_unverified" for error in report.errors)


def test_health_detects_empty_metrics_to_verify_as_unverified(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "performance").mkdir(exist_ok=True)
    (tmp_path / "wiki" / "performance" / "leaderboard.md").write_text(
        "---\n"
        "type: performance\n"
        "date: 2026-05-20\n"
        "metrics_to_verify: []\n"
        "---\n"
        "# Leaderboard\n\n"
        "## Metrics\n\n"
        "- accuracy: 0.91\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki" / "index.md").write_text(
        "# Index\n\n"
        "<!-- wiki-ingest:index:start -->\n"
        "- [Leaderboard](performance/leaderboard.md)\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert any(error.code == "performance_metric_unverified" for error in report.errors)
