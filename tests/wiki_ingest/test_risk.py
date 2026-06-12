from team_llm_wiki.wiki_ingest.models import GuardResult, GuardViolation, PacketManifest, RiskTier
from team_llm_wiki.wiki_ingest.risk import classify_risk


def manifest(**overrides):
    data = {
        "id": "pkt-1",
        "type": "reference",
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
        "intended_wiki_targets": ["wiki/reports/pkt-1.md"],
    }
    data.update(overrides)
    return PacketManifest(**data)


def test_reference_reports_route_requires_review():
    packet = manifest(id="ref", type="reference", title="Reference", intended_wiki_targets=["wiki/reports/ref.md"])

    decision = classify_risk(packet, GuardResult())

    assert decision.tier is RiskTier.BOT_PR
    assert "high-risk canonical route" in decision.reasons


def test_high_risk_packet_type_goes_bot_pr():
    packet = manifest(id="exp", type="experiment", title="Run", intended_wiki_targets=["wiki/reports/exp.md"])

    assert classify_risk(packet, GuardResult()).tier is RiskTier.BOT_PR


def test_preprocessing_packet_requires_review():
    packet = manifest(
        id="prep",
        type="preprocessing",
        title="Preprocessing",
        intended_wiki_targets=["wiki/preprocessing/prep.md"],
    )

    decision = classify_risk(packet, GuardResult())

    assert decision.tier is RiskTier.BOT_PR


def test_dataset_packet_requires_review():
    packet = manifest(
        id="ds",
        type="dataset",
        title="Dataset",
        intended_wiki_targets=["wiki/preprocessing/ds.md"],
    )

    decision = classify_risk(packet, GuardResult())

    assert decision.tier is RiskTier.BOT_PR
    assert "high-risk packet type: dataset" in decision.reasons


def test_benchmark_packet_requires_review():
    packet = manifest(
        id="bm",
        type="benchmark",
        title="Benchmark",
        intended_wiki_targets=["wiki/performance/bm.md"],
    )

    decision = classify_risk(packet, GuardResult())

    assert decision.tier is RiskTier.BOT_PR
    assert "high-risk packet type: benchmark" in decision.reasons
    assert "high-risk wiki target path" in decision.reasons


def test_guard_failure_hard_fail():
    packet = manifest(id="ref", type="reference", title="Reference", intended_wiki_targets=["wiki/reports/ref.md"])
    guard = GuardResult(failures=[GuardViolation(code="missing_raw_file", message="missing")])

    assert classify_risk(packet, guard).tier is RiskTier.HARD_FAIL


def test_supported_disputed_superseded_claims_require_bot_pr():
    for status in ["supported", "disputed", "superseded"]:
        packet = manifest(
            id=status,
            type="reference",
            title="Claim",
            intended_wiki_targets=[f"wiki/reports/{status}.md"],
            claims=[{"status": status, "text": "claim"}],
        )

        assert classify_risk(packet, GuardResult()).tier is RiskTier.BOT_PR


def test_top_level_supported_disputed_superseded_claim_status_requires_bot_pr():
    for status in ["supported", "disputed", "superseded"]:
        packet = manifest(
            id=status,
            type="reference",
            title="Claim",
            intended_wiki_targets=[f"wiki/reports/{status}.md"],
            claim_status=status,
            claims=[],
        )

        decision = classify_risk(packet, GuardResult())

        assert decision.tier is RiskTier.BOT_PR
        assert "governance-tier claim status" in decision.reasons
