from __future__ import annotations

from pathlib import Path

from .models import GuardResult, PacketManifest, PacketType, RiskDecision, RiskTier, RiskTierLabel
from .route_contract import load_route_contract
from .routes import packet_route

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
GOVERNANCE_CLAIM_STATUSES = {"supported", "disputed", "superseded"}
DEFAULT_HIGH_RISK_PATHS = (
    "wiki/preprocessing",
    "wiki/features",
    "wiki/models",
    "wiki/performance",
    "wiki/claims",
    "wiki/targets",
    "wiki/decisions",
    "wiki/reports",
)


def _high_risk_path_prefixes(repo_root: Path | None = None) -> tuple[str, ...]:
    if repo_root is None:
        return tuple(f"{path}/" for path in DEFAULT_HIGH_RISK_PATHS)
    contract = load_route_contract(repo_root)
    return tuple(f"{path}/" for path in contract.canonical_paths if path != "wiki/team")


def classify_risk(manifest: PacketManifest, guard: GuardResult, *, repo_root: Path | None = None) -> RiskDecision:
    if guard.failures:
        return RiskDecision(RiskTier.HARD_FAIL, [failure.message for failure in guard.failures], RiskTierLabel.TIER4_GOVERNANCE)

    reasons: list[str] = []
    risk_tier = RiskTierLabel.TIER0_CATALOG
    if manifest.type in HIGH_RISK_TYPES:
        reasons.append(f"high-risk packet type: {manifest.type.value}")
        risk_tier = RiskTierLabel.TIER2_INTERPRETATION
    if manifest.type is PacketType.PERFORMANCE:
        risk_tier = RiskTierLabel.TIER3_PERFORMANCE
    high_risk_path_prefixes = _high_risk_path_prefixes(repo_root)
    if any(path.startswith(high_risk_path_prefixes) for path in manifest.intended_wiki_targets):
        reasons.append("high-risk wiki target path")
        if risk_tier is RiskTierLabel.TIER0_CATALOG:
            risk_tier = RiskTierLabel.TIER2_INTERPRETATION
    if packet_route(manifest.type, repo_root=repo_root) + "/" in high_risk_path_prefixes:
        reasons.append("high-risk canonical route")
        if risk_tier is RiskTierLabel.TIER0_CATALOG:
            risk_tier = RiskTierLabel.TIER2_INTERPRETATION
    if manifest.claim_status in GOVERNANCE_CLAIM_STATUSES or any(
        claim.status in GOVERNANCE_CLAIM_STATUSES for claim in manifest.claims
    ):
        reasons.append("governance-tier claim status")
        risk_tier = RiskTierLabel.TIER4_GOVERNANCE

    return RiskDecision(RiskTier.BOT_PR if reasons else RiskTier.DIRECT_COMMIT, reasons, risk_tier)
