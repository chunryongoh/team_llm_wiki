from team_llm_wiki.wiki_ingest.models import GuardResult, GuardViolation, PacketManifest, RiskTier
from team_llm_wiki.wiki_ingest.risk import classify_risk


def manifest(**overrides):
    data = {
        "id": "pkt-1",
        "type": "reference",
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
        "intended_wiki_targets": ["wiki/sources/pkt-1.md"],
    }
    data.update(overrides)
    return PacketManifest(**data)


def test_low_risk_reference_direct_commit():
    packet = manifest(id="ref", type="reference", title="Reference", intended_wiki_targets=["wiki/sources/ref.md"])

    assert classify_risk(packet, GuardResult()).tier is RiskTier.DIRECT_COMMIT


def test_high_risk_packet_type_goes_bot_pr():
    packet = manifest(id="exp", type="experiment", title="Run", intended_wiki_targets=["wiki/experiments/exp.md"])

    assert classify_risk(packet, GuardResult()).tier is RiskTier.BOT_PR


def test_guard_failure_hard_fail():
    packet = manifest(id="ref", type="reference", title="Reference", intended_wiki_targets=["wiki/sources/ref.md"])
    guard = GuardResult(failures=[GuardViolation(code="missing_raw_file", message="missing")])

    assert classify_risk(packet, guard).tier is RiskTier.HARD_FAIL


def test_supported_disputed_superseded_claims_require_bot_pr():
    for status in ["supported", "disputed", "superseded"]:
        packet = manifest(
            id=status,
            type="reference",
            title="Claim",
            intended_wiki_targets=[f"wiki/sources/{status}.md"],
            claims=[{"status": status, "text": "claim"}],
        )

        assert classify_risk(packet, GuardResult()).tier is RiskTier.BOT_PR
