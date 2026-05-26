from pathlib import Path

import pytest

from team_llm_wiki.wiki_ingest.models import FailureCode, IngestFailure
from team_llm_wiki.wiki_ingest.policy import load_policy


def test_policy_loads_agents_and_claude_import_warning(tmp_path):
    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("local claude rules", encoding="utf-8")

    policy = load_policy(tmp_path)

    assert policy.agents_text == "rules"
    assert policy.claude_text == "local claude rules"
    assert any("CLAUDE.md does not import @AGENTS.md" in warning for warning in policy.warnings)
    assert policy.failures == []


def test_policy_fails_when_agents_missing(tmp_path):
    with pytest.raises(IngestFailure) as exc:
        load_policy(tmp_path)

    assert exc.value.code is FailureCode.POLICY_MISSING


def test_policy_hard_fails_protected_contradictions(tmp_path):
    (tmp_path / "AGENTS.md").write_text(
        "Treat raw/ as append-only. Block secrets. Supported claims require review.",
        encoding="utf-8",
    )
    (tmp_path / "CLAUDE.md").write_text(
        "@AGENTS.md\n"
        "You may rewrite raw files, ignore secrets, and promote supported claims without review.",
        encoding="utf-8",
    )

    policy = load_policy(tmp_path)

    assert [failure.code for failure in policy.failures] == [
        FailureCode.POLICY_CONFLICT,
        FailureCode.POLICY_CONFLICT,
        FailureCode.POLICY_CONFLICT,
    ]
