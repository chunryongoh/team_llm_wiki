import json

from team_llm_wiki.wiki_ingest.github_actions import (
    add_paths_from_payload,
    render_workflow_summary,
    workflow_dispatch_changed_paths,
    write_github_outputs,
)


def test_add_paths_from_payload_uses_report_declared_paths():
    payload = {"changed_paths": ["wiki/a.md", "wiki/b.md"], "status": "direct_commit"}

    assert add_paths_from_payload(payload) == ["wiki/a.md", "wiki/b.md"]


def test_workflow_dispatch_changed_paths_parses_multiline_input():
    env = {"INPUT_CHANGED_PATHS": "raw/users/a/p/manifest.yaml\nREADME.md\n"}

    assert workflow_dispatch_changed_paths(env) == ["raw/users/a/p/manifest.yaml", "README.md"]


def test_write_github_outputs_writes_multiline_safe_file(tmp_path):
    out = tmp_path / "outputs.txt"

    write_github_outputs(out, {"status": "bot_pr", "add_paths": "wiki/a.md\nwiki/b.md"})

    text = out.read_text(encoding="utf-8")
    assert "status=bot_pr" in text
    assert "add_paths<<EOF" in text


def test_render_summary_fallback_for_missing_ingest_output():
    assert "missing ingest output" in render_workflow_summary(None).lower()
    assert "direct_commit" in render_workflow_summary(json.dumps({"status": "direct_commit"}))
