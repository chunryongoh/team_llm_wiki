from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any
from urllib import error, request

from .health import check_wiki_health
from .links import lint_wiki_links
from .manifest import discover_packet_roots, load_packet_manifest, validate_changed_paths
from .models import FailureCode, IngestFailure, IngestReport, PacketManifest, RiskTierLabel, as_jsonable
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
    evidence_by_target = _raw_evidence_by_target(repo_root, manifests)
    prompt = build_llm_synthesis_prompt(repo_root, manifests, target_paths)
    synthesis_client = client or OpenAIResponsesClient()
    llm_payload = synthesis_client.synthesize(model=model, reasoning_effort=reasoning_effort, prompt=prompt)
    pages = _validated_pages(llm_payload, allowed_paths=set(target_paths))
    changed: list[str] = []
    staging = _staged_wiki(repo_root)
    try:
        for page in pages:
            target = staging / page["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            content = _ensure_raw_evidence(page["content"], evidence_by_target.get(page["path"], []))
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
        risk_tier=RiskTierLabel.TIER2_INTERPRETATION.value if not failures else RiskTierLabel.TIER4_GOVERNANCE.value,
        timing_ms=int((time.monotonic() - start) * 1000),
        llm_synthesis=True,
        model=model,
        review_notes=[str(note) for note in llm_payload.get("review_notes") or []],
        synthesis_summary=str(llm_payload.get("summary", "")),
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
    for rel in ["CLAUDE.md", "wiki/latest-context.md"]:
        files.append(_file_block(repo_root, rel, missing_ok=True))
    files.append(_file_block(repo_root, "wiki/team/llm-synthesis-policy.md", missing_ok=True))
    for manifest, packet_root in manifests:
        files.extend(_packet_file_blocks(repo_root, packet_root))
    for rel in target_paths:
        files.append(_file_block(repo_root, rel, missing_ok=True))
    allowed = "\n".join(f"- {path}" for path in target_paths)
    return (
        "Rewrite the allowed wiki pages as high-quality team memory.\n\n"
        "Requirements:\n"
        "- Read and obey AGENTS.md and CLAUDE.md.\n"
        "- Use stable entity pages, not dated packet mirrors.\n"
        "- Preserve raw provenance, packet ids, claim boundaries, and claim statuses.\n"
        "- Do not write raw/, automation/, or policy files.\n"
        "- Do not promote tentative claims to supported without explicit raw metric/split evidence.\n"
        "- Return JSON with keys: summary, review_notes, pages.\n\n"
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
    return list(dict.fromkeys(render_target_path(manifest, packet_root) for manifest, packet_root in manifests))


def _validated_pages(payload: dict[str, Any], *, allowed_paths: set[str]) -> list[dict[str, str]]:
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


def _raw_evidence_by_target(repo_root: Path, manifests: list[tuple[PacketManifest, Path]]) -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {}
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
        evidence[render_target_path(manifest, packet_root)] = seen
    return evidence


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
            "required": ["summary", "review_notes", "pages"],
            "properties": {
                "summary": {"type": "string"},
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
