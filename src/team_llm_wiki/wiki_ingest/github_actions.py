from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

MAX_COMMENT_CHARS = 60000
MAX_LIST_ITEMS = 25
MAX_FAILURE_MESSAGE_CHARS = 500
MAX_PATH_CHARS = 180
WIKI_BOT_PREFIX = "[wiki-bot]"


def _bounded_text(value: Any, limit: int = MAX_FAILURE_MESSAGE_CHARS) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _append_path_section(lines: list[str], title: str, paths: list[Any]) -> None:
    lines.extend(["", f"### {title}"])
    clean = [_bounded_text(path, MAX_PATH_CHARS) for path in paths if str(path).strip()]
    if not clean:
        lines.append("- none")
        return
    for path in clean[:MAX_LIST_ITEMS]:
        lines.append(f"- `{path}`")
    remaining = len(clean) - MAX_LIST_ITEMS
    if remaining > 0:
            lines.append(f"- and {remaining} more")


def _failure_line(failure: Any) -> str:
    if isinstance(failure, dict):
        code = failure.get("code", "unknown")
        message = _bounded_text(failure.get("message", ""))
    else:
        code = "unknown"
        message = _bounded_text(failure)
    return f"- `{code}` {message}".rstrip()


def _append_packet_type_section(lines: list[str], packets: list[Any]) -> None:
    lines.extend(["", "### Detected packet types"])
    clean = [packet for packet in packets if isinstance(packet, dict)]
    if not clean:
        lines.append("- none")
        return
    for packet in clean[:MAX_LIST_ITEMS]:
        packet_id = _bounded_text(packet.get("id", "unknown"), MAX_PATH_CHARS)
        packet_type = _bounded_text(packet.get("type", "unknown"), MAX_PATH_CHARS)
        risk = _bounded_text(packet.get("risk_tier", "unknown"), MAX_PATH_CHARS)
        lines.append(f"- `{packet_id}` {packet_type} (risk: `{risk}`)")
    remaining = len(clean) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- and {remaining} more")


def _append_claim_status_section(lines: list[str], payload: dict[str, Any]) -> None:
    lines.extend(["", "### Proposed claim statuses"])
    statuses = [item for item in payload.get("claim_statuses") or [] if isinstance(item, dict)]
    if not statuses:
        statuses = [
            {"packet": packet.get("id", "unknown"), "status": packet.get("claim_status", "unknown")}
            for packet in payload.get("packets") or []
            if isinstance(packet, dict) and packet.get("claim_status")
        ]
    if not statuses:
        lines.append("- none")
        return
    for item in statuses[:MAX_LIST_ITEMS]:
        packet_id = _bounded_text(item.get("packet", item.get("id", "unknown")), MAX_PATH_CHARS)
        status = _bounded_text(item.get("status", "unknown"), MAX_PATH_CHARS)
        lines.append(f"- `{packet_id}` `{status}`")
    remaining = len(statuses) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- and {remaining} more")


def _append_missing_evidence_section(lines: list[str], failures: list[Any]) -> None:
    lines.extend(["", "### Missing evidence"])
    missing = [
        failure
        for failure in failures
        if isinstance(failure, dict)
        and str(failure.get("code", "")) in {"missing_raw_file", "metric_mismatch", "invalid_manifest"}
    ]
    if not missing:
        lines.append("- none")
        return
    for failure in missing[:MAX_LIST_ITEMS]:
        lines.append(_failure_line(failure))
    remaining = len(missing) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- and {remaining} more")


def _append_review_question_section(lines: list[str], payload: dict[str, Any], failures: list[Any]) -> None:
    lines.extend(["", "### Expected PR review questions"])
    questions: list[str] = []
    questions.extend(str(warning) for warning in payload.get("warnings") or [] if str(warning).strip())
    for packet in payload.get("packets") or []:
        if not isinstance(packet, dict):
            continue
        for reason in packet.get("risk_reasons") or []:
            if str(reason).strip():
                questions.append(str(reason))
    if failures and not questions:
        questions.append("Resolve hard-fail items before merge.")
    if not questions:
        questions.append("Confirm the packet claim boundary and evidence are sufficient for the proposed status.")
    for question in list(dict.fromkeys(questions))[:MAX_LIST_ITEMS]:
        lines.append(f"- {_bounded_text(question)}")


def should_skip_wiki_ingest(actor: str, commit_message: str | None = None, pr_title: str | None = None) -> bool:
    if pr_title and pr_title.startswith(WIKI_BOT_PREFIX):
        return True
    return actor == "github-actions[bot]" and bool(commit_message and commit_message.startswith(WIKI_BOT_PREFIX))


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

    failures = list(payload.get("failures") or [])
    _append_packet_type_section(lines, list(payload.get("packets") or []))
    _append_path_section(lines, "Affected wiki pages", list(payload.get("generated_paths") or payload.get("changed_paths") or []))
    _append_claim_status_section(lines, payload)
    _append_missing_evidence_section(lines, failures)
    _append_review_question_section(lines, payload, failures)
    lines.extend(["", "### Failures"])
    if not failures:
        lines.append("- none")
    else:
        for failure in failures[:MAX_LIST_ITEMS]:
            lines.append(_failure_line(failure))
        remaining = len(failures) - MAX_LIST_ITEMS
        if remaining > 0:
            lines.append(f"- and {remaining} more")

    _append_path_section(lines, "Packet roots", list(payload.get("packet_roots") or []))
    _append_path_section(lines, "Generated paths", list(payload.get("generated_paths") or []))

    comment = "\n".join(lines).rstrip() + "\n"
    if len(comment) <= MAX_COMMENT_CHARS:
        return comment
    return comment[: MAX_COMMENT_CHARS - 80].rstrip() + "\n\n_Comment truncated to fit GitHub limits._\n"


def preview_payload_from_streams(raw_stdout: str, raw_stderr: str, run_id: str = "preview") -> dict[str, Any]:
    raw = raw_stdout.strip()
    error = raw_stderr.strip()
    payload: dict[str, Any] = {}
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                payload = parsed
            else:
                payload = {
                    "status": "hard_fail",
                    "failures": [{"code": "invalid_preview_json", "message": "preview stdout was not an object"}],
                }
        except json.JSONDecodeError:
            payload = {
                "status": "hard_fail",
                "failures": [{"code": "invalid_preview_json", "message": raw or "missing stdout"}],
            }
    if not payload and error:
        try:
            error_payload = json.loads(error)
            failure = error_payload.get("error", {"code": "preview_failed", "message": error})
            if not isinstance(failure, dict):
                failure = {"code": "preview_failed", "message": str(failure)}
            payload = {"status": "hard_fail", "failures": [failure]}
        except json.JSONDecodeError:
            payload = {"status": "hard_fail", "failures": [{"code": "preview_failed", "message": error}]}
    if not payload:
        payload = {"status": "hard_fail", "failures": [{"code": "missing_preview", "message": "preview produced no output"}]}
    payload.setdefault("run_id", run_id)
    return payload


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
