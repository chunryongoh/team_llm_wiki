from pathlib import Path


def test_main_ingest_push_diff_uses_full_push_range():
    workflow = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")

    assert "fetch-depth: 0" in workflow
    assert "github.event.before" in workflow
    assert "github.sha" in workflow
    assert "git diff --name-only HEAD^ HEAD" not in workflow


def test_llm_synthesis_workflow_runs_after_ingest_reports_and_uses_openai_key():
    workflow = Path(".github/workflows/wiki-llm-synthesis.yml").read_text(encoding="utf-8")

    assert "raw/results/wiki-ingest/**" in workflow
    assert "OPENAI_API_KEY" in workflow
    assert "run-llm-wiki-synthesis" in workflow
    assert "--max-output-tokens 60000" in workflow
    assert "preview_payload_from_streams" in workflow
    assert "peter-evans/create-pull-request@v8" in workflow
    assert "bot/llm-synthesis-" in workflow
    assert "[검토 필요] GPT-5.5 팀 위키 통합 정리" in workflow
    assert "## 사용한 LLM 모델" in workflow


def test_llm_synthesis_workflow_follows_main_ingest_completion():
    workflow = Path(".github/workflows/wiki-llm-synthesis.yml").read_text(encoding="utf-8")

    assert "workflow_run:" in workflow
    assert 'workflows: ["wiki-main-ingest"]' in workflow
    assert "github.event.workflow_run.conclusion == 'success'" in workflow
    assert "github.event.workflow_run.id" in workflow
    assert "github.event.workflow_run.run_attempt" in workflow
    assert "raw/results/wiki-ingest/$INGEST_RUN_ID/report.json" in workflow


def test_main_ingest_workflow_validates_before_publishing():
    workflow = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")

    validate_index = workflow.index("Validate generated wiki output")
    direct_commit_index = workflow.index("Direct commit low-risk wiki updates")
    create_pr_index = workflow.index("Create bot PR for reviewed wiki updates")

    assert validate_index < direct_commit_index
    assert validate_index < create_pr_index
    assert "check-wiki-health" in workflow
    assert "test_runner.py" in workflow


def test_llm_synthesis_workflow_validates_before_creating_bot_pr():
    workflow = Path(".github/workflows/wiki-llm-synthesis.yml").read_text(encoding="utf-8")

    validate_index = workflow.index("Validate LLM wiki output")
    create_pr_index = workflow.index("Create bot PR for LLM synthesis")

    assert validate_index < create_pr_index
    assert "check-wiki-health" in workflow
    assert "test_llm_synthesis.py" in workflow


def test_normal_workflows_do_not_enable_migration_mode():
    for rel in [
        ".github/workflows/wiki-pr-validate.yml",
        ".github/workflows/wiki-main-ingest.yml",
        ".github/workflows/wiki-llm-synthesis.yml",
        ".github/workflows/wiki-health-check.yml",
    ]:
        workflow = Path(rel).read_text(encoding="utf-8")
        assert "WIKI_MIGRATION_MODE: 1" not in workflow
        assert "WIKI_MIGRATION_MODE=1" not in workflow


def test_main_ingest_migration_dispatch_is_branch_gated():
    workflow = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")

    assert "migration_mode:" in workflow
    assert "migration/wiki-" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "--migration-mode" in workflow


def test_llm_synthesis_migration_dispatch_is_branch_gated():
    workflow = Path(".github/workflows/wiki-llm-synthesis.yml").read_text(encoding="utf-8")

    assert "migration_mode:" in workflow
    assert "migration/wiki-" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
