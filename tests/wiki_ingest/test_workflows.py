from pathlib import Path


def test_main_ingest_push_diff_uses_full_push_range():
    workflow = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")

    assert "fetch-depth: 0" in workflow
    assert "github.event.before" in workflow
    assert "github.sha" in workflow
    assert "git diff --name-only HEAD^ HEAD" not in workflow
