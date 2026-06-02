from pathlib import Path

from team_llm_wiki.wiki_ingest.models import PacketManifest, PacketType, RiskTier, RiskTierLabel
from team_llm_wiki.wiki_ingest.policy import IngestPolicy
from team_llm_wiki.wiki_ingest.render import render_packets
from team_llm_wiki.wiki_ingest.health import check_wiki_health


def manifest(**overrides):
    packet_id = overrides.get("id", "pkt-1")
    packet_type = overrides.get("type", PacketType.REFERENCE)
    route = {
        "meeting": "wiki/sources",
        "feature": "wiki/features",
        "model": "wiki/models",
        "performance": "wiki/performance",
        "preprocessing": "wiki/datasets",
        "augmentation": "wiki/datasets",
        "experiment": "wiki/experiments",
        "reference": "wiki/sources",
        "dataset": "wiki/datasets",
        "benchmark": "wiki/benchmarks",
        PacketType.MEETING: "wiki/sources",
        PacketType.FEATURE: "wiki/features",
        PacketType.MODEL: "wiki/models",
        PacketType.PERFORMANCE: "wiki/performance",
        PacketType.PREPROCESSING: "wiki/datasets",
        PacketType.AUGMENTATION: "wiki/datasets",
        PacketType.EXPERIMENT: "wiki/experiments",
        PacketType.REFERENCE: "wiki/sources",
        PacketType.DATASET: "wiki/datasets",
        PacketType.BENCHMARK: "wiki/benchmarks",
    }[packet_type]
    data = {
        "id": packet_id,
        "type": packet_type,
        "title": "Reference",
        "date": "2026-05-27",
        "owner": "alice",
        "status": "submitted",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1"},
        "split": {"name": "dev"},
        "model": {"family": "llama"},
        "claim_boundary": "Only applies to the dev split.",
        "claim_status": "tentative",
        "summary": "Run summary.",
        "raw_paths": ["result.json"],
        "intended_wiki_targets": [f"{route}/{packet_id}.md"],
    }
    data.update(overrides)
    return PacketManifest(**data)


def seed_entity_model_pages(root: Path):
    required = [
        "wiki/team/ml-ai-hackathon-entity-model.md",
        "wiki/team/packet-quality-standard.md",
        "wiki/claims/current-supported-claims.md",
        "wiki/preprocessing/canonical-split-and-leakage-policy.md",
        "wiki/submissions/dacon-leaderboard-history.md",
    ]
    for rel_path in required:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.stem.replace('-', ' ').title()}\n", encoding="utf-8")


def test_render_source_index_log_and_latest_context(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    latest = tmp_path / "wiki" / "latest-context.md"
    latest.write_text(
        "# Latest Context\n\n"
        "<!-- wiki-ingest:latest:start -->\n"
        "old generated entry\n"
        "<!-- wiki-ingest:latest:end -->\n",
        encoding="utf-8",
    )
    packet = manifest(
        id="ref-1",
        type=PacketType.REFERENCE,
        title="Reference One",
        date="2026-05-26",
        summary="Short summary",
    )

    result = render_packets(tmp_path, [(packet, RiskTier.DIRECT_COMMIT)], run_id="run-1")

    target = tmp_path / "wiki" / "sources" / "ref-1.md"
    assert target.exists()
    assert "Reference One" in target.read_text(encoding="utf-8")
    assert "sources/ref-1.md" in (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    assert "## [2026-05-26] ingest | ref-1" in (tmp_path / "wiki" / "log.md").read_text(encoding="utf-8")
    latest_text = latest.read_text(encoding="utf-8")
    assert "old generated entry" in latest_text
    assert "[[index]]" in latest_text
    assert "[[overview]]" in latest_text
    assert "[[log]]" in latest_text
    assert result.changed_paths == [
        "wiki/sources/ref-1.md",
        "wiki/index.md",
        "wiki/log.md",
        "wiki/latest-context.md",
    ]


def test_render_packet_page_separates_publish_action_from_risk_tier(tmp_path):
    (tmp_path / "wiki").mkdir()
    packet = manifest(id="risk-ref", type=PacketType.REFERENCE, title="Risk Ref")

    render_packets(
        tmp_path,
        [(packet, RiskTier.BOT_PR, RiskTierLabel.TIER4_GOVERNANCE)],
        run_id="run-risk",
    )

    text = (tmp_path / "wiki" / "sources" / "risk-ref.md").read_text(encoding="utf-8")
    latest = (tmp_path / "wiki" / "latest-context.md").read_text(encoding="utf-8")
    assert "publish_action: bot_pr" in text
    assert "risk_tier: tier4-governance" in text
    assert "- publish_action: `bot_pr`" in latest
    assert "- risk_tier: `tier4-governance`" in latest


def test_render_canonical_routes_and_review_notes(tmp_path):
    (tmp_path / "wiki").mkdir()
    packets = [
        manifest(id="meet", type="meeting", title="Meeting"),
        manifest(id="feat", type="feature", title="Feature"),
        manifest(id="model", type="model", title="Model"),
        manifest(id="perf", type="performance", title="Perf"),
        manifest(id="prep", type="preprocessing", title="Prep"),
        manifest(id="aug", type="augmentation", title="Aug"),
        manifest(id="exp", type="experiment", title="Exp"),
    ]

    render_packets(tmp_path, [(packet, RiskTier.BOT_PR) for packet in packets], run_id="run-2")

    assert (tmp_path / "wiki" / "sources" / "meet.md").exists()
    assert (tmp_path / "wiki" / "features" / "feat.md").exists()
    assert (tmp_path / "wiki" / "models" / "model.md").exists()
    assert (tmp_path / "wiki" / "performance" / "perf.md").exists()
    assert (tmp_path / "wiki" / "datasets" / "prep.md").exists()
    assert (tmp_path / "wiki" / "datasets" / "aug.md").exists()
    assert "review-required" in (tmp_path / "wiki" / "features" / "feat.md").read_text(encoding="utf-8")


def test_render_spec_metric_uses_raw_evidence_fields(tmp_path):
    (tmp_path / "wiki").mkdir()
    packet = manifest(
        id="metric-ref",
        type="reference",
        title="Metric Ref",
        raw_paths=["metrics/result.json"],
        metrics_to_verify=[
            {
                "raw_path": "metrics/result.json",
                "metric_key": "scores.accuracy",
                "reported_value": 0.82,
                "tolerance": 0.001,
            }
        ],
    )

    render_packets(tmp_path, [(packet, RiskTier.DIRECT_COMMIT)], run_id="run-metric")

    text = (tmp_path / "wiki" / "sources" / "metric-ref.md").read_text(encoding="utf-8")
    assert "None" not in text
    assert "- `scores.accuracy`: reported `0.82`, raw_path `metrics/result.json`, tolerance `0.001`" in text
    assert "raw-evidence-backed" in text


def test_render_packet_page_includes_full_manifest_lineage(tmp_path):
    (tmp_path / "wiki").mkdir()
    packet = manifest(id="lineage-ref", type="reference", title="Lineage Ref")

    render_packets(tmp_path, [(packet, RiskTier.DIRECT_COMMIT)], run_id="run-lineage")

    text = (tmp_path / "wiki" / "sources" / "lineage-ref.md").read_text(encoding="utf-8")
    assert "owner: alice" in text
    assert "task: classification" in text
    assert "dataset:" in text
    assert "name: benchmark-set" in text
    assert "split:" in text
    assert "name: dev" in text
    assert "model:" in text
    assert "family: llama" in text
    assert "claim_boundary: Only applies to the dev split." in text
    assert "claim_status: tentative" in text
    assert "- owner: `alice`" in text
    assert "- task: `classification`" in text
    assert "- dataset: `benchmark-set` (`v1`)" in text
    assert "- split: `dev`" in text
    assert "- model: `llama`" in text
    assert "- claim_boundary: Only applies to the dev split." in text
    assert "- claim_status: `tentative`" in text


def test_render_packet_page_links_to_compiled_packet_json(tmp_path):
    (tmp_path / "wiki").mkdir()
    seed_entity_model_pages(tmp_path)
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (tmp_path / "automation" / ".cache" / "compiled").mkdir(parents=True)
    (tmp_path / "automation" / ".cache" / "compiled" / "compiled-ref.json").write_text("{}\n", encoding="utf-8")
    packet = manifest(id="compiled-ref", type="reference", title="Compiled Ref")

    render_packets(tmp_path, [(packet, RiskTier.DIRECT_COMMIT)], run_id="run-compiled")

    text = (tmp_path / "wiki" / "sources" / "compiled-ref.md").read_text(encoding="utf-8")
    assert "[automation/.cache/compiled/compiled-ref.json](../../automation/.cache/compiled/compiled-ref.json)" in text
    assert check_wiki_health(tmp_path).ok is True


def test_render_preserves_existing_generated_index_entries(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text(
        "# Index\n\n"
        "<!-- wiki-ingest:index:start -->\n"
        "- [Existing](wiki/sources/existing.md) - `reference`\n"
        "<!-- wiki-ingest:index:end -->\n",
        encoding="utf-8",
    )
    (tmp_path / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    packet = manifest(id="new-ref", type="reference", title="New Ref")

    render_packets(tmp_path, [(packet, RiskTier.DIRECT_COMMIT)], run_id="run-3")

    index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    assert "- [Existing](wiki/sources/existing.md) - `reference`" in index
    assert "- [New Ref](sources/new-ref.md) - `reference`" in index


def test_render_escapes_manifest_title_in_generated_index(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    packet = manifest(
        id="bad-title",
        type="reference",
        title="Bad <!-- wiki-ingest:index:end --> [link](../AGENTS.md)",
    )

    render_packets(tmp_path, [(packet, RiskTier.DIRECT_COMMIT)], run_id="run-title")

    index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    assert index.count("<!-- wiki-ingest:index:end -->") == 1
    assert "Bad &lt;!-- wiki-ingest:index:end --&gt; \\[link\\]" in index


def test_latest_context_bounded_and_notes_bot_pr_review_required(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (tmp_path / "wiki" / "latest-context.md").write_text(
        "# Latest Context\n\n[[index]] [[overview]] [[log]]\n\n"
        "<!-- wiki-ingest:latest:start -->\n"
        "### old-1 | old-one\n\n- link: [[sources/old-one]]\n\n"
        "### old-2 | old-two\n\n- link: [[sources/old-two]]\n"
        "<!-- wiki-ingest:latest:end -->\n",
        encoding="utf-8",
    )
    policy = IngestPolicy(agents_text="rules", latest_context_max_entries=2)

    render_packets(
        tmp_path,
        [(manifest(id="exp-1", type="experiment", title="Experiment"), RiskTier.BOT_PR)],
        run_id="run-4",
        policy=policy,
    )

    latest = (tmp_path / "wiki" / "latest-context.md").read_text(encoding="utf-8")
    assert "review-required" in latest
    assert "### run-4 | exp-1" in latest
    assert "### old-1 | old-one" in latest
    assert "### old-2 | old-two" not in latest


def test_latest_context_defaults_to_12_entries_and_6000_chars(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    old_entries = "\n\n".join(
        f"### old-{index} | old-{index}\n\n- link: [[sources/old-{index}]]\n- note: {'x' * 700}"
        for index in range(20)
    )
    (tmp_path / "wiki" / "latest-context.md").write_text(
        "# Latest Context\n\n[[index]] [[overview]] [[log]]\n\n"
        "<!-- wiki-ingest:latest:start -->\n"
        f"{old_entries}\n"
        "<!-- wiki-ingest:latest:end -->\n",
        encoding="utf-8",
    )

    render_packets(
        tmp_path,
        [(manifest(id="ref-new", type="reference", title="New Ref"), RiskTier.DIRECT_COMMIT)],
        run_id="run-new",
    )

    latest = (tmp_path / "wiki" / "latest-context.md").read_text(encoding="utf-8")
    assert latest.count("### ") <= 12
    assert len(latest) <= 6000
    assert "### run-new | ref-new" in latest
    assert "[[index]]" in latest
    assert "[[overview]]" in latest
    assert "[[log]]" in latest


def test_render_dataset_packet_uses_canonical_entity_page_and_promotes_packet_markdown(tmp_path):
    (tmp_path / "wiki").mkdir()
    packet_root = tmp_path / "raw" / "users" / "alice" / "datasets" / "2026-05-29-sleep-lifelog-2024"
    packet_root.mkdir(parents=True)
    (packet_root / "dataset.yaml").write_text(
        "name: sleep-lifelog-2024\n"
        "version: v0\n"
        "modalities:\n"
        "  - smartphone:mActivity\n"
        "package_files:\n"
        "  - ch2026_metrics_train.csv\n"
        "splits:\n"
        "  policy: groupkfold-subject\n"
        "  group_key: subject_id\n"
        "  n_folds: 3\n"
        "leakage_risks:\n"
        "  - q-family-identity-leakage\n"
        "provenance:\n"
        "  source_type: released-package\n"
        "claim_status: tentative\n",
        encoding="utf-8",
    )
    (packet_root / "packet.md").write_text(
        "---\n"
        "id: 2026-05-29-sleep-lifelog-2024\n"
        "---\n"
        "# Sleep Lifelog 2024 Dataset Definition\n\n"
        "## Released Package Contents\n\n"
        "- `ch2026_metrics_train.csv`\n\n"
        "## Known Leakage and Bias Risks\n\n"
        "- Q-family labels are participant-relative averages.\n",
        encoding="utf-8",
    )
    packet = manifest(
        id="2026-05-29-sleep-lifelog-2024",
        type=PacketType.DATASET,
        title="Sleep Lifelog 2024 Dataset Definition",
        dataset={"name": "sleep-lifelog-2024", "version": "v0"},
        raw_paths={"dataset": "dataset.yaml"},
        intended_wiki_targets=["wiki/datasets/2026-05-29-sleep-lifelog-2024.md"],
    )

    result = render_packets(
        tmp_path,
        [(packet, RiskTier.BOT_PR, RiskTierLabel.TIER2_INTERPRETATION)],
        run_id="run-dataset",
        packet_roots={packet.id: packet_root},
    )

    target = tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md"
    assert target.exists()
    assert not (tmp_path / "wiki" / "datasets" / "2026-05-29-sleep-lifelog-2024.md").exists()
    text = target.read_text(encoding="utf-8")
    assert "## Dataset Entity" in text
    assert "`smartphone:mActivity`" in text
    assert "`ch2026_metrics_train.csv`" in text
    assert "## Released Package Contents" in text
    assert "Q-family labels are participant-relative averages." in text
    index = (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    assert "(datasets/sleep-lifelog-2024.md)" in index
    assert "(wiki/datasets/sleep-lifelog-2024.md)" not in index
    assert "wiki/datasets/sleep-lifelog-2024.md" in result.changed_paths


def test_render_benchmark_packet_uses_canonical_page_structured_sections_and_rewrites_packet_links(tmp_path):
    (tmp_path / "wiki").mkdir()
    dataset_root = tmp_path / "raw" / "users" / "alice" / "datasets" / "2026-05-29-sleep-lifelog-2024"
    benchmark_root = tmp_path / "raw" / "users" / "alice" / "benchmarks" / "2026-05-29-sleep-health-hackathon-v0"
    dataset_root.mkdir(parents=True)
    benchmark_root.mkdir(parents=True)
    (dataset_root / "dataset.yaml").write_text(
        "name: sleep-lifelog-2024\n"
        "version: v0\n"
        "modalities: [smartphone:mActivity]\n"
        "package_files: [ch2026_metrics_train.csv]\n"
        "splits: {policy: groupkfold-subject}\n"
        "leakage_risks: [q-family-identity-leakage]\n"
        "provenance: {source_type: released-package}\n"
        "claim_status: tentative\n",
        encoding="utf-8",
    )
    (benchmark_root / "benchmark.yaml").write_text(
        "name: sleep-health-hackathon-v0\n"
        "dataset_ref: sleep-lifelog-2024\n"
        "task_family: sleep-health-prediction\n"
        "targets:\n"
        "  - id: Q1\n"
        "    kind: subjective-binary\n"
        "    description: perceived sleep quality\n"
        "primary_metric:\n"
        "  name: grouped_macro_logloss\n"
        "  definition: subject-grouped OOF log-loss macro mean\n"
        "evaluation_policy:\n"
        "  split: groupkfold-subject\n"
        "  group_key: subject_id\n"
        "  n_folds: 3\n"
        "claim_boundaries:\n"
        "  - local_oof_diagnostic_only\n"
        "claim_status: tentative\n",
        encoding="utf-8",
    )
    (benchmark_root / "packet.md").write_text(
        "# Sleep Health Hackathon Benchmark v0 Definition\n\n"
        "## Dataset Anchor\n\n"
        "This benchmark evaluates [[datasets/2026-05-29-sleep-lifelog-2024]].\n",
        encoding="utf-8",
    )
    dataset_packet = manifest(
        id="2026-05-29-sleep-lifelog-2024",
        type=PacketType.DATASET,
        title="Sleep Lifelog 2024 Dataset Definition",
        dataset={"name": "sleep-lifelog-2024", "version": "v0"},
        raw_paths={"dataset": "dataset.yaml"},
        intended_wiki_targets=["wiki/datasets/2026-05-29-sleep-lifelog-2024.md"],
    )
    benchmark_packet = manifest(
        id="2026-05-29-sleep-health-hackathon-v0",
        type=PacketType.BENCHMARK,
        title="Sleep Health Hackathon Benchmark v0 Definition",
        raw_paths={"benchmark": "benchmark.yaml"},
        intended_wiki_targets=["wiki/benchmarks/2026-05-29-sleep-health-hackathon-v0.md"],
    )

    render_packets(
        tmp_path,
        [
            (dataset_packet, RiskTier.BOT_PR, RiskTierLabel.TIER2_INTERPRETATION),
            (benchmark_packet, RiskTier.BOT_PR, RiskTierLabel.TIER2_INTERPRETATION),
        ],
        run_id="run-benchmark",
        packet_roots={dataset_packet.id: dataset_root, benchmark_packet.id: benchmark_root},
    )

    text = (tmp_path / "wiki" / "benchmarks" / "sleep-health-hackathon-v0.md").read_text(encoding="utf-8")
    assert "## Benchmark Entity" in text
    assert "`grouped_macro_logloss`" in text
    assert "| Q1 | subjective-binary | perceived sleep quality |" in text
    assert "[[datasets/sleep-lifelog-2024]]" in text
    assert "[[datasets/2026-05-29-sleep-lifelog-2024]]" not in text
