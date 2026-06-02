import json
from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest import llm_synthesis
from team_llm_wiki.wiki_ingest.llm_synthesis import OpenAIResponsesClient
from team_llm_wiki.wiki_ingest.models import FailureCode, IngestFailure
from team_llm_wiki.wiki_ingest.llm_synthesis import run_llm_wiki_synthesis


class FakeClient:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def synthesize(self, *, model, reasoning_effort, prompt):
        self.calls.append({"model": model, "reasoning_effort": reasoning_effort, "prompt": prompt})
        return self.payload


def seed_repo(root: Path):
    (root / "AGENTS.md").write_text(
        "# Rules\n\n- Treat raw/ as append-only.\n- Dataset pages must be synthesized entity pages.\n",
        encoding="utf-8",
    )
    (root / "CLAUDE.md").write_text("@AGENTS.md\nRead latest context first.\n", encoding="utf-8")
    (root / "wiki" / "datasets").mkdir(parents=True)
    (root / "wiki" / "team").mkdir(parents=True)
    (root / "wiki" / "team" / "ml-ai-hackathon-entity-model.md").write_text(
        "# ML/AI Hackathon Entity Model\n", encoding="utf-8"
    )
    (root / "wiki" / "team" / "packet-quality-standard.md").write_text(
        "# Packet Quality Standard\n", encoding="utf-8"
    )
    (root / "wiki" / "index.md").write_text(
        "# Index\n\n<!-- wiki-ingest:index:start -->\n"
        "- [Sleep Lifelog 2024](datasets/sleep-lifelog-2024.md) - `dataset`\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )
    (root / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (root / "wiki" / "log.md").write_text(
        "# Log\n\n## [2026-05-01] seed | baseline\n\n- Existing log entry.\n",
        encoding="utf-8",
    )
    (root / "wiki" / "latest-context.md").write_text(
        "# Latest Context\n\n[[index]] [[overview]] [[log]]\n\n"
        "<!-- wiki-ingest:latest:start -->\n"
        "### seed | dataset\n\n- link: [[datasets/sleep-lifelog-2024]]\n"
        "<!-- wiki-ingest:latest:end -->\n",
        encoding="utf-8",
    )
    (root / "wiki" / "datasets" / "sleep-lifelog-2024.md").write_text(
        "# Old Dataset Page\n\nOld deterministic summary.\n",
        encoding="utf-8",
    )


def seed_dataset_packet(root: Path) -> Path:
    packet_root = root / "raw" / "users" / "alice" / "datasets" / "2026-05-29-sleep-lifelog-2024"
    packet_root.mkdir(parents=True)
    manifest = {
        "id": "2026-05-29-sleep-lifelog-2024",
        "packet_type": "dataset",
        "title": "Sleep Lifelog 2024 Dataset Definition",
        "date": "2026-05-29",
        "owner": "alice",
        "status": "submitted",
        "task": "dataset-definition",
        "dataset": {"name": "sleep-lifelog-2024", "version": "v0"},
        "split": {"name": "groupkfold-subject-3fold-oof"},
        "model": {"family": "not-applicable"},
        "claim_boundary": "dataset_definition_not_metric_claim",
        "claim_status": "tentative",
        "summary": "Dataset summary.",
        "raw_paths": {"dataset": "dataset.yaml"},
        "intended_wiki_targets": ["wiki/datasets/2026-05-29-sleep-lifelog-2024.md"],
    }
    (packet_root / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    (packet_root / "dataset.yaml").write_text(
        "name: sleep-lifelog-2024\nmodalities: [smartphone:mActivity]\nclaim_status: tentative\n",
        encoding="utf-8",
    )
    (packet_root / "packet.md").write_text(
        "# Sleep Lifelog 2024 Dataset Definition\n\nThis packet explains leakage risks.\n",
        encoding="utf-8",
    )
    return packet_root


def seed_benchmark_packet(root: Path) -> Path:
    packet_root = root / "raw" / "users" / "alice" / "benchmarks" / "2026-05-29-sleep-health-hackathon-v0"
    packet_root.mkdir(parents=True)
    manifest = {
        "id": "2026-05-29-sleep-health-hackathon-v0",
        "packet_type": "benchmark",
        "title": "Sleep Health Hackathon Benchmark v0 Definition",
        "date": "2026-05-29",
        "owner": "alice",
        "status": "submitted",
        "task": "benchmark-definition",
        "dataset": {"name": "sleep-lifelog-2024", "version": "v0"},
        "split": {"name": "groupkfold-subject-3fold-oof", "group_key": "subject_id"},
        "model": {"family": "not-applicable"},
        "claim_boundary": "benchmark_definition_not_metric_claim",
        "claim_status": "tentative",
        "summary": "Benchmark summary.",
        "raw_paths": {"benchmark": "benchmark.yaml"},
        "intended_wiki_targets": ["wiki/benchmarks/2026-05-29-sleep-health-hackathon-v0.md"],
    }
    (packet_root / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    (packet_root / "benchmark.yaml").write_text(
        "name: sleep-health-hackathon-v0\n"
        "dataset_ref: sleep-lifelog-2024\n"
        "primary_metric:\n"
        "  name: grouped_macro_logloss\n",
        encoding="utf-8",
    )
    (packet_root / "packet.md").write_text(
        "# Sleep Health Hackathon Benchmark v0 Definition\n\nThis packet defines Track A and Track B.\n",
        encoding="utf-8",
    )
    return packet_root


def integration_pages() -> list[dict[str, str]]:
    return [
        {
            "path": "wiki/datasets/sleep-lifelog-2024.md",
            "content": "# Sleep Lifelog 2024\n\nDataset entity synthesis.\n",
        },
        {
            "path": "wiki/benchmarks/sleep-health-hackathon-v0.md",
            "content": "# Sleep Health Hackathon v0\n\nBenchmark entity synthesis.\n",
        },
        {
            "path": "wiki/features/sleep-lifelog-feature-landscape.md",
            "content": "# Sleep Lifelog Feature Landscape\n\nFeature implications from modalities.\n",
        },
        {
            "path": "wiki/decisions/sleep-lifelog-evaluation-protocol.md",
            "content": "# Sleep Lifelog Evaluation Protocol\n\nTrack A is the local comparison default.\n",
        },
        {
            "path": "wiki/questions/sleep-lifelog-open-questions.md",
            "content": "# Sleep Lifelog Open Questions\n\n- How should Track B be handled?\n",
        },
        {
            "path": "wiki/claims/current-supported-claims.md",
            "content": "# Current Supported Claims\n\n- No leaderboard claim promoted.\n",
        },
        {
            "path": "wiki/submissions/dacon-leaderboard-history.md",
            "content": "# DACON Leaderboard History\n\n- No verified submission in this packet.\n",
        },
        {
            "path": "wiki/preprocessing/canonical-split-and-leakage-policy.md",
            "content": "# Canonical Split And Leakage Policy\n\n- Keep local OOF and leaderboard evidence separate.\n",
        },
        {
            "path": "wiki/reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md",
            "content": "# Sleep Lifelog Benchmark Synthesis\n\nIntegrated report.\n",
        },
        {
            "path": "wiki/overview.md",
            "content": "# Team LLM Wiki Overview\n\nCurrent focus: sleep lifelog benchmark integration.\n",
        },
        {
            "path": "wiki/latest-context.md",
            "content": "# Latest Context\n\n[[index]] [[overview]] [[log]]\n\n## Current Best\n\n- Current best remains claim-boundary dependent.\n\n## Active Risks\n\n- Local OOF and leaderboard evidence remain separate.\n\n## Next Actions\n\n- Review benchmark integration.\n\n<!-- wiki-ingest:latest:start -->\n### llm integration | sleep lifelog\n\n- link: [[reports/2026-05-29-sleep-lifelog-benchmark-synthesis]]\n<!-- wiki-ingest:latest:end -->\n",
        },
        {
            "path": "wiki/index.md",
            "content": "# Index\n\n<!-- wiki-ingest:index:start -->\n- [Sleep Health Hackathon v0](benchmarks/sleep-health-hackathon-v0.md) - `benchmark`\n- [Sleep Lifelog 2024](datasets/sleep-lifelog-2024.md) - `dataset`\n- [Sleep Lifelog Feature Landscape](features/sleep-lifelog-feature-landscape.md) - `feature-synthesis`\n- [Sleep Lifelog Evaluation Protocol](decisions/sleep-lifelog-evaluation-protocol.md) - `decision`\n- [Sleep Lifelog Open Questions](questions/sleep-lifelog-open-questions.md) - `questions`\n- [Sleep Lifelog Benchmark Synthesis](reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md) - `report`\n<!-- wiki-ingest:index:end -->\n",
        },
        {
            "path": "wiki/log.md",
            "content": "# Log\n\n## [2026-05-01] seed | baseline\n\n- Existing log entry.\n\n## [2026-05-29] llm-synthesis | sleep-lifelog-benchmark\n\n- Integrated dataset and benchmark packets into the wiki graph.\n",
        },
    ]


def single_dataset_integration_pages() -> list[dict[str, str]]:
    pages = [
        {
            "path": "wiki/datasets/sleep-lifelog-2024.md",
            "content": "# Sleep Lifelog 2024\n\nLLM synthesized page.\n\n- claim_status: `tentative`\n",
        },
        {
            "path": "wiki/features/sleep-lifelog-feature-landscape.md",
            "content": "# Sleep Lifelog Feature Landscape\n\nDataset feature implications.\n",
        },
        {
            "path": "wiki/decisions/sleep-lifelog-evaluation-protocol.md",
            "content": "# Sleep Lifelog Evaluation Protocol\n\nEvaluation protocol notes.\n",
        },
        {
            "path": "wiki/questions/sleep-lifelog-open-questions.md",
            "content": "# Sleep Lifelog Open Questions\n\n- Which modalities need schema expansion?\n",
        },
        {
            "path": "wiki/reports/2026-05-29-sleep-lifelog-packet-synthesis.md",
            "content": "# Sleep Lifelog Packet Synthesis\n\nDataset packet integration report.\n",
        },
        {
            "path": "wiki/claims/current-supported-claims.md",
            "content": "# Current Supported Claims\n\n- No supported claim changed.\n",
        },
        {
            "path": "wiki/submissions/dacon-leaderboard-history.md",
            "content": "# DACON Leaderboard History\n\n- No verified submission in this packet.\n",
        },
        {
            "path": "wiki/preprocessing/canonical-split-and-leakage-policy.md",
            "content": "# Canonical Split And Leakage Policy\n\n- GroupKFold split policy remains local OOF only.\n",
        },
        {
            "path": "wiki/overview.md",
            "content": "# Team LLM Wiki Overview\n\nCurrent focus: sleep lifelog dataset integration.\n",
        },
        {
            "path": "wiki/latest-context.md",
            "content": "# Latest Context\n\n[[index]] [[overview]] [[log]]\n\n## Current Best\n\n- Current best unchanged.\n\n## Active Risks\n\n- Dataset claims remain tentative.\n\n## Next Actions\n\n- Review dataset evidence gaps.\n\n<!-- wiki-ingest:latest:start -->\n### llm integration | sleep lifelog\n\n- link: [[reports/2026-05-29-sleep-lifelog-packet-synthesis]]\n<!-- wiki-ingest:latest:end -->\n",
        },
        {
            "path": "wiki/index.md",
            "content": "# Index\n\n<!-- wiki-ingest:index:start -->\n- [Sleep Lifelog 2024](datasets/sleep-lifelog-2024.md) - `dataset`\n- [Sleep Lifelog Feature Landscape](features/sleep-lifelog-feature-landscape.md) - `feature-synthesis`\n- [Sleep Lifelog Evaluation Protocol](decisions/sleep-lifelog-evaluation-protocol.md) - `decision`\n- [Sleep Lifelog Open Questions](questions/sleep-lifelog-open-questions.md) - `questions`\n- [Sleep Lifelog Packet Synthesis](reports/2026-05-29-sleep-lifelog-packet-synthesis.md) - `report`\n<!-- wiki-ingest:index:end -->\n",
        },
        {
            "path": "wiki/log.md",
            "content": "# Log\n\n## [2026-05-01] seed | baseline\n\n- Existing log entry.\n\n## [2026-05-29] llm-synthesis | sleep-lifelog\n\n- Integrated dataset packet into the wiki graph.\n",
        },
    ]
    return pages


def test_llm_synthesis_calls_gpt55_with_policy_packet_and_existing_wiki_context(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    client = FakeClient(
        {
            "summary": "Rewrote dataset page with policy-aware synthesis.",
            "review_notes": ["Confirm tentative claims remain tentative."],
            "pages": [
                *single_dataset_integration_pages(),
            ],
        }
    )

    report = run_llm_wiki_synthesis(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        report_path=tmp_path / "raw" / "results" / "llm-synthesis" / "llm-run" / "report.json",
        run_id="llm-run",
        client=client,
    )

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["model"] == "gpt-5.5"
    assert call["reasoning_effort"] == "high"
    prompt = call["prompt"]
    assert "FILE: AGENTS.md" in prompt
    assert "Treat raw/ as append-only" in prompt
    assert "FILE: CLAUDE.md" in prompt
    assert "FILE: wiki/latest-context.md" in prompt
    assert "FILE: raw/users/alice/datasets/2026-05-29-sleep-lifelog-2024/packet.md" in prompt
    assert "This packet explains leakage risks." in prompt
    assert "FILE: wiki/datasets/sleep-lifelog-2024.md" in prompt
    assert "Old deterministic summary" in prompt
    assert "metadata summaries in Korean" in prompt
    assert "claim registry" in prompt
    assert "leaderboard history" in prompt
    assert "latest-context must expose Current Best, Active Risks, and Next Actions" in prompt
    assert report.status == "bot_pr"
    assert report.risk_tier == "tier4-governance"
    assert "wiki/features/sleep-lifelog-feature-landscape.md" in report.generated_paths
    assert "wiki/decisions/sleep-lifelog-evaluation-protocol.md" in report.generated_paths
    assert "wiki/questions/sleep-lifelog-open-questions.md" in report.generated_paths
    assert "wiki/claims/current-supported-claims.md" in report.generated_paths
    assert "wiki/submissions/dacon-leaderboard-history.md" in report.generated_paths
    assert "wiki/preprocessing/canonical-split-and-leakage-policy.md" in report.generated_paths
    assert report.generated_paths[-1] == "raw/results/llm-synthesis/llm-run/report.json"
    assert "LLM synthesized page" in (tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md").read_text(
        encoding="utf-8"
    )
    generated_text = (tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md").read_text(encoding="utf-8")
    assert "raw_evidence:" in generated_text
    assert "raw/users/alice/datasets/2026-05-29-sleep-lifelog-2024/manifest.yaml" in generated_text
    assert "raw/users/alice/datasets/2026-05-29-sleep-lifelog-2024/dataset.yaml" in generated_text
    assert "raw/users/alice/datasets/2026-05-29-sleep-lifelog-2024/packet.md" in generated_text
    payload = json.loads((tmp_path / "raw" / "results" / "llm-synthesis" / "llm-run" / "report.json").read_text())
    assert payload["model"] == "gpt-5.5"
    assert payload["llm_synthesis"] is True
    assert payload["review_notes"] == ["Confirm tentative claims remain tentative."]


def test_llm_synthesis_integrates_packets_across_compounding_wiki_pages(tmp_path):
    seed_repo(tmp_path)
    dataset_root = seed_dataset_packet(tmp_path)
    benchmark_root = seed_benchmark_packet(tmp_path)
    client = FakeClient(
        {
            "summary": "Integrated packets into the wiki graph.",
            "integration_plan": [
                "Update stable entity pages.",
                "Create feature, decision, question, and synthesis report pages.",
                "Refresh overview, latest context, index, and log.",
            ],
            "created_pages": [
                "wiki/features/sleep-lifelog-feature-landscape.md",
                "wiki/decisions/sleep-lifelog-evaluation-protocol.md",
                "wiki/questions/sleep-lifelog-open-questions.md",
                "wiki/reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md",
            ],
            "updated_pages": [
                "wiki/datasets/sleep-lifelog-2024.md",
                "wiki/benchmarks/sleep-health-hackathon-v0.md",
                "wiki/overview.md",
                "wiki/latest-context.md",
                "wiki/index.md",
                "wiki/log.md",
            ],
            "claim_register": [{"status": "tentative", "text": "Track A is the local comparison default."}],
            "open_questions": [
                {
                    "id": "Q-SL-006",
                    "question": "How should Track B be evaluated separately?",
                    "priority": "high",
                    "owner_role": "modeling",
                    "merge_blocker": False,
                    "needed_evidence": "Track B leakage analysis packet",
                    "close_condition": "Track B decision page links accepted raw evidence",
                }
            ],
            "superseded_or_conflicting_claims": ["Older six-target notes may be superseded by seven-target packets."],
            "review_notes": ["Review the expanded wiki graph, not only entity pages."],
            "pages": integration_pages(),
        }
    )

    report = run_llm_wiki_synthesis(
        tmp_path,
        changed_paths=[
            str(dataset_root.relative_to(tmp_path) / "manifest.yaml"),
            str(benchmark_root.relative_to(tmp_path) / "manifest.yaml"),
        ],
        run_id="graph-run",
        client=client,
    )

    prompt = client.calls[0]["prompt"]
    assert "Karpathy-style LLM wiki integration pass" in prompt
    assert "wiki/features/sleep-lifelog-feature-landscape.md" in prompt
    assert "wiki/decisions/sleep-lifelog-evaluation-protocol.md" in prompt
    assert "wiki/questions/sleep-lifelog-open-questions.md" in prompt
    assert "wiki/reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md" in prompt
    assert report.status == "bot_pr"
    assert report.generated_paths == [
        "wiki/datasets/sleep-lifelog-2024.md",
        "wiki/benchmarks/sleep-health-hackathon-v0.md",
        "wiki/features/sleep-lifelog-feature-landscape.md",
        "wiki/decisions/sleep-lifelog-evaluation-protocol.md",
        "wiki/questions/sleep-lifelog-open-questions.md",
        "wiki/claims/current-supported-claims.md",
        "wiki/submissions/dacon-leaderboard-history.md",
        "wiki/preprocessing/canonical-split-and-leakage-policy.md",
        "wiki/reports/2026-05-29-sleep-lifelog-benchmark-synthesis.md",
        "wiki/overview.md",
        "wiki/latest-context.md",
        "wiki/index.md",
        "wiki/log.md",
        "raw/results/llm-synthesis/graph-run/report.json",
    ]
    assert (tmp_path / "wiki" / "features" / "sleep-lifelog-feature-landscape.md").exists()
    assert (tmp_path / "wiki" / "decisions" / "sleep-lifelog-evaluation-protocol.md").exists()
    assert (tmp_path / "wiki" / "questions" / "sleep-lifelog-open-questions.md").exists()
    payload = json.loads((tmp_path / "raw" / "results" / "llm-synthesis" / "graph-run" / "report.json").read_text())
    assert payload["integration_plan"][1] == "Create feature, decision, question, and synthesis report pages."
    assert payload["open_questions"] == [
        {
            "id": "Q-SL-006",
            "question": "How should Track B be evaluated separately?",
            "priority": "high",
            "owner_role": "modeling",
            "merge_blocker": False,
            "needed_evidence": "Track B leakage analysis packet",
            "close_condition": "Track B decision page links accepted raw evidence",
        }
    ]


def test_llm_response_schema_requires_structured_open_questions():
    schema = llm_synthesis._response_schema()["schema"]
    open_question_schema = schema["properties"]["open_questions"]["items"]

    assert open_question_schema["type"] == "object"
    assert open_question_schema["required"] == [
        "id",
        "question",
        "priority",
        "owner_role",
        "merge_blocker",
        "needed_evidence",
        "close_condition",
    ]


def test_llm_synthesis_prompt_bounds_page_output_size(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)

    prompt = llm_synthesis.build_llm_synthesis_prompt(
        tmp_path,
        [(llm_synthesis.load_packet_manifest(packet_root), packet_root)],
        ["wiki/datasets/sleep-lifelog-2024.md", "wiki/latest-context.md"],
    )

    assert "Concise page budgets" in prompt
    assert "Do not copy raw packet text into wiki pages" in prompt


def test_llm_synthesis_merges_log_output_append_only(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    pages = [
        {
            "path": page["path"],
            "content": "# Log\n\n## [2026-05-29] llm-synthesis | sleep-lifelog\n\n- Integrated dataset packet into the wiki graph.\n",
        }
        if page["path"] == "wiki/log.md"
        else page
        for page in single_dataset_integration_pages()
    ]
    client = FakeClient(
        {
            "summary": "Merged log entry.",
            "integration_plan": ["Append log entry."],
            "created_pages": [],
            "updated_pages": ["wiki/log.md"],
            "claim_register": [],
            "open_questions": [],
            "superseded_or_conflicting_claims": [],
            "review_notes": [],
            "pages": pages,
        }
    )

    report = run_llm_wiki_synthesis(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        run_id="append-log",
        client=client,
    )

    log_text = (tmp_path / "wiki" / "log.md").read_text(encoding="utf-8")
    assert report.status == "bot_pr"
    assert "## [2026-05-01] seed | baseline" in log_text
    assert "## [2026-05-29] llm-synthesis | sleep-lifelog" in log_text
    assert log_text.index("## [2026-05-01] seed | baseline") < log_text.index(
        "## [2026-05-29] llm-synthesis | sleep-lifelog"
    )


def test_llm_synthesis_rejects_model_attempt_to_write_raw_paths(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    client = FakeClient({"summary": "bad", "review_notes": [], "pages": [{"path": "raw/users/alice/bad.md", "content": "bad"}]})

    with pytest.raises(IngestFailure) as excinfo:
        run_llm_wiki_synthesis(
            tmp_path,
            changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
            run_id="bad-run",
            client=client,
        )

    assert excinfo.value.code is FailureCode.INVALID_TARGET_ROUTE
    assert not (tmp_path / "raw" / "users" / "alice" / "bad.md").exists()


def test_llm_synthesis_hard_fail_does_not_mutate_wiki_on_broken_generated_link(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    target = tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md"
    before = target.read_text(encoding="utf-8")
    client = FakeClient(
        {
            "summary": "bad link",
            "review_notes": [],
            "pages": [
                {"path": page["path"], "content": "# Sleep Lifelog 2024\n\nThis page points at [[missing-page]].\n"}
                if page["path"] == "wiki/datasets/sleep-lifelog-2024.md"
                else page
                for page in single_dataset_integration_pages()
            ],
        }
    )

    report = run_llm_wiki_synthesis(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        run_id="broken-link",
        client=client,
    )

    assert report.status == "hard_fail"
    assert target.read_text(encoding="utf-8") == before


def test_llm_synthesis_staging_preserves_existing_docs_links(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    docs_target = tmp_path / "docs" / "superpowers" / "specs" / "design.md"
    docs_target.parent.mkdir(parents=True)
    docs_target.write_text("# Design\n", encoding="utf-8")
    reports = tmp_path / "wiki" / "reports"
    reports.mkdir()
    (reports / "design-summary.md").write_text(
        "# Design Summary\n\n[Design](../../docs/superpowers/specs/design.md)\n",
        encoding="utf-8",
    )
    index = tmp_path / "wiki" / "index.md"
    index.write_text(index.read_text(encoding="utf-8") + "\n- [Design Summary](reports/design-summary.md)\n", encoding="utf-8")
    client = FakeClient(
        {
            "summary": "ok",
            "review_notes": [],
            "pages": [
                {
                    "path": page["path"],
                    "content": page["content"].replace(
                        "<!-- wiki-ingest:index:end -->",
                        "- [Design Summary](reports/design-summary.md)\n<!-- wiki-ingest:index:end -->",
                    ),
                }
                if page["path"] == "wiki/index.md"
                else page
                for page in single_dataset_integration_pages()
            ],
        }
    )

    report = run_llm_wiki_synthesis(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        run_id="docs-link",
        client=client,
    )

    assert report.status == "bot_pr"


def test_llm_synthesis_merges_index_with_existing_entries_and_generated_pages(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    existing_experiment = tmp_path / "wiki" / "experiments" / "existing-section07.md"
    existing_experiment.parent.mkdir(parents=True)
    existing_experiment.write_text("# Existing Section07\n\nAlready indexed.\n", encoding="utf-8")
    index = tmp_path / "wiki" / "index.md"
    index.write_text(
        "# Index\n\n<!-- wiki-ingest:index:start -->\n"
        "- [Existing Section07](experiments/existing-section07.md) - `experiment`\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )
    pages = [
        {
            "path": page["path"],
            "content": "# Index\n\n<!-- wiki-ingest:index:start -->\n"
            "- [Sleep Lifelog 2024](datasets/sleep-lifelog-2024.md) - `dataset`\n",
        }
        if page["path"] == "wiki/index.md"
        else page
        for page in single_dataset_integration_pages()
    ]
    client = FakeClient(
        {
            "summary": "ok",
            "integration_plan": [],
            "created_pages": ["wiki/reports/2026-05-29-sleep-lifelog-packet-synthesis.md"],
            "updated_pages": ["wiki/index.md"],
            "claim_register": [],
            "open_questions": [],
            "superseded_or_conflicting_claims": [],
            "review_notes": [],
            "pages": pages,
        }
    )

    report = run_llm_wiki_synthesis(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        run_id="index-merge",
        client=client,
    )

    merged_index = index.read_text(encoding="utf-8")
    assert report.status == "bot_pr"
    assert merged_index.count("<!-- wiki-ingest:index:start -->") == 1
    assert merged_index.count("<!-- wiki-ingest:index:end -->") == 1
    assert "experiments/existing-section07.md" in merged_index
    assert "datasets/sleep-lifelog-2024.md" in merged_index
    assert "reports/2026-05-29-sleep-lifelog-packet-synthesis.md" in merged_index


def test_openai_responses_client_posts_structured_gpt55_request(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(
                {
                    "output": [
                        {
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": json.dumps({"summary": "ok", "review_notes": [], "pages": []}),
                                }
                            ]
                        }
                    ]
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(req.header_items())
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr(llm_synthesis.request, "urlopen", fake_urlopen)
    client = OpenAIResponsesClient(api_key="test-key", base_url="https://api.openai.test/v1")

    payload = client.synthesize(model="gpt-5.5", reasoning_effort="high", prompt="context")

    assert payload["summary"] == "ok"
    assert captured["url"] == "https://api.openai.test/v1/responses"
    assert captured["timeout"] == 600
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    body = captured["body"]
    assert body["model"] == "gpt-5.5"
    assert body["reasoning"] == {"effort": "high"}
    assert body["max_output_tokens"] >= 60000
    assert body["text"]["format"]["type"] == "json_schema"
    assert body["input"][1]["content"] == "context"


def test_run_llm_synthesis_can_override_openai_output_budget(monkeypatch, tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    captured = {}

    class CapturingClient:
        def __init__(self, *, max_output_tokens):
            captured["max_output_tokens"] = max_output_tokens

        def synthesize(self, *, model, reasoning_effort, prompt):
            return {
                "summary": "ok",
                "integration_plan": [],
                "created_pages": [],
                "updated_pages": [],
                "claim_register": [],
                "open_questions": [],
                "superseded_or_conflicting_claims": [],
                "review_notes": [],
                "pages": single_dataset_integration_pages(),
            }

    monkeypatch.setattr(llm_synthesis, "OpenAIResponsesClient", CapturingClient)

    report = run_llm_wiki_synthesis(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        run_id="budget-run",
        max_output_tokens=72000,
    )

    assert report.status == "bot_pr"
    assert captured["max_output_tokens"] == 72000
