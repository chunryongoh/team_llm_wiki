from pathlib import Path

import yaml


def load_workflow(path: str) -> dict:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if True in payload and "on" not in payload:
        payload["on"] = payload.pop(True)
    return payload


def steps_by_name(path: str, job: str) -> dict[str, dict]:
    workflow = load_workflow(path)
    return {
        step["name"]: step
        for step in workflow["jobs"][job]["steps"]
        if isinstance(step, dict) and "name" in step
    }


def test_main_ingest_push_diff_uses_full_push_range():
    workflow = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")

    assert "fetch-depth: 0" in workflow
    assert "github.event.before" in workflow
    assert "github.sha" in workflow
    assert "git diff --name-only HEAD^ HEAD" not in workflow


def test_llm_synthesis_workflow_runs_after_ingest_reports_and_uses_openai_key():
    workflow = Path(".github/workflows/wiki-llm-synthesis.yml").read_text(encoding="utf-8")
    parsed = load_workflow(".github/workflows/wiki-llm-synthesis.yml")

    assert "raw/results/wiki-ingest/**" in workflow
    assert "OPENAI_API_KEY" in workflow
    assert parsed["permissions"]["models"] == "read"
    assert "GITHUB_TOKEN: ${{ github.token }}" in workflow
    assert "GITHUB_MODELS_MODEL" in workflow
    assert "run-llm-wiki-synthesis" in workflow
    assert "--max-output-tokens 60000" in workflow
    assert "preview_payload_from_streams" in workflow
    assert "peter-evans/create-pull-request@v8" in workflow
    assert "bot/llm-synthesis-" in workflow
    assert "[검토 필요] 팀 위키 통합 정리" in workflow
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


def test_scheduled_health_warns_on_stale_tentative_claims_only():
    workflow = Path(".github/workflows/wiki-health-check.yml").read_text(encoding="utf-8")
    main_ingest = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")
    llm_synthesis = Path(".github/workflows/wiki-llm-synthesis.yml").read_text(encoding="utf-8")

    assert "--stale-tentative-as-warning" in workflow
    assert "--stale-tentative-as-warning" not in main_ingest
    assert "--stale-tentative-as-warning" not in llm_synthesis


def test_main_ingest_migration_dispatch_is_branch_gated():
    workflow = load_workflow(".github/workflows/wiki-main-ingest.yml")
    steps = steps_by_name(".github/workflows/wiki-main-ingest.yml", "ingest")

    migration_input = workflow["on"]["workflow_dispatch"]["inputs"]["migration_mode"]
    assert migration_input["type"] == "boolean"
    assert migration_input["default"] is False

    route_migration = steps["Run route migration when explicitly dispatched"]
    assert route_migration["if"] == (
        "steps.skip.outputs.skip != 'true' && github.event_name == 'workflow_dispatch' && inputs.migration_mode"
    )
    assert "startsWith(github.ref_name, 'migration/wiki-')" in route_migration["env"]["WIKI_MIGRATION_MODE"]
    assert "exit 1" in route_migration["run"]
    assert "--migration-mode" in route_migration["run"]

    normal_exclusion = "github.event_name != 'workflow_dispatch' || inputs.migration_mode != true"
    assert normal_exclusion in steps["Collect changed paths"]["if"]
    assert normal_exclusion in steps["Run wiki ingest"]["if"]
    assert normal_exclusion in steps["Upload wiki ingest report"]["if"]
    assert "workflow_dispatch_changed_paths" in steps["Collect changed paths"]["run"]


def test_llm_synthesis_migration_dispatch_is_branch_gated():
    workflow_path = ".github/workflows/wiki-llm-synthesis.yml"
    workflow_text = Path(workflow_path).read_text(encoding="utf-8")
    workflow = load_workflow(workflow_path)
    steps = steps_by_name(workflow_path, "synthesize")

    migration_input = workflow["on"]["workflow_dispatch"]["inputs"]["migration_mode"]
    assert migration_input["type"] == "boolean"
    assert migration_input["default"] is False

    gate = steps["Check migration dispatch gate"]
    assert gate["if"] == "github.event_name == 'workflow_dispatch' && inputs.migration_mode"
    assert "startsWith(github.ref_name, 'migration/wiki-')" in gate["env"]["WIKI_MIGRATION_MODE"]
    assert "exit 1" in gate["run"]
    assert "run-wiki-route-migration" not in workflow_text
    assert "--migration-mode" not in workflow_text
