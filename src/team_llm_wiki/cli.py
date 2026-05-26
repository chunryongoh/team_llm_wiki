from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .wiki_ingest.health import check_wiki_health
from .wiki_ingest.manifest import read_changed_paths_file
from .wiki_ingest.models import IngestFailure, as_jsonable
from .wiki_ingest.runner import plan_wiki_main_ingest, run_wiki_main_ingest


def _changed_paths(args: argparse.Namespace) -> list[str]:
    paths = list(args.changed_path or [])
    if args.changed_path_file:
        paths.extend(read_changed_paths_file(Path(args.changed_path_file)))
    return paths


def _print_json(payload: object, stream) -> None:
    print(json.dumps(as_jsonable(payload), indent=2, sort_keys=True), file=stream)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="team-llm-wiki")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan-wiki-main-ingest")
    plan.add_argument("--repo-root", required=True)
    plan.add_argument("--changed-path", action="append")
    plan.add_argument("--changed-path-file")
    plan.add_argument("--run-id", default="plan")

    run = sub.add_parser("run-wiki-main-ingest")
    run.add_argument("--repo-root", required=True)
    run.add_argument("--changed-path", action="append")
    run.add_argument("--changed-path-file")
    run.add_argument("--report-path")
    run.add_argument("--run-id", default="run")

    health = sub.add_parser("check-wiki-health")
    health.add_argument("--repo-root", required=True)
    health.add_argument("--report-path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "plan-wiki-main-ingest":
            report = plan_wiki_main_ingest(Path(args.repo_root), _changed_paths(args), run_id=args.run_id)
            _print_json(report, sys.stdout)
            return 0
        if args.command == "run-wiki-main-ingest":
            report = run_wiki_main_ingest(
                Path(args.repo_root),
                _changed_paths(args),
                report_path=Path(args.report_path) if args.report_path else None,
                run_id=args.run_id,
            )
            _print_json(report, sys.stdout)
            return 0
        if args.command == "check-wiki-health":
            report = check_wiki_health(Path(args.repo_root), Path(args.report_path) if args.report_path else None)
            _print_json(report, sys.stdout)
            return 0 if report.ok else 1
    except IngestFailure as exc:
        _print_json({"error": exc.to_dict()}, sys.stderr)
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
