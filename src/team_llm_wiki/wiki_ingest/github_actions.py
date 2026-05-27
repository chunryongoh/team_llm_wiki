from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

MAX_COMMENT_CHARS = 60000
MAX_LIST_ITEMS = 25
MAX_FAILURE_MESSAGE_CHARS = 500


def _bounded_text(value: Any, limit: int = MAX_FAILURE_MESSAGE_CHARS) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _append_path_section(lines: list[str], title: str, paths: list[Any]) -> None:
    lines.extend(["", f"### {title}"])
    clean = [str(path).strip() for path in paths if str(path).strip()]
    if not clean:
        lines.append("- none")
        return
    for path in clean[:MAX_LIST_ITEMS]:
        lines.append(f"- `{path}`")
    remaining = len(clean) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- and {remaining} more")


def render_pr_comment(payload: dict[str, Any]) -> str:
    status = payload.get("status", "unknown")
    lines = [
        "<!-- team-llm-wiki-preview -->",
        "## Wiki ingest preview",
        "",
        f"- status: `{status}`",
    ]
    if payload.get("run_id"):
        lines.append(f"- run id: `{payload['run_id']}`")
    if payload.get("timing_ms") is not None:
        lines.append(f"- timing: `{payload['timing_ms']} ms`")

    _append_path_section(lines, "Packet roots", list(payload.get("packet_roots") or []))
    _append_path_section(lines, "Generated paths", list(payload.get("generated_paths") or []))

    failures = list(payload.get("failures") or [])
    lines.extend(["", "### Failures"])
    if not failures:
        lines.append("- none")
    else:
        for failure in failures[:MAX_LIST_ITEMS]:
            if isinstance(failure, dict):
                code = failure.get("code", "unknown")
                message = _bounded_text(failure.get("message", ""))
            else:
                code = "unknown"
                message = _bounded_text(failure)
            lines.append(f"- `{code}` {message}".rstrip())
        remaining = len(failures) - MAX_LIST_ITEMS
        if remaining > 0:
            lines.append(f"- and {remaining} more")

    comment = "\n".join(lines).rstrip() + "\n"
    if len(comment) <= MAX_COMMENT_CHARS:
        return comment
    return comment[: MAX_COMMENT_CHARS - 80].rstrip() + "\n\n_Comment truncated to fit GitHub limits._\n"


def add_paths_from_payload(payload: dict[str, Any]) -> list[str]:
    paths = list(payload.get("generated_paths") or payload.get("changed_paths") or [])
    report_path = payload.get("report_path")
    if report_path:
        paths.append(str(report_path))
    return list(dict.fromkeys(str(path) for path in paths if str(path).strip()))


def workflow_dispatch_changed_paths(env: dict[str, str], repo_root: Path | None = None) -> list[str]:
    raw = env.get("INPUT_CHANGED_PATHS", "")
    paths = [line.strip() for line in raw.splitlines() if line.strip()]
    if paths or repo_root is None:
        return paths
    try:
        result = subprocess.run(
            ["git", "ls-files", "raw/users/**/manifest.yaml"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=True,
        )
        tracked = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if tracked:
            return sorted(tracked)
    except (OSError, subprocess.CalledProcessError):
        pass
    return sorted(path.relative_to(repo_root).as_posix() for path in (repo_root / "raw" / "users").glob("*/*/manifest.yaml"))


def safe_add_paths_file_from_payload(payload: dict[str, Any], path: Path) -> list[str]:
    paths = add_paths_from_payload(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(paths) + ("\n" if paths else ""), encoding="utf-8")
    return paths


def write_github_outputs(path: Path, outputs: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for key, value in outputs.items():
        if "\n" in value:
            lines.extend([f"{key}<<EOF", value, "EOF"])
        else:
            lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_workflow_summary(ingest_output: str | None) -> str:
    if not ingest_output:
        return "## Wiki ingest\n\nMissing ingest output; no machine-readable report was produced.\n"
    try:
        payload = json.loads(ingest_output)
    except json.JSONDecodeError:
        return "## Wiki ingest\n\nMissing ingest output; CLI output was not JSON.\n"
    status = payload.get("status", "unknown")
    changed = payload.get("changed_paths", [])
    failures = payload.get("failures", [])
    lines = ["## Wiki ingest", "", f"- status: `{status}`", f"- changed paths: `{len(changed)}`"]
    if payload.get("report_path"):
        lines.append(f"- report: `{payload['report_path']}`")
    if failures:
        lines.append(f"- failures: `{len(failures)}`")
        for failure in failures[:10]:
            code = failure.get("code", "unknown") if isinstance(failure, dict) else "unknown"
            message = failure.get("message", "") if isinstance(failure, dict) else str(failure)
            lines.append(f"  - `{code}` {message}".rstrip())
    return "\n".join(lines) + "\n"
