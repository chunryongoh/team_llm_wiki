from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
from typing import Any
from urllib import error, request

from .health import check_wiki_health
from .links import lint_wiki_links
from .manifest import discover_packet_roots, load_packet_manifest, validate_changed_paths
from .models import FailureCode, IngestFailure, IngestReport, PacketManifest, PacketType, RiskTierLabel, as_jsonable
from .policy import load_policy
from .render import render_target_path

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_MAX_OUTPUT_TOKENS = 20000
DEFAULT_BASE_URL = "https://api.openai.com/v1"
MAX_CONTEXT_FILE_CHARS = 120_000


class OpenAIResponsesClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.max_output_tokens = max_output_tokens

    def synthesize(self, *, model: str, reasoning_effort: str, prompt: str) -> dict[str, Any]:
        if not self.api_key:
            raise IngestFailure(FailureCode.MISSING_API_KEY, "OPENAI_API_KEY is required for LLM synthesis")
        payload = {
            "model": model,
            "reasoning": {"effort": reasoning_effort},
            "max_output_tokens": self.max_output_tokens,
            "text": {"format": _response_schema()},
            "input": [
                {
                    "role": "system",
                    "content": (
                        "You are the Team LLM Wiki synthesis engine. Rewrite only the allowed wiki pages. "
                        "Follow AGENTS.md and CLAUDE.md exactly. Preserve claim statuses unless raw evidence "
                        "proves a change. Return only the requested JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}/responses",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=600) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise IngestFailure(
                FailureCode.LLM_SYNTHESIS_FAILED,
                f"OpenAI Responses API failed with HTTP {exc.code}",
                {"body": body[:2000]},
            ) from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise IngestFailure(FailureCode.LLM_SYNTHESIS_FAILED, str(exc)) from exc
        output_text = _extract_output_text(response_payload)
        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise IngestFailure(
                FailureCode.INVALID_LLM_OUTPUT,
                "LLM output was not valid JSON",
                {"output_text": output_text[:2000]},
            ) from exc
        return parsed if isinstance(parsed, dict) else {}


def run_llm_wiki_synthesis(
    repo_root: Path,
    changed_paths: list[str],
    *,
    report_path: Path | None = None,
    run_id: str = "llm-synthesis",
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    client: Any | None = None,
) -> IngestReport:
    start = time.monotonic()
    repo_root = repo_root.resolve()
    input_changed_paths = validate_changed_paths(repo_root, changed_paths)
    packet_roots = _resolve_packet_roots(repo_root, input_changed_paths)
    if not packet_roots:
        return IngestReport(
            status="skipped",
            run_id=run_id,
            input_changed_paths=input_changed_paths,
            llm_synthesis=True,
            model=model,
            timing_ms=int((time.monotonic() - start) * 1000),
        )
    load_policy(repo_root)
    manifests = [(load_packet_manifest(root), root) for root in packet_roots]
    target_paths = _target_paths(manifests)
    evidence_by_target = _raw_evidence_by_target(repo_root, manifests, target_paths)
    prompt = build_llm_synthesis_prompt(repo_root, manifests, target_paths)
    synthesis_client = client or OpenAIResponsesClient()
    llm_payload = synthesis_client.synthesize(model=model, reasoning_effort=reasoning_effort, prompt=prompt)
    pages = _validated_pages(llm_payload, allowed_paths=set(target_paths), required_paths=set(target_paths))
    changed: list[str] = []
    staging = _staged_wiki(repo_root)
    try:
        for page in pages:
            target = staging / page["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            content = _finalize_page_content(
                repo_root,
                page["path"],
                page["content"],
                evidence_by_target.get(page["path"], []),
            )
            target.write_text(content.rstrip() + "\n", encoding="utf-8")
            changed.append(page["path"])
        link_errors = lint_wiki_links(staging, changed)
        health = check_wiki_health(staging)
        failures = [as_jsonable(error) for error in link_errors]
        if not health.ok:
            failures.extend(as_jsonable(error) for error in health.errors)
        if not failures:
            for rel in changed:
                source = staging / rel
                target = repo_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    status = "hard_fail" if failures else "bot_pr"
    report = IngestReport(
        status=status,
        run_id=run_id,
        input_changed_paths=input_changed_paths,
        packet_roots=[_rel(repo_root, root) for root in packet_roots],
        packets=[
            {"id": manifest.id, "type": manifest.type.value, "packet_root": _rel(repo_root, root)}
            for manifest, root in manifests
        ],
        failures=failures,
        generated_paths=list(changed),
        changed_paths=list(changed),
        risk_tier=RiskTierLabel.TIER4_GOVERNANCE.value if failures or _has_governance_targets(changed) else RiskTierLabel.TIER2_INTERPRETATION.value,
        timing_ms=int((time.monotonic() - start) * 1000),
        llm_synthesis=True,
        model=model,
        review_notes=[str(note) for note in llm_payload.get("review_notes") or []],
        synthesis_summary=str(llm_payload.get("summary", "")),
        integration_plan=[str(item) for item in llm_payload.get("integration_plan") or []],
        created_pages=[str(item) for item in llm_payload.get("created_pages") or []],
        updated_pages=[str(item) for item in llm_payload.get("updated_pages") or []],
        claim_register=[item for item in llm_payload.get("claim_register") or [] if isinstance(item, dict)],
        open_questions=[str(item) for item in llm_payload.get("open_questions") or []],
        superseded_or_conflicting_claims=[
            str(item) for item in llm_payload.get("superseded_or_conflicting_claims") or []
        ],
    )
    report_path = report_path or repo_root / "raw" / "results" / "llm-synthesis" / run_id / "report.json"
    _write_report(repo_root, report, report_path)
    if report.report_path and report.report_path not in report.generated_paths:
        report.generated_paths.append(report.report_path)
        report.changed_paths.append(report.report_path)
    return report


def build_llm_synthesis_prompt(
    repo_root: Path,
    manifests: list[tuple[PacketManifest, Path]],
    target_paths: list[str],
) -> str:
    files: list[str] = []
    files.append(_file_block(repo_root, "AGENTS.md"))
    for rel in ["CLAUDE.md", "wiki/index.md", "wiki/overview.md", "wiki/latest-context.md", "wiki/log.md"]:
        files.append(_file_block(repo_root, rel, missing_ok=True))
    files.append(_file_block(repo_root, "wiki/team/llm-synthesis-policy.md", missing_ok=True))
    for manifest, packet_root in manifests:
        files.extend(_packet_file_blocks(repo_root, packet_root))
    for rel in target_paths:
        files.append(_file_block(repo_root, rel, missing_ok=True))
    allowed = "\n".join(f"- {path}" for path in target_paths)
    return (
        "Run a Karpathy-style LLM wiki integration pass. A new source may update many wiki pages: "
        "stable entities, topic synthesis pages, decisions, open questions, reports, index, log, "
        "latest context, and overview. Do not behave like a formatter that rewrites only packet mirrors.\n\n"
        "Requirements:\n"
        "- Read and obey AGENTS.md and CLAUDE.md.\n"
        "- Use stable entity pages plus compounding topic pages, not dated packet mirrors.\n"
        "- Write every allowed output page exactly once; missing pages are invalid output.\n"
        "- Cross-link related dataset, benchmark, feature, decision, question, and report pages.\n"
        "- Capture contradictions, supersession notes, and unresolved questions as first-class wiki content.\n"
        "- Preserve raw provenance, packet ids, claim boundaries, and claim statuses.\n"
        "- Do not write raw/, automation/, or policy files.\n"
        "- Do not promote tentative claims to supported without explicit raw metric/split evidence.\n"
        "- Return JSON with keys: summary, integration_plan, created_pages, updated_pages, claim_register, "
        "open_questions, superseded_or_conflicting_claims, review_notes, pages.\n\n"
        "Allowed output pages:\n"
        f"{allowed}\n\n"
        "Context files:\n\n"
        + "\n\n".join(files)
    )


def _resolve_packet_roots(repo_root: Path, changed_paths: list[str]) -> list[Path]:
    roots = discover_packet_roots(repo_root, changed_paths)
    seen = {root.resolve() for root in roots}
    for rel in changed_paths:
        if not rel.startswith("raw/results/wiki-ingest/") or not rel.endswith("/report.json"):
            continue
        report_path = repo_root / rel
        if not report_path.exists():
            continue
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for packet_root in payload.get("packet_roots") or []:
            root = (repo_root / str(packet_root)).resolve()
            if root.is_dir() and root not in seen:
                roots.append(root)
                seen.add(root)
    return roots


def _target_paths(manifests: list[tuple[PacketManifest, Path]]) -> list[str]:
    entity_paths = [render_target_path(manifest, packet_root) for manifest, packet_root in manifests]
    return list(dict.fromkeys([*entity_paths, *_integration_paths(manifests)]))


def _validated_pages(
    payload: dict[str, Any],
    *,
    allowed_paths: set[str],
    required_paths: set[str] | None = None,
) -> list[dict[str, str]]:
    pages = payload.get("pages")
    if not isinstance(pages, list) or not pages:
        raise IngestFailure(FailureCode.INVALID_LLM_OUTPUT, "LLM output must include at least one page")
    clean: list[dict[str, str]] = []
    for page in pages:
        if not isinstance(page, dict):
            raise IngestFailure(FailureCode.INVALID_LLM_OUTPUT, "LLM page entries must be mappings")
        raw_path = page.get("path")
        content = page.get("content")
        if not isinstance(raw_path, str) or not isinstance(content, str) or not content.strip():
            raise IngestFailure(FailureCode.INVALID_LLM_OUTPUT, "LLM page path and content are required")
        path = Path(raw_path)
        rel = path.as_posix()
        if path.is_absolute() or ".." in path.parts or not rel.startswith("wiki/"):
            raise IngestFailure(FailureCode.INVALID_TARGET_ROUTE, f"LLM may only write wiki pages: {raw_path}")
        if rel not in allowed_paths:
            raise IngestFailure(FailureCode.INVALID_TARGET_ROUTE, f"LLM wrote an unapproved wiki path: {raw_path}")
        clean.append({"path": rel, "content": content})
    required_paths = required_paths or set()
    present = {page["path"] for page in clean}
    missing = sorted(required_paths - present)
    if missing:
        raise IngestFailure(
            FailureCode.INVALID_LLM_OUTPUT,
            "LLM output omitted required wiki integration pages",
            {"missing_paths": missing},
        )
    return clean


def _packet_file_blocks(repo_root: Path, packet_root: Path) -> list[str]:
    blocks: list[str] = []
    for path in sorted(item for item in packet_root.rglob("*") if item.is_file()):
        blocks.append(_file_block(repo_root, _rel(repo_root, path)))
    return blocks


def _staged_wiki(repo_root: Path) -> Path:
    staging = Path(tempfile.mkdtemp(prefix="llm-wiki-synthesis-stage-"))
    for rel in ["wiki", "docs", "automation"]:
        source = repo_root / rel
        target = staging / rel
        if source.exists():
            shutil.copytree(source, target)
        elif rel == "wiki":
            target.mkdir(parents=True)
    return staging


def _raw_evidence_by_target(
    repo_root: Path,
    manifests: list[tuple[PacketManifest, Path]],
    target_paths: list[str],
) -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {}
    all_evidence: list[str] = []
    for manifest, packet_root in manifests:
        paths = [packet_root / "manifest.yaml"]
        raw_paths = manifest.raw_paths.values() if isinstance(manifest.raw_paths, dict) else manifest.raw_paths
        for raw_path in raw_paths:
            paths.append(packet_root / raw_path)
        packet_md = packet_root / "packet.md"
        if packet_md.exists():
            paths.append(packet_md)
        seen: list[str] = []
        for path in paths:
            rel = _rel(repo_root, path)
            if rel not in seen:
                seen.append(rel)
            if rel not in all_evidence:
                all_evidence.append(rel)
        evidence[render_target_path(manifest, packet_root)] = seen
    for target_path in target_paths:
        evidence.setdefault(target_path, all_evidence)
    return evidence


def _integration_paths(manifests: list[tuple[PacketManifest, Path]]) -> list[str]:
    topic = _topic_slug(manifests)
    date_slug = _source_date_slug(manifests)
    has_benchmark = any(manifest.type is PacketType.BENCHMARK for manifest, _root in manifests)
    report_slug = f"{date_slug}-{topic}-{'benchmark' if has_benchmark else 'packet'}-synthesis"
    return [
        f"wiki/features/{topic}-feature-landscape.md",
        f"wiki/decisions/{topic}-evaluation-protocol.md",
        f"wiki/questions/{topic}-open-questions.md",
        f"wiki/reports/{report_slug}.md",
        "wiki/overview.md",
        "wiki/latest-context.md",
        "wiki/index.md",
        "wiki/log.md",
    ]


def _topic_slug(manifests: list[tuple[PacketManifest, Path]]) -> str:
    for manifest, _root in manifests:
        dataset_name = getattr(manifest.dataset, "name", "")
        if dataset_name:
            return re.sub(r"-20\d{2}$", "", _slugify(dataset_name)) or _slugify(dataset_name)
    return _slugify(manifests[0][0].id if manifests else "wiki-integration")


def _source_date_slug(manifests: list[tuple[PacketManifest, Path]]) -> str:
    dates = sorted(str(manifest.date) for manifest, _root in manifests if str(manifest.date).strip())
    return _slugify(dates[0]) if dates else "undated"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "wiki-integration"


def _has_governance_targets(paths: list[str]) -> bool:
    prefixes = ("wiki/decisions/", "wiki/questions/", "wiki/reports/", "wiki/index.md", "wiki/log.md", "wiki/overview.md")
    return any(path.startswith(prefixes) for path in paths)


def _ensure_raw_evidence(content: str, evidence_paths: list[str]) -> str:
    if not evidence_paths or "raw_evidence:" in content:
        return content
    lines = content.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                evidence_lines = ["raw_evidence:", *(f"- {path}" for path in evidence_paths)]
                return "\n".join([*lines[:index], *evidence_lines, *lines[index:]]) + ("\n" if content.endswith("\n") else "")
    evidence_block = "\n".join(["## Raw Evidence", "", "raw_evidence:", *(f"- {path}" for path in evidence_paths)])
    return content.rstrip() + "\n\n" + evidence_block + ("\n" if content.endswith("\n") else "")


def _finalize_page_content(repo_root: Path, rel_path: str, content: str, evidence_paths: list[str]) -> str:
    if rel_path == "wiki/log.md":
        return _merge_append_only_log(repo_root, content)
    if rel_path in {"wiki/index.md", "wiki/latest-context.md"}:
        return content
    return _ensure_raw_evidence(content, evidence_paths)


def _merge_append_only_log(repo_root: Path, content: str) -> str:
    existing_path = repo_root / "wiki" / "log.md"
    if not existing_path.exists():
        return content
    existing = existing_path.read_text(encoding="utf-8").rstrip()
    candidate = content.rstrip()
    if not existing or candidate.startswith(existing):
        return content
    new_entries = _extract_log_entries(candidate)
    if not new_entries:
        raise IngestFailure(
            FailureCode.INVALID_LLM_OUTPUT,
            "LLM log output must preserve existing wiki/log.md content or include appendable log entries",
            {"path": "wiki/log.md"},
        )
    existing_headings = {_entry_heading(entry) for entry in _extract_log_entries(existing)}
    appendable = [entry for entry in new_entries if _entry_heading(entry) not in existing_headings]
    if not appendable:
        return existing + "\n"
    return existing + "\n\n" + "\n\n".join(entry.rstrip() for entry in appendable) + "\n"


def _extract_log_entries(content: str) -> list[str]:
    matches = list(re.finditer(r"(?m)^## \[\d{4}-\d{2}-\d{2}\] .*$", content))
    entries: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        entry = content[match.start() : end].strip()
        if entry:
            entries.append(entry)
    return entries


def _entry_heading(entry: str) -> str:
    return entry.splitlines()[0].strip() if entry.splitlines() else ""


def _file_block(repo_root: Path, rel: str, *, missing_ok: bool = False) -> str:
    path = repo_root / rel
    if not path.exists():
        if missing_ok:
            return f"FILE: {rel}\n```text\n<missing>\n```"
        raise IngestFailure(FailureCode.INVALID_CHANGED_PATH, f"required context file is missing: {rel}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = "<binary or non-UTF-8 file omitted>"
    if len(text) > MAX_CONTEXT_FILE_CHARS:
        text = text[:MAX_CONTEXT_FILE_CHARS] + "\n\n<file truncated>"
    return f"FILE: {rel}\n```text\n{text.rstrip()}\n```"


def _write_report(repo_root: Path, report: IngestReport, report_path: Path) -> None:
    try:
        rel_report = report_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        rel_report = report_path.resolve().as_posix()
    report.report_path = rel_report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(as_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _extract_output_text(response_payload: dict[str, Any]) -> str:
    if isinstance(response_payload.get("output_text"), str):
        return response_payload["output_text"]
    texts: list[str] = []
    for item in response_payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content") or []:
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str):
                    texts.append(text)
    return "\n".join(texts)


def _response_schema() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "name": "team_llm_wiki_synthesis",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "summary",
                "integration_plan",
                "created_pages",
                "updated_pages",
                "claim_register",
                "open_questions",
                "superseded_or_conflicting_claims",
                "review_notes",
                "pages",
            ],
            "properties": {
                "summary": {"type": "string"},
                "integration_plan": {"type": "array", "items": {"type": "string"}},
                "created_pages": {"type": "array", "items": {"type": "string"}},
                "updated_pages": {"type": "array", "items": {"type": "string"}},
                "claim_register": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["status", "text"],
                        "properties": {
                            "status": {"type": "string"},
                            "text": {"type": "string"},
                        },
                    },
                },
                "open_questions": {"type": "array", "items": {"type": "string"}},
                "superseded_or_conflicting_claims": {"type": "array", "items": {"type": "string"}},
                "review_notes": {"type": "array", "items": {"type": "string"}},
                "pages": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["path", "content"],
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                    },
                },
            },
        },
    }
