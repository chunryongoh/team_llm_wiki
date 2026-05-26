from team_llm_wiki.wiki_ingest.models import GuardResult, GuardViolation, PacketManifest, RiskTier
from team_llm_wiki.wiki_ingest.risk import classify_risk


def test_low_risk_reference_direct_commit():
    manifest = PacketManifest(id="ref", type="reference", title="Reference")

    assert classify_risk(manifest, GuardResult()).tier is RiskTier.DIRECT_COMMIT


def test_high_risk_packet_type_goes_bot_pr():
    manifest = PacketManifest(id="exp", type="experiment", title="Run")

    assert classify_risk(manifest, GuardResult()).tier is RiskTier.BOT_PR


def test_guard_failure_hard_fail():
    manifest = PacketManifest(id="ref", type="reference", title="Reference")
    guard = GuardResult(failures=[GuardViolation(code="missing_raw_file", message="missing")])

    assert classify_risk(manifest, guard).tier is RiskTier.HARD_FAIL


def test_supported_disputed_superseded_claims_require_bot_pr():
    for status in ["supported", "disputed", "superseded"]:
        manifest = PacketManifest(
            id=status,
            type="reference",
            title="Claim",
            claims=[{"status": status, "text": "claim"}],
        )

        assert classify_risk(manifest, GuardResult()).tier is RiskTier.BOT_PR
