from __future__ import annotations

import json
import shutil
import tempfile
import time
from pathlib import Path

from .compile import compile_packet
from .guards import run_guard_checks
from .links import lint_wiki_links
from .manifest import discover_packet_roots, load_packet_manifest, validate_changed_paths
from .models import FailureCode, IngestFailure, IngestReport, RiskDecision, RiskTier, RiskTierLabel, as_jsonable
from .policy import load_policy
from .render import render_packets
from .risk import classify_risk
from .routes import packet_target_path


def _rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _write_report(repo_root: Path, report: IngestReport, report_path: Path | None) -> None:
    if report_path is None:
        return
    try:
        rel_report = report_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        rel_report = report_path.resolve().as_posix()
    report.report_path = rel_report
    if rel_report not in report.changed_paths:
        report.changed_paths.append(rel_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(as_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _default_report_path(repo_root: Path, run_id: str) -> Path:
    return repo_root / "raw" / "results" / "wiki-ingest" / run_id / "report.json"


def _compiled_packet_path(packet_id: str) -> str:
    return f"automation/.cache/compiled/{packet_id}.json"


def _write_compiled_packets(staging: Path, packets: list[tuple], packet_roots: list[str]) -> list[str]:
    compiled_paths: list[str] = []
    for (manifest, risk), packet_root in zip(packets, packet_roots, strict=True):
        rel = _compiled_packet_path(manifest.id)
        target = staging / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = compile_packet(
            manifest,
            packet_root=packet_root,
            risk_tier=risk.risk_tier.value,
            publish_action=risk.tier.value,
        )
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        compiled_paths.append(rel)
    return compiled_paths


def _predicted_generated_paths(packets: list[tuple]) -> list[str]:
    paths: list[str] = []
    for manifest, _risk in packets:
        paths.append(packet_target_path(manifest.type, manifest.id))
    if packets:
        paths.extend(["wiki/index.md", "wiki/log.md", "wiki/latest-context.md"])
        paths.extend(_compiled_packet_path(manifest.id) for manifest, _risk in packets)
    return list(dict.fromkeys(paths))


def _staged_subset(repo_root: Path, packet_roots: list[Path]) -> Path:
    staging = Path(tempfile.mkdtemp(prefix="wiki-ingest-stage-"))
    for name in ["AGENTS.md", "CLAUDE.md"]:
        source = repo_root / name
        if source.exists():
            shutil.copy2(source, staging / name)
    if (repo_root / "wiki").exists():
        shutil.copytree(repo_root / "wiki", staging / "wiki")
    for root in packet_roots:
        dest = staging / root.relative_to(repo_root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(root, dest)
    return staging


def _build_report(repo_root: Path, changed_paths: list[str], run_id: str) -> tuple[IngestReport, list[tuple]]:
    start = time.monotonic()
    input_changed_paths = validate_changed_paths(repo_root, changed_paths)
    packet_roots = discover_packet_roots(repo_root, changed_paths)
    if not packet_roots:
        return IngestReport(status="skipped", run_id=run_id, input_changed_paths=input_changed_paths), []

    try:
        policy = load_policy(repo_root)
    except IngestFailure as exc:
        report = IngestReport(
            status="hard_fail",
            run_id=run_id,
            input_changed_paths=input_changed_paths,
            packet_roots=[_rel(repo_root, root) for root in packet_roots],
            failures=[exc.to_dict()],
            risk_tier=RiskTierLabel.TIER4_GOVERNANCE.value,
            timing_ms=int((time.monotonic() - start) * 1000),
        )
        return report, []

    packets = []
    report_packets = []
    failures = [as_jsonable(failure) for failure in policy.failures]
    warnings = list(policy.warnings)
    for packet_root in packet_roots:
        try:
            manifest = load_packet_manifest(packet_root)
        except IngestFailure as exc:
            failure = exc.to_dict()
            failure.setdefault("details", {})["packet_root"] = _rel(repo_root, packet_root)
            failures.append(failure)
            report_packets.append({"packet_root": _rel(repo_root, packet_root), "error": exc.code.value})
            continue
        guard = run_guard_checks(repo_root, packet_root, manifest, policy)
        risk = classify_risk(manifest, guard)
        packets.append((manifest, risk))
        report_packets.append(
            {
                "id": manifest.id,
                "type": manifest.type.value,
                "claim_status": manifest.claim_status,
                "packet_root": _rel(repo_root, packet_root),
                "publish_action": risk.tier.value,
                "risk_tier": risk.risk_tier.value,
                "risk_reasons": risk.reasons,
            }
        )
        warnings.extend(guard.warnings)
        failures.extend(as_jsonable(failure) for failure in guard.failures)

    status = "hard_fail" if failures else ("bot_pr" if any(risk.tier is RiskTier.BOT_PR for _, risk in packets) else "direct_commit")
    report = IngestReport(
        status=status,
        run_id=run_id,
        input_changed_paths=input_changed_paths,
        packet_roots=[_rel(repo_root, root) for root in packet_roots],
        packets=report_packets,
        claim_statuses=[
            {"packet": packet["id"], "status": packet["claim_status"]}
            for packet in report_packets
            if "id" in packet and "claim_status" in packet
        ],
        metric_changes=[
            {
                "packet": manifest.id,
                "metric": metric.metric_key,
                "reported_value": metric.reported_value,
            }
            for manifest, _risk in packets
            for metric in manifest.metrics_to_verify
        ],
        failures=failures,
        warnings=list(dict.fromkeys(warnings)),
        policy_warnings=list(dict.fromkeys(policy.warnings)),
        risk_tier=RiskTierLabel.TIER4_GOVERNANCE.value
        if failures
        else _max_risk_tier([risk for _manifest, risk in packets]),
        timing_ms=int((time.monotonic() - start) * 1000),
    )
    return report, packets


def _max_risk_tier(risks: list[RiskDecision]) -> str | None:
    if not risks:
        return None
    order = {
        RiskTierLabel.TIER0_CATALOG: 0,
        RiskTierLabel.TIER1_SUMMARY: 1,
        RiskTierLabel.TIER2_INTERPRETATION: 2,
        RiskTierLabel.TIER3_PERFORMANCE: 3,
        RiskTierLabel.TIER4_GOVERNANCE: 4,
    }
    return max((risk.risk_tier for risk in risks), key=lambda tier: order[tier]).value


def plan_wiki_main_ingest(repo_root: Path, changed_paths: list[str], run_id: str = "plan") -> IngestReport:
    report, packets = _build_report(repo_root, changed_paths, run_id)
    if report.status not in {"skipped", "hard_fail"}:
        report.generated_paths = _predicted_generated_paths(packets)
        report.changed_paths = list(report.generated_paths)
    return report


def run_wiki_main_ingest(
    repo_root: Path,
    changed_paths: list[str],
    report_path: Path | None = None,
    run_id: str = "run",
) -> IngestReport:
    report_path = report_path or _default_report_path(repo_root, run_id)
    start = time.monotonic()
    try:
        report, packets = _build_report(repo_root, changed_paths, run_id)
    except IngestFailure as exc:
        report = IngestReport(
            status="hard_fail",
            run_id=run_id,
            failures=[exc.to_dict()],
            risk_tier=RiskTierLabel.TIER4_GOVERNANCE.value,
            timing_ms=int((time.monotonic() - start) * 1000),
        )
        _write_report(repo_root, report, report_path)
        return report
    if report.status in {"skipped", "hard_fail"}:
        report.timing_ms = int((time.monotonic() - start) * 1000)
        _write_report(repo_root, report, report_path)
        return report

    packet_roots = [repo_root / root for root in report.packet_roots]
    staging = _staged_subset(repo_root, packet_roots)
    try:
        policy = load_policy(repo_root)
        rendered = render_packets(
            staging,
            [(manifest, risk.tier, risk.risk_tier) for manifest, risk in packets],
            run_id=run_id,
            policy=policy,
        )
        compiled_paths = _write_compiled_packets(staging, packets, report.packet_roots)
        link_errors = lint_wiki_links(staging, rendered.changed_paths)
        report.link_lint_errors = [as_jsonable(error) for error in link_errors]
        if link_errors:
            report.status = "hard_fail"
            report.risk_tier = RiskTierLabel.TIER4_GOVERNANCE.value
        else:
            generated_paths = [*rendered.changed_paths, *compiled_paths]
            report.generated_paths = generated_paths
            report.changed_paths = list(generated_paths)
            for rel in generated_paths:
                source = staging / rel
                target = repo_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    report.timing_ms = int((time.monotonic() - start) * 1000)
    _write_report(repo_root, report, report_path)
    return report
