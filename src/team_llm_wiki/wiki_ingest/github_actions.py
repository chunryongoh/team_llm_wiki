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
        lines.append("- 없음")
        return
    for path in clean[:MAX_LIST_ITEMS]:
        lines.append(f"- `{path}`")
    remaining = len(clean) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- 외 {remaining}개 더")


def _packet_ids_from_payload(payload: dict[str, Any]) -> list[str]:
    ids = [
        _bounded_text(packet.get("id"), MAX_PATH_CHARS)
        for packet in payload.get("packets") or []
        if isinstance(packet, dict) and str(packet.get("id", "")).strip()
    ]
    if ids:
        return list(dict.fromkeys(ids))
    roots = []
    for root in payload.get("packet_roots") or []:
        path = str(root).strip().rstrip("/")
        if path:
            roots.append(_bounded_text(Path(path).name, MAX_PATH_CHARS))
    return list(dict.fromkeys(roots))


def _failure_line(failure: Any) -> str:
    if isinstance(failure, dict):
        code = failure.get("code", "unknown")
        message = _bounded_text(failure.get("message", ""))
    else:
        code = "unknown"
        message = _bounded_text(failure)
    return f"- `{code}` {message}".rstrip()


def _append_packet_type_section(lines: list[str], packets: list[Any]) -> None:
    lines.extend(["", "### 감지된 packet"])
    clean = [packet for packet in packets if isinstance(packet, dict)]
    if not clean:
        lines.append("- 없음")
        return
    for packet in clean[:MAX_LIST_ITEMS]:
        packet_id = _bounded_text(packet.get("id", "unknown"), MAX_PATH_CHARS)
        packet_type = _bounded_text(packet.get("type", "unknown"), MAX_PATH_CHARS)
        publish_action = _bounded_text(packet.get("publish_action", "unknown"), MAX_PATH_CHARS)
        risk = _bounded_text(packet.get("risk_tier", "unknown"), MAX_PATH_CHARS)
        boundary = _bounded_text(packet.get("claim_boundary", "unknown"), MAX_PATH_CHARS)
        lines.append(
            f"- `{packet_id}` {packet_type} "
            f"(publish: `{publish_action}`, risk: `{risk}`, claim_boundary: `{boundary}`)"
        )
    remaining = len(clean) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- 외 {remaining}개 더")


def _append_claim_status_section(lines: list[str], payload: dict[str, Any]) -> None:
    lines.extend(["", "### 제안된 claim 상태"])
    statuses = [item for item in payload.get("claim_statuses") or [] if isinstance(item, dict)]
    if not statuses:
        statuses = [
            {"packet": packet.get("id", "unknown"), "status": packet.get("claim_status", "unknown")}
            for packet in payload.get("packets") or []
            if isinstance(packet, dict) and packet.get("claim_status")
        ]
    if not statuses:
        lines.append("- 없음")
        return
    for item in statuses[:MAX_LIST_ITEMS]:
        packet_id = _bounded_text(item.get("packet", item.get("id", "unknown")), MAX_PATH_CHARS)
        status = _bounded_text(item.get("status", "unknown"), MAX_PATH_CHARS)
        lines.append(f"- `{packet_id}` `{status}`")
    remaining = len(statuses) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- 외 {remaining}개 더")


def _append_missing_evidence_section(lines: list[str], failures: list[Any]) -> None:
    lines.extend(["", "### 누락되었거나 확인할 evidence"])
    missing = [
        failure
        for failure in failures
        if isinstance(failure, dict)
        and str(failure.get("code", "")) in {"missing_raw_file", "metric_mismatch", "invalid_manifest"}
    ]
    if not missing:
        lines.append("- 없음")
        return
    for failure in missing[:MAX_LIST_ITEMS]:
        lines.append(_failure_line(failure))
    remaining = len(missing) - MAX_LIST_ITEMS
    if remaining > 0:
        lines.append(f"- 외 {remaining}개 더")


def _append_review_question_section(lines: list[str], payload: dict[str, Any], failures: list[Any]) -> None:
    lines.extend(["", "### 팀원이 확인할 것"])
    questions: list[str] = []
    questions.extend(str(warning) for warning in payload.get("warnings") or [] if str(warning).strip())
    for packet in payload.get("packets") or []:
        if not isinstance(packet, dict):
            continue
        for reason in packet.get("risk_reasons") or []:
            if str(reason).strip():
                questions.append(str(reason))
    if failures and not questions:
        questions.append("merge 전 hard-fail 항목을 해결해야 합니다.")
    if not questions:
        questions.append("packet claim boundary와 evidence가 제안된 claim 상태에 충분한지 확인합니다.")
    for question in list(dict.fromkeys(questions))[:MAX_LIST_ITEMS]:
        lines.append(f"- {_bounded_text(question)}")


def should_skip_wiki_ingest(actor: str, commit_message: str | None = None, pr_title: str | None = None) -> bool:
    if pr_title and pr_title.startswith(WIKI_BOT_PREFIX):
        return True
    return actor == "github-actions[bot]" and bool(commit_message and commit_message.startswith(WIKI_BOT_PREFIX))


def render_pr_comment(payload: dict[str, Any]) -> str:
    status = payload.get("status", "unknown")
    compatibility = payload.get("packet_skill_compatibility") or {}
    compatibility_status = compatibility.get("status", "unknown") if isinstance(compatibility, dict) else "unknown"
    lines = [
        "<!-- team-llm-wiki-preview -->",
        "## Packet 검증 결과",
        "",
        f"- 상태: `{status}`",
        f"- merge 후 다음 단계: deterministic ingest -> GPT-5.5 synthesis PR",
        f"- packet skill compatibility: `{compatibility_status}`",
    ]
    if payload.get("run_id"):
        lines.append(f"- run id: `{payload['run_id']}`")
    if payload.get("timing_ms") is not None:
        lines.append(f"- timing: `{payload['timing_ms']} ms`")

    failures = list(payload.get("failures") or [])
    _append_packet_type_section(lines, list(payload.get("packets") or []))
    _append_path_section(lines, "영향받을 wiki 페이지", list(payload.get("generated_paths") or payload.get("changed_paths") or []))
    _append_claim_status_section(lines, payload)
    _append_compatibility_section(lines, compatibility)
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
            lines.append(f"- 외 {remaining}개 더")

    _append_path_section(lines, "Packet roots", list(payload.get("packet_roots") or []))
    _append_path_section(lines, "Generated paths", list(payload.get("generated_paths") or []))

    comment = "\n".join(lines).rstrip() + "\n"
    if len(comment) <= MAX_COMMENT_CHARS:
        return comment
    return comment[: MAX_COMMENT_CHARS - 80].rstrip() + "\n\n_Comment truncated to fit GitHub limits._\n"


def _append_compatibility_section(lines: list[str], compatibility: Any) -> None:
    if not isinstance(compatibility, dict) or not compatibility:
        return
    checks = [check for check in compatibility.get("checks") or [] if isinstance(check, dict)]
    if not checks:
        return
    lines.extend(["", "### Packet skill compatibility checks"])
    for check in checks[:MAX_LIST_ITEMS]:
        check_id = _bounded_text(check.get("id", "unknown"), MAX_PATH_CHARS)
        status = _bounded_text(check.get("status", "unknown"), MAX_PATH_CHARS)
        message = _bounded_text(check.get("message", ""))
        packet_root = check.get("packet_root")
        suffix = f" ({_bounded_text(packet_root, MAX_PATH_CHARS)})" if packet_root else ""
        lines.append(f"- `{check_id}` `{status}` {message}{suffix}".rstrip())


def render_bot_pr_body(payload: dict[str, Any]) -> str:
    lines = ["## 생성 리포트", ""]
    report_path = payload.get("report_path")
    if report_path:
        lines.append(f"- `{_bounded_text(report_path, MAX_PATH_CHARS)}`")
    else:
        lines.append("- 없음")

    lines.extend(["", "## 반영된 raw packet", ""])
    packet_ids = _packet_ids_from_payload(payload)
    if packet_ids:
        lines.extend(f"- `{packet_id}`" for packet_id in packet_ids[:MAX_LIST_ITEMS])
    else:
        lines.append("- 없음")

    _append_bot_compatibility_section(lines, payload.get("packet_skill_compatibility"))

    if payload.get("llm_synthesis"):
        lines.extend(["", "## LLM 통합 정리", ""])
        summary = payload.get("synthesis_summary") or payload.get("summary") or "없음"
        lines.append(_bounded_text(summary, 1000))
        integration_plan = [item for item in payload.get("integration_plan") or [] if str(item).strip()]
        if integration_plan:
            lines.extend(["", "### 통합 계획"])
            lines.extend(f"- {_bounded_text(item, 300)}" for item in integration_plan[:MAX_LIST_ITEMS])
        _append_path_section(lines, "새로 생성된 wiki 페이지", list(payload.get("created_pages") or []))
        _append_path_section(lines, "수정된 wiki 페이지", list(payload.get("updated_pages") or []))
        open_questions = [item for item in payload.get("open_questions") or [] if item]
        if open_questions:
            lines.extend(["", "### 확인해야 할 질문"])
            lines.extend(_open_question_line(item) for item in open_questions[:MAX_LIST_ITEMS])
        conflicts = [item for item in payload.get("superseded_or_conflicting_claims") or [] if str(item).strip()]
        if conflicts:
            lines.extend(["", "### 충돌하거나 대체된 claim"])
            lines.extend(f"- {_bounded_text(item, 300)}" for item in conflicts[:MAX_LIST_ITEMS])

    lines.extend(["", "## 영향받은 wiki 페이지", ""])
    wiki_paths = [path for path in payload.get("generated_paths") or payload.get("changed_paths") or [] if str(path).startswith("wiki/")]
    if wiki_paths:
        lines.extend(f"- `{_bounded_text(path, MAX_PATH_CHARS)}`" for path in wiki_paths[:MAX_LIST_ITEMS])
    else:
        lines.append("- 없음")

    lines.extend(["", "## claim 상태 변경", ""])
    claim_statuses = list(payload.get("claim_statuses") or [])
    if claim_statuses:
        for item in claim_statuses[:MAX_LIST_ITEMS]:
            if isinstance(item, dict):
                packet = _bounded_text(item.get("packet", item.get("id", "unknown")), MAX_PATH_CHARS)
                status = _bounded_text(item.get("status", "unknown"), MAX_PATH_CHARS)
                lines.append(f"- `{packet}` `{status}`")
            else:
                lines.append(f"- {_bounded_text(item)}")
    else:
        lines.append("- 없음")

    lines.extend(["", "## metric 변경", ""])
    metric_changes = list(payload.get("metric_changes") or [])
    if metric_changes:
        for item in metric_changes[:MAX_LIST_ITEMS]:
            if isinstance(item, dict):
                packet = _bounded_text(item.get("packet", "unknown"), MAX_PATH_CHARS)
                metric = _bounded_text(item.get("metric", "unknown"), MAX_PATH_CHARS)
                value = _bounded_text(item.get("reported_value", "unknown"), MAX_PATH_CHARS)
                lines.append(f"- `{packet}` `{metric}` = `{value}`")
            else:
                lines.append(f"- {_bounded_text(item)}")
    else:
        lines.append("- 없음")

    lines.extend(["", "## leakage/security 경고", ""])
    warnings = list(payload.get("warnings") or [])
    security_failures = [
        failure
        for failure in payload.get("failures") or []
        if isinstance(failure, dict)
        and str(failure.get("code", "")) in {"secret_content", "pii_content", "forbidden_secret_file", "model_weight_file"}
    ]
    if warnings or security_failures:
        lines.extend(f"- {_bounded_text(warning)}" for warning in warnings[:MAX_LIST_ITEMS])
        lines.extend(_failure_line(failure) for failure in security_failures[:MAX_LIST_ITEMS])
    else:
        lines.append("- 없음")

    _append_validation_section(lines, payload.get("validation"))

    lines.extend(
        [
            "",
            "## 리뷰어 체크리스트",
            "",
            "- [ ] 반영된 raw packet과 영향받은 wiki 페이지가 예상 범위인지 확인합니다.",
            "- [ ] claim 상태 변경이 raw evidence로 뒷받침되는지 확인합니다.",
            "- [ ] metric 변경이 참조한 raw result 파일과 일치하는지 확인합니다.",
            "- [ ] leakage, security, PII 경고가 남아 있지 않은지 확인합니다.",
        ]
    )
    body = "\n".join(lines).rstrip() + "\n"
    if len(body) <= MAX_COMMENT_CHARS:
        return body
    return body[: MAX_COMMENT_CHARS - 80].rstrip() + "\n\n_Body truncated to fit GitHub limits._\n"


def _append_bot_compatibility_section(lines: list[str], compatibility: Any) -> None:
    if not isinstance(compatibility, dict) or not compatibility:
        return
    lines.extend(["", "## packet skill 입력과의 연결", ""])
    lines.append(f"- compatibility: `{_bounded_text(compatibility.get('status', 'unknown'), MAX_PATH_CHARS)}`")
    checks = [check for check in compatibility.get("checks") or [] if isinstance(check, dict)]
    for check in checks[:MAX_LIST_ITEMS]:
        lines.append(
            f"- `{_bounded_text(check.get('id', 'unknown'), MAX_PATH_CHARS)}` "
            f"`{_bounded_text(check.get('status', 'unknown'), MAX_PATH_CHARS)}` "
            f"{_bounded_text(check.get('message', ''))}".rstrip()
        )


def _open_question_line(item: Any) -> str:
    if not isinstance(item, dict):
        return f"- {_bounded_text(item, 300)}"
    question_id = _bounded_text(item.get("id", "unknown"), MAX_PATH_CHARS)
    priority = _bounded_text(item.get("priority", "unknown"), MAX_PATH_CHARS)
    owner = _bounded_text(item.get("owner_role", "unknown"), MAX_PATH_CHARS)
    blocker = _bounded_text(item.get("merge_blocker", "unknown"), MAX_PATH_CHARS)
    question = _bounded_text(item.get("question", ""), 240)
    evidence = _bounded_text(item.get("needed_evidence", ""), 240)
    close = _bounded_text(item.get("close_condition", ""), 240)
    return (
        f"- `{question_id}` priority=`{priority}` owner=`{owner}` merge_blocker=`{blocker}`: {question} "
        f"needed_evidence=`{evidence}` close_condition=`{close}`"
    ).rstrip()


def _append_validation_section(lines: list[str], validation: Any) -> None:
    lines.extend(["", "## 자동 검증 결과", ""])
    if not isinstance(validation, dict) or not validation:
        lines.append("- 없음")
        return
    lines.append(f"- status: `{_bounded_text(validation.get('status', 'unknown'), MAX_PATH_CHARS)}`")
    checks = [check for check in validation.get("checks") or [] if isinstance(check, dict)]
    if not checks:
        lines.append("- checks: 없음")
        return
    for check in checks[:MAX_LIST_ITEMS]:
        check_id = _bounded_text(check.get("id", "unknown"), MAX_PATH_CHARS)
        status = _bounded_text(check.get("status", "unknown"), MAX_PATH_CHARS)
        summary = _bounded_text(check.get("summary", ""), 300)
        command = _bounded_text(check.get("command", ""), 300)
        lines.append(f"- `{check_id}` `{status}` {summary} (`{command}`)".rstrip())


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


def validation_payload_from_outputs(
    *,
    health_stdout: str,
    health_stderr: str,
    health_status: int,
    health_command: str,
    pytest_stdout: str,
    pytest_status: int,
    pytest_command: str,
) -> dict[str, Any]:
    checks = [
        {
            "id": "wiki_health",
            "status": "pass" if health_status == 0 else "fail",
            "command": health_command,
            "summary": _health_summary(health_stdout, health_stderr),
            "exit_status": health_status,
        },
        {
            "id": "targeted_pytest",
            "status": "pass" if pytest_status == 0 else "fail",
            "command": pytest_command,
            "summary": _last_nonempty_line(pytest_stdout) or "no pytest output",
            "exit_status": pytest_status,
        },
    ]
    status = "fail" if any(check["status"] == "fail" for check in checks) else "pass"
    return {"status": status, "checks": checks}


def _health_summary(stdout: str, stderr: str) -> str:
    raw = stdout.strip()
    if raw:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return _last_nonempty_line(raw) or "health output was not JSON"
        if isinstance(payload, dict):
            ok = payload.get("ok")
            errors = payload.get("errors") or []
            if ok is True:
                return "ok"
            return f"errors={len(errors)}"
    return _last_nonempty_line(stderr) or "no health output"


def _last_nonempty_line(text: str) -> str:
    for line in reversed(text.splitlines()):
        if line.strip():
            return _bounded_text(line.strip(), 300)
    return ""


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
