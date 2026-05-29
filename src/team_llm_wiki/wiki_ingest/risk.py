from __future__ import annotations

from .models import GuardResult, PacketManifest, PacketType, RiskDecision, RiskTier, RiskTierLabel
from .routes import PACKET_ROUTE_MAP

HIGH_RISK_TYPES = {
    PacketType.PERFORMANCE,
    PacketType.EXPERIMENT,
    PacketType.MODEL,
    PacketType.FEATURE,
    PacketType.PREPROCESSING,
    PacketType.AUGMENTATION,
    PacketType.DATASET,
    PacketType.BENCHMARK,
}
HIGH_RISK_PATH_PREFIXES = (
    "wiki/performance/",
    "wiki/models/",
    "wiki/features/",
    "wiki/experiments/",
    "wiki/datasets/",
    "wiki/benchmarks/",
)
GOVERNANCE_CLAIM_STATUSES = {"supported", "disputed", "superseded"}


def classify_risk(manifest: PacketManifest, guard: GuardResult) -> RiskDecision:
    if guard.failures:
        return RiskDecision(RiskTier.HARD_FAIL, [failure.message for failure in guard.failures], RiskTierLabel.TIER4_GOVERNANCE)

    reasons: list[str] = []
    risk_tier = RiskTierLabel.TIER0_CATALOG
    if manifest.type in HIGH_RISK_TYPES:
        reasons.append(f"high-risk packet type: {manifest.type.value}")
        risk_tier = RiskTierLabel.TIER2_INTERPRETATION
    if manifest.type is PacketType.PERFORMANCE:
        risk_tier = RiskTierLabel.TIER3_PERFORMANCE
    if any(path.startswith(HIGH_RISK_PATH_PREFIXES) for path in manifest.intended_wiki_targets):
        reasons.append("high-risk wiki target path")
        if risk_tier is RiskTierLabel.TIER0_CATALOG:
            risk_tier = RiskTierLabel.TIER2_INTERPRETATION
    if PACKET_ROUTE_MAP[manifest.type] + "/" in HIGH_RISK_PATH_PREFIXES:
        reasons.append("high-risk canonical route")
        if risk_tier is RiskTierLabel.TIER0_CATALOG:
            risk_tier = RiskTierLabel.TIER2_INTERPRETATION
    if manifest.claim_status in GOVERNANCE_CLAIM_STATUSES or any(
        claim.status in GOVERNANCE_CLAIM_STATUSES for claim in manifest.claims
    ):
        reasons.append("governance-tier claim status")
        risk_tier = RiskTierLabel.TIER4_GOVERNANCE

    return RiskDecision(RiskTier.BOT_PR if reasons else RiskTier.DIRECT_COMMIT, reasons, risk_tier)
