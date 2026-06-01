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
    assert "peter-evans/create-pull-request@v8" in workflow
    assert "bot/llm-synthesis-" in workflow
    assert "[검토 필요] GPT-5.5 팀 위키 통합 정리" in workflow
    assert "## 사용한 LLM 모델" in workflow
