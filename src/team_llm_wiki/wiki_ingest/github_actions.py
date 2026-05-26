from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def add_paths_from_payload(payload: dict[str, Any]) -> list[str]:
    return [str(path) for path in payload.get("changed_paths", []) if str(path).strip()]


def workflow_dispatch_changed_paths(env: dict[str, str]) -> list[str]:
    raw = env.get("INPUT_CHANGED_PATHS", "")
    return [line.strip() for line in raw.splitlines() if line.strip()]


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
    if failures:
        lines.append(f"- failures: `{len(failures)}`")
    return "\n".join(lines) + "\n"
