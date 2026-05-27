from pathlib import Path

from team_llm_wiki.wiki_ingest.models import PacketManifest, PacketType, RiskTier
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
        PacketType.MEETING: "wiki/sources",
        PacketType.FEATURE: "wiki/features",
        PacketType.MODEL: "wiki/models",
        PacketType.PERFORMANCE: "wiki/performance",
        PacketType.PREPROCESSING: "wiki/datasets",
        PacketType.AUGMENTATION: "wiki/datasets",
        PacketType.EXPERIMENT: "wiki/experiments",
        PacketType.REFERENCE: "wiki/sources",
    }[packet_type]
    data = {
        "id": packet_id,
        "type": packet_type,
        "title": "Reference",
        "date": "2026-05-27",
        "owner": "alice",
        "status": "ready",
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
    assert "wiki/sources/ref-1.md" in (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
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
    assert "- [New Ref](wiki/sources/new-ref.md) - `reference`" in index


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
