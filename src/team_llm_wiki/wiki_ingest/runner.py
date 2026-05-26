from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from .guards import run_guard_checks
from .links import lint_wiki_links
from .manifest import discover_packet_roots, load_packet_manifest, validate_changed_paths
from .models import IngestReport, RiskTier, as_jsonable
from .policy import load_policy
from .render import render_packets
from .risk import classify_risk


def _rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _write_report(repo_root: Path, report: IngestReport, report_path: Path | None) -> None:
    if report_path is None:
        return
    rel_report = report_path.resolve().relative_to(repo_root.resolve()).as_posix()
    if rel_report not in report.changed_paths:
        report.changed_paths.append(rel_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(as_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _default_report_path(repo_root: Path, run_id: str) -> Path:
    return repo_root / "raw" / "results" / "wiki-ingest" / run_id / "report.json"


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
    validate_changed_paths(repo_root, changed_paths)
    packet_roots = discover_packet_roots(repo_root, changed_paths)
    if not packet_roots:
        return IngestReport(status="skipped", run_id=run_id), []

    policy = load_policy(repo_root)
    packets = []
    report_packets = []
    failures = []
    warnings = list(policy.warnings)
    for packet_root in packet_roots:
        manifest = load_packet_manifest(packet_root)
        guard = run_guard_checks(repo_root, packet_root, manifest, policy)
        risk = classify_risk(manifest, guard)
        packets.append((manifest, risk.tier))
        report_packets.append(
            {
                "id": manifest.id,
                "type": manifest.type.value,
                "packet_root": _rel(repo_root, packet_root),
                "risk_tier": risk.tier.value,
                "risk_reasons": risk.reasons,
            }
        )
        warnings.extend(guard.warnings)
        failures.extend(as_jsonable(failure) for failure in guard.failures)

    status = "hard_fail" if failures else ("bot_pr" if any(tier is RiskTier.BOT_PR for _, tier in packets) else "direct_commit")
    report = IngestReport(
        status=status,
        run_id=run_id,
        packet_roots=[_rel(repo_root, root) for root in packet_roots],
        packets=report_packets,
        failures=failures,
        warnings=list(dict.fromkeys(warnings)),
    )
    return report, packets


def plan_wiki_main_ingest(repo_root: Path, changed_paths: list[str], run_id: str = "plan") -> IngestReport:
    report, _packets = _build_report(repo_root, changed_paths, run_id)
    return report


def run_wiki_main_ingest(
    repo_root: Path,
    changed_paths: list[str],
    report_path: Path | None = None,
    run_id: str = "run",
) -> IngestReport:
    report_path = report_path or _default_report_path(repo_root, run_id)
    report, packets = _build_report(repo_root, changed_paths, run_id)
    if report.status in {"skipped", "hard_fail"}:
        _write_report(repo_root, report, report_path)
        return report

    packet_roots = [repo_root / root for root in report.packet_roots]
    staging = _staged_subset(repo_root, packet_roots)
    shutil.rmtree(staging, ignore_errors=True)
    policy = load_policy(repo_root)
    rendered = render_packets(repo_root, packets, run_id=run_id, policy=policy)
    report.changed_paths = rendered.changed_paths
    link_errors = lint_wiki_links(repo_root, rendered.changed_paths)
    report.link_lint_errors = [as_jsonable(error) for error in link_errors]
    if link_errors:
        report.status = "hard_fail"
    _write_report(repo_root, report, report_path)
    return report
