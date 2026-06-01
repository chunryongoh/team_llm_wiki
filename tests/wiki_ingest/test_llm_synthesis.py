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
    (root / "wiki" / "index.md").write_text(
        "# Index\n\n<!-- wiki-ingest:index:start -->\n"
        "- [Sleep Lifelog 2024](datasets/sleep-lifelog-2024.md) - `dataset`\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )
    (root / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (root / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
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


def test_llm_synthesis_calls_gpt55_with_policy_packet_and_existing_wiki_context(tmp_path):
    seed_repo(tmp_path)
    packet_root = seed_dataset_packet(tmp_path)
    client = FakeClient(
        {
            "summary": "Rewrote dataset page with policy-aware synthesis.",
            "review_notes": ["Confirm tentative claims remain tentative."],
            "pages": [
                {
                    "path": "wiki/datasets/sleep-lifelog-2024.md",
                    "content": "# Sleep Lifelog 2024\n\nLLM synthesized page.\n\n- claim_status: `tentative`\n",
                }
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
    assert report.status == "bot_pr"
    assert report.risk_tier == "tier2-interpretation"
    assert report.generated_paths == [
        "wiki/datasets/sleep-lifelog-2024.md",
        "raw/results/llm-synthesis/llm-run/report.json",
    ]
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
                {
                    "path": "wiki/datasets/sleep-lifelog-2024.md",
                    "content": "# Sleep Lifelog 2024\n\nThis page points at [[missing-page]].\n",
                }
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
                    "path": "wiki/datasets/sleep-lifelog-2024.md",
                    "content": "---\nid: 2026-05-29-sleep-lifelog-2024\nclaim_status: tentative\n---\n# Sleep Lifelog 2024\n\nLLM synthesized page.\n",
                }
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
    assert body["text"]["format"]["type"] == "json_schema"
    assert body["input"][1]["content"] == "context"
