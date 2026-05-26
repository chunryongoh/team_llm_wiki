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
    (root / "wiki" / "latest-context.md").write_text("[[index]] [[overview]] [[log]]\n", encoding="utf-8")


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


def test_health_writes_json_report(tmp_path):
    seed_clean(tmp_path)
    report_path = tmp_path / "health.json"

    report = check_wiki_health(tmp_path, report_path=report_path)

    assert report.ok is True
    assert json.loads(report_path.read_text(encoding="utf-8"))["ok"] is True
