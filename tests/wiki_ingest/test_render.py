from pathlib import Path

from team_llm_wiki.wiki_ingest.models import PacketManifest, PacketType, RiskTier
from team_llm_wiki.wiki_ingest.render import render_packets


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
    manifest = PacketManifest(
        id="ref-1",
        type=PacketType.REFERENCE,
        title="Reference One",
        date="2026-05-26",
        summary="Short summary",
    )

    result = render_packets(tmp_path, [(manifest, RiskTier.DIRECT_COMMIT)], run_id="run-1")

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
        PacketManifest(id="meet", type="meeting", title="Meeting"),
        PacketManifest(id="feat", type="feature", title="Feature"),
        PacketManifest(id="model", type="model", title="Model"),
        PacketManifest(id="perf", type="performance", title="Perf"),
        PacketManifest(id="prep", type="preprocessing", title="Prep"),
        PacketManifest(id="aug", type="augmentation", title="Aug"),
        PacketManifest(id="exp", type="experiment", title="Exp"),
    ]

    render_packets(tmp_path, [(packet, RiskTier.BOT_PR) for packet in packets], run_id="run-2")

    assert (tmp_path / "wiki" / "sources" / "meet.md").exists()
    assert (tmp_path / "wiki" / "features" / "feat.md").exists()
    assert (tmp_path / "wiki" / "models" / "model.md").exists()
    assert (tmp_path / "wiki" / "performance" / "perf.md").exists()
    assert (tmp_path / "wiki" / "datasets" / "prep.md").exists()
    assert (tmp_path / "wiki" / "datasets" / "aug.md").exists()
    assert "review-required" in (tmp_path / "wiki" / "features" / "feat.md").read_text(encoding="utf-8")
