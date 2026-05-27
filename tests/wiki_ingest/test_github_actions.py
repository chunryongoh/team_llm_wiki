import json
from pathlib import Path

from team_llm_wiki.wiki_ingest.github_actions import (
    add_paths_from_payload,
    preview_payload_from_streams,
    render_bot_pr_body,
    render_pr_comment,
    safe_add_paths_file_from_payload,
    render_workflow_summary,
    should_skip_wiki_ingest,
    workflow_dispatch_changed_paths,
    write_github_outputs,
)


def test_add_paths_from_payload_uses_report_declared_paths():
    payload = {"changed_paths": ["wiki/a.md", "wiki/b.md"], "status": "direct_commit"}

    assert add_paths_from_payload(payload) == ["wiki/a.md", "wiki/b.md"]


def test_should_skip_wiki_ingest_for_wiki_bot_direct_commit():
    assert should_skip_wiki_ingest(
        "github-actions[bot]",
        commit_message="[wiki-bot] ingest wiki packets",
    )


def test_should_skip_wiki_ingest_for_wiki_bot_pr_title():
    assert should_skip_wiki_ingest("octocat", pr_title="[wiki-bot] ingest wiki packets")


def test_should_skip_wiki_ingest_allows_normal_human_and_raw_packet_changes():
    assert not should_skip_wiki_ingest("alice", commit_message="add raw packet")
    assert not should_skip_wiki_ingest("github-actions[bot]", commit_message="chore: unrelated automation")
    assert not should_skip_wiki_ingest("alice", pr_title="add experiment packet")


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


def test_render_bot_pr_body_includes_required_review_sections():
    body = render_bot_pr_body(
        {
            "packet_roots": ["raw/users/alice/pkt-1"],
            "generated_paths": ["wiki/performance/pkt-1.md", "automation/.cache/compiled/pkt-1.json"],
            "claim_statuses": [{"packet": "pkt-1", "status": "supported"}],
            "metric_changes": [{"packet": "pkt-1", "metric": "accuracy", "reported_value": 0.82}],
            "warnings": ["possible leakage warning"],
        }
    )

    assert "## Changed raw packet ids" in body
    assert "raw/users/alice/pkt-1" in body
    assert "## Affected wiki pages" in body
    assert "wiki/performance/pkt-1.md" in body
    assert "## Claim changes" in body
    assert "`pkt-1` `supported`" in body
    assert "## Metric changes" in body
    assert "accuracy" in body
    assert "## Leakage/security warnings" in body
    assert "possible leakage warning" in body
    assert "## Reviewer checklist" in body


def test_render_pr_comment_includes_preview_details():
    comment = render_pr_comment(
        {
            "status": "hard_fail",
            "packet_roots": ["raw/users/alice/pkt-1"],
            "packets": [
                {
                    "id": "pkt-1",
                    "type": "performance",
                    "risk_tier": "bot_pr",
                    "risk_reasons": ["performance evidence requires review"],
                }
            ],
            "generated_paths": ["wiki/sources/pkt-1.md"],
            "claim_statuses": [{"packet": "pkt-1", "status": "tentative"}],
            "failures": [{"code": "invalid_manifest", "message": "missing title"}],
            "warnings": ["review calibration evidence"],
        }
    )

    assert "Wiki ingest preview" in comment
    assert "raw/users/alice/pkt-1" in comment
    assert "wiki/sources/pkt-1.md" in comment
    assert "invalid_manifest" in comment
    assert "### Detected packet types" in comment
    assert "`pkt-1` performance" in comment
    assert "### Affected wiki pages" in comment
    assert "### Proposed claim statuses" in comment
    assert "`pkt-1` `tentative`" in comment
    assert "### Missing evidence" in comment
    assert "missing title" in comment
    assert "### Expected PR review questions" in comment
    assert "review calibration evidence" in comment


def test_preview_payload_from_streams_preserves_stderr_only_error():
    payload = preview_payload_from_streams(
        "",
        '{"error": {"code": "invalid_manifest", "message": "bad manifest"}}',
        run_id="preview-1",
    )

    assert payload == {
        "status": "hard_fail",
        "run_id": "preview-1",
        "failures": [{"code": "invalid_manifest", "message": "bad manifest"}],
    }
    comment = render_pr_comment(payload)
    assert "hard_fail" in comment
    assert "invalid_manifest" in comment
    assert "bad manifest" in comment


def test_render_pr_comment_preserves_failures_with_many_long_paths():
    long_paths = [f"wiki/sources/{'very-long-segment-' * 200}{idx}.md" for idx in range(200)]

    comment = render_pr_comment(
        {
            "status": "hard_fail",
            "packet_roots": long_paths,
            "generated_paths": long_paths,
            "failures": [{"code": "invalid_manifest", "message": "missing title"}],
        }
    )

    assert "### Failures" in comment
    assert "invalid_manifest" in comment
    assert "missing title" in comment


def test_health_workflow_copies_latest_after_weekly_brief_generation():
    workflow = Path(".github/workflows/wiki-health-check.yml").read_text(encoding="utf-8")

    weekly_index = workflow.index("generate-wiki-weekly-brief")
    latest_copy_index = workflow.rindex("cp wiki/briefs/latest.md")

    assert latest_copy_index > weekly_index


def test_main_ingest_workflow_uses_review_required_pr_title_and_body():
    workflow = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")

    assert 'title: "[wiki-bot][review-required] ingest wiki packets"' in workflow
    assert "body: ${{ steps.ingest.outputs.pr_body }}" in workflow
