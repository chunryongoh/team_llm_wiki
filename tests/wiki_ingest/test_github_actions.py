import json

from team_llm_wiki.wiki_ingest.github_actions import (
    add_paths_from_payload,
    render_pr_comment,
    safe_add_paths_file_from_payload,
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


def test_workflow_dispatch_empty_input_falls_back_to_raw_user_manifests(tmp_path):
    manifest = tmp_path / "raw" / "users" / "alice" / "pkt-1" / "manifest.yaml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("id: pkt-1\npacket_type: reference\ntitle: Packet\n", encoding="utf-8")
    ignored = tmp_path / "raw" / "shared" / "template" / "manifest.yaml"
    ignored.parent.mkdir(parents=True)
    ignored.write_text("id: ignored\npacket_type: reference\ntitle: Ignored\n", encoding="utf-8")

    assert workflow_dispatch_changed_paths({"INPUT_CHANGED_PATHS": ""}, repo_root=tmp_path) == [
        "raw/users/alice/pkt-1/manifest.yaml"
    ]


def test_write_github_outputs_writes_multiline_safe_file(tmp_path):
    out = tmp_path / "outputs.txt"

    write_github_outputs(out, {"status": "bot_pr", "add_paths": "wiki/a.md\nwiki/b.md"})

    text = out.read_text(encoding="utf-8")
    assert "status=bot_pr" in text
    assert "add_paths<<EOF" in text


def test_safe_add_paths_file_from_payload_writes_newline_file(tmp_path):
    path = tmp_path / "add-paths.txt"

    safe_add_paths_file_from_payload({"generated_paths": ["wiki/a.md"], "report_path": "raw/results/report.json"}, path)

    assert path.read_text(encoding="utf-8").splitlines() == ["wiki/a.md", "raw/results/report.json"]


def test_render_summary_fallback_for_missing_ingest_output():
    assert "missing ingest output" in render_workflow_summary(None).lower()
    assert "direct_commit" in render_workflow_summary(json.dumps({"status": "direct_commit"}))


def test_render_summary_includes_report_and_failure_codes():
    summary = render_workflow_summary(
        json.dumps(
            {
                "status": "hard_fail",
                "report_path": "raw/results/wiki-ingest/1/report.json",
                "failures": [{"code": "invalid_manifest", "message": "missing title"}],
            }
        )
    )

    assert "raw/results/wiki-ingest/1/report.json" in summary
    assert "invalid_manifest" in summary
    assert "missing title" in summary


def test_render_pr_comment_includes_preview_details():
    comment = render_pr_comment(
        {
            "status": "hard_fail",
            "packet_roots": ["raw/users/alice/pkt-1"],
            "generated_paths": ["wiki/sources/pkt-1.md"],
            "failures": [{"code": "invalid_manifest", "message": "missing title"}],
        }
    )

    assert "Wiki ingest preview" in comment
    assert "raw/users/alice/pkt-1" in comment
    assert "wiki/sources/pkt-1.md" in comment
    assert "invalid_manifest" in comment
