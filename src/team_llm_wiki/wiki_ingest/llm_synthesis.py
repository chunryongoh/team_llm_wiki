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
from .render import INDEX_END, INDEX_START, LATEST_END, LATEST_START, render_target_path
from .route_contract import load_route_contract
from .wiki_plan import proposed_synthesis_paths

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_MAX_OUTPUT_TOKENS = 60000
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"
DEFAULT_GITHUB_MODELS_MODEL = "openai/gpt-4.1"
DEFAULT_GITHUB_MODELS_MAX_OUTPUT_TOKENS = 3000
DEFAULT_GITHUB_MODELS_MAX_PROMPT_CHARS = 12000
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
        self.provider_name = "openai-responses"
        self.last_model: str | None = None

    def synthesize(self, *, model: str, reasoning_effort: str, prompt: str) -> dict[str, Any]:
        if not self.api_key:
            raise IngestFailure(FailureCode.MISSING_API_KEY, "OPENAI_API_KEY is required for LLM synthesis")
        self.last_model = model
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


class GitHubModelsChatClient:
    def __init__(
        self,
        *,
        token: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
        max_prompt_chars: int | None = None,
    ):
        self.token = token or os.environ.get("GITHUB_MODELS_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.model = model or os.environ.get("GITHUB_MODELS_MODEL") or DEFAULT_GITHUB_MODELS_MODEL
        self.base_url = (base_url or os.environ.get("GITHUB_MODELS_BASE_URL") or DEFAULT_GITHUB_MODELS_BASE_URL).rstrip("/")
        env_budget = os.environ.get("GITHUB_MODELS_MAX_OUTPUT_TOKENS")
        self.max_output_tokens = int(env_budget) if env_budget else min(max_output_tokens, DEFAULT_GITHUB_MODELS_MAX_OUTPUT_TOKENS)
        env_prompt_budget = os.environ.get("GITHUB_MODELS_MAX_PROMPT_CHARS")
        self.max_prompt_chars = int(env_prompt_budget) if env_prompt_budget else (max_prompt_chars or DEFAULT_GITHUB_MODELS_MAX_PROMPT_CHARS)
        self.provider_name = "github-models"
        self.last_model: str | None = None

    def synthesize(self, *, model: str, reasoning_effort: str, prompt: str) -> dict[str, Any]:
        if not self.token:
            raise IngestFailure(FailureCode.MISSING_API_KEY, "GITHUB_TOKEN or GITHUB_MODELS_TOKEN is required for GitHub Models synthesis")
        self.last_model = self.model
        compact_prompt = _compact_prompt_for_github_models(prompt, max_chars=self.max_prompt_chars)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the Team LLM Wiki synthesis engine. Rewrite only the allowed wiki pages. "
                        "Follow AGENTS.md and CLAUDE.md exactly. Preserve claim statuses unless raw evidence "
                        "proves a change. Return only valid JSON matching the provided schema."
                    ),
                },
                {"role": "user", "content": compact_prompt},
            ],
            "max_tokens": self.max_output_tokens,
            "temperature": 0,
            "response_format": _chat_response_schema(),
        }
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2026-03-10",
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
                f"GitHub Models API failed with HTTP {exc.code}",
                {"body": body[:2000]},
            ) from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise IngestFailure(FailureCode.LLM_SYNTHESIS_FAILED, str(exc)) from exc
        output_text = _extract_chat_completion_text(response_payload)
        try:
            parsed = _loads_llm_json(output_text)
        except json.JSONDecodeError as exc:
            raise IngestFailure(
                FailureCode.INVALID_LLM_OUTPUT,
                "GitHub Models output was not valid JSON",
                {"output_text": output_text[:2000]},
            ) from exc
        return parsed if isinstance(parsed, dict) else {}


class SynthesisClientChain:
    def __init__(self, clients: list[Any]):
        self.clients = clients
        self.last_model: str | None = None
        self.last_provider: str | None = None
        self.review_notes: list[str] = []

    def synthesize(self, *, model: str, reasoning_effort: str, prompt: str) -> dict[str, Any]:
        failures: list[IngestFailure] = []
        for client in self.clients:
            try:
                payload = client.synthesize(model=model, reasoning_effort=reasoning_effort, prompt=prompt)
            except IngestFailure as exc:
                failures.append(exc)
                if _is_recoverable_synthesis_failure(exc):
                    continue
                raise
            self.last_model = getattr(client, "last_model", None) or getattr(client, "model", None) or model
            self.last_provider = getattr(client, "provider_name", client.__class__.__name__)
            if failures:
                failed = "; ".join(f"{failure.code.value}: {failure.message}" for failure in failures)
                self.review_notes.append(
                    f"Primary LLM provider failed recoverably ({failed}); synthesis completed with {self.last_provider} `{self.last_model}`."
                )
            return payload
        if failures:
            last = failures[-1]
            detail = {"provider_failures": [failure.to_dict() for failure in failures]}
            raise IngestFailure(last.code, last.message, detail) from last
        raise IngestFailure(FailureCode.MISSING_API_KEY, "No LLM synthesis provider is configured")


def default_synthesis_client(max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS) -> SynthesisClientChain:
    clients: list[Any] = []
    if os.environ.get("OPENAI_API_KEY"):
        clients.append(OpenAIResponsesClient(max_output_tokens=max_output_tokens))
    if os.environ.get("GITHUB_MODELS_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"):
        clients.append(GitHubModelsChatClient(max_output_tokens=max_output_tokens))
    if not clients:
        clients.append(OpenAIResponsesClient(max_output_tokens=max_output_tokens))
    return SynthesisClientChain(clients)


def run_llm_wiki_synthesis(
    repo_root: Path,
    changed_paths: list[str],
    *,
    report_path: Path | None = None,
    run_id: str = "llm-synthesis",
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
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
    target_paths = _target_paths(repo_root, manifests)
    evidence_by_target = _raw_evidence_by_target(repo_root, manifests, target_paths)
    prompt = build_llm_synthesis_prompt(repo_root, manifests, target_paths)
    synthesis_client = client or default_synthesis_client(max_output_tokens=max_output_tokens)
    llm_payload = synthesis_client.synthesize(model=model, reasoning_effort=reasoning_effort, prompt=prompt)
    actual_model = getattr(synthesis_client, "last_model", None) or model
    provider_name = _synthesis_provider_name(synthesis_client)
    provider_notes = list(getattr(synthesis_client, "review_notes", []) or [])
    llm_payload, metadata_notes = _normalize_github_models_payload_metadata(
        llm_payload,
        manifests=manifests,
        provider_name=provider_name,
    )
    provider_notes.extend(metadata_notes)
    pages = _coerce_page_outputs(llm_payload)
    pages, preserve_notes = _preserve_existing_pages_for_github_models(
        repo_root,
        pages,
        manifests=manifests,
        provider_name=provider_name,
    )
    provider_notes.extend(preserve_notes)
    pages, fallback_fill_notes = _fill_missing_required_pages_for_github_models(
        repo_root,
        pages,
        required_paths=target_paths,
        manifests=manifests,
        provider_name=provider_name,
    )
    provider_notes.extend(fallback_fill_notes)
    validation_failures = _page_validation_failures(
        repo_root,
        pages,
        allowed_paths=set(target_paths),
        required_paths=set(target_paths),
    )
    final_report_path = report_path or repo_root / "raw" / "results" / "llm-synthesis" / run_id / "report.json"
    if validation_failures:
        report = IngestReport(
            status="hard_fail",
            run_id=run_id,
            input_changed_paths=input_changed_paths,
            packet_roots=[_rel(repo_root, root) for root in packet_roots],
            packets=[
                {"id": manifest.id, "type": manifest.type.value, "packet_root": _rel(repo_root, root)}
                for manifest, root in manifests
            ],
            failures=validation_failures,
            risk_tier=RiskTierLabel.TIER4_GOVERNANCE.value,
            timing_ms=int((time.monotonic() - start) * 1000),
            llm_synthesis=True,
            model=actual_model,
            review_notes=[*provider_notes, *[str(note) for note in llm_payload.get("review_notes") or []]],
            synthesis_summary=str(llm_payload.get("summary", "")),
        )
        _write_report(repo_root, report, final_report_path)
        if report.report_path:
            report.generated_paths.append(report.report_path)
            report.changed_paths.append(report.report_path)
        return report
    changed: list[str] = []
    staging = _staged_wiki(repo_root)
    try:
        generated_page_paths = [page["path"] for page in pages]
        for page in pages:
            target = staging / page["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            content = _finalize_page_content(
                repo_root,
                page["path"],
                page["content"],
                evidence_by_target.get(page["path"], []),
                generated_page_paths,
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
        model=actual_model,
        review_notes=[*provider_notes, *[str(note) for note in llm_payload.get("review_notes") or []]],
        synthesis_summary=str(llm_payload.get("summary", "")),
        integration_plan=[str(item) for item in llm_payload.get("integration_plan") or []],
        created_pages=[str(item) for item in llm_payload.get("created_pages") or []],
        updated_pages=[str(item) for item in llm_payload.get("updated_pages") or []],
        claim_register=[item for item in llm_payload.get("claim_register") or [] if isinstance(item, dict)],
        open_questions=[item for item in llm_payload.get("open_questions") or [] if isinstance(item, dict)],
        superseded_or_conflicting_claims=[
            str(item) for item in llm_payload.get("superseded_or_conflicting_claims") or []
        ],
    )
    _write_report(repo_root, report, final_report_path)
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
    for rel in [
        "wiki/team/llm-synthesis-policy.md",
        "wiki/team/llm-wiki-operating-harness.md",
        "wiki/team/page-taxonomy.md",
        "wiki/team/wiki-ingest-policy.md",
        "wiki/team/packet-quality-standard.md",
    ]:
        files.append(_file_block(repo_root, rel, missing_ok=True))
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
        "- Use only canonical wiki namespaces for durable pages: preprocessing, features, models, performance, "
        "claims, targets, decisions, reports, team.\n"
        "- Do not create wiki/datasets, wiki/benchmarks, wiki/submissions, wiki/questions, wiki/experiments, "
        "or wiki/sources pages.\n"
        "- Put open questions into wiki/targets/* or wiki/reports/* with close conditions.\n"
        "- Put leaderboard and metric history into wiki/performance/*.\n"
        "- Put dataset, split, leakage, and fit-scope policy into wiki/preprocessing/*.\n"
        "- Follow the operating harness: session context is ephemeral, durable insight must be crystallized into "
        "wiki pages, `index.md` is the content catalog, and `log.md` is the chronological audit trail.\n"
        "- Respect page roles. Entrypoints route, hubs/registries summarize and link, leaf pages own reusable "
        "entity memory, packet review pages preserve source-specific context, and reports archive time-bounded waves.\n"
        "- If `wiki_plan.yaml` proposes justified leaf pages, update those leaf pages instead of absorbing all detail "
        "into a hub. If a proposed leaf is unjustified, explain why in review_notes.\n"
        "- Update the claim registry, DACON leaderboard history, metric history, and preprocessing/split policy pages when relevant; "
        "even when no claim changes, explicitly preserve that boundary.\n"
        "- Write every allowed output page exactly once; missing pages are invalid output.\n"
        "- Cross-link related preprocessing, performance, feature, decision, target, and report pages.\n"
        "- Capture contradictions, supersession notes, and unresolved questions as first-class wiki content.\n"
        "- `wiki/latest-context.md` latest-context must expose Current Best, Active Risks, and Next Actions.\n"
        "- Never merge local OOF, notebook-output, user-reported public score, DACON public leaderboard, "
        "DACON private leaderboard, or organizer-official validation into one evidence surface.\n"
        "- Preserve raw provenance, packet ids, claim boundaries, and claim statuses.\n"
        "- Do not write raw/, automation/, or policy files.\n"
        "- Do not promote tentative claims to supported without explicit raw metric/split evidence.\n"
        "- Write narrative prose and all metadata summaries in Korean so every teammate can review the PR; "
        "keep file paths, ids, field names, metrics, and model names verbatim.\n"
        "- Concise page budgets: write compact wiki pages, not exhaustive reports. Keep packet review pages around "
        "900-1400 Korean characters and integration pages around 1200-2200 Korean characters unless a page already "
        "requires longer append-only history.\n"
        "- Do not copy raw packet text into wiki pages. Synthesize stable facts, claim boundaries, evidence gaps, "
        "decisions, and next actions with links to raw evidence.\n"
        "- Return JSON with keys: summary, integration_plan, created_pages, updated_pages, claim_register, "
        "open_questions, superseded_or_conflicting_claims, review_notes, pages.\n"
        "- Each open_questions item must be an actionable backlog object with id, question, priority, "
        "owner_role, merge_blocker, needed_evidence, and close_condition.\n\n"
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


def _target_paths(repo_root: Path, manifests: list[tuple[PacketManifest, Path]]) -> list[str]:
    entity_paths = [render_target_path(manifest, packet_root, repo_root=repo_root) for manifest, packet_root in manifests]
    proposed_paths = [
        path
        for path in proposed_synthesis_paths([packet_root for _manifest, packet_root in manifests], repo_root=repo_root)
        if not path.startswith("wiki/team/")
    ]
    return list(dict.fromkeys([*entity_paths, *_integration_paths(manifests), *proposed_paths]))


def _coerce_page_outputs(payload: dict[str, Any]) -> list[dict[str, str]]:
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
        clean.append({"path": rel, "content": content})
    return clean


def _validated_pages(
    payload: dict[str, Any],
    *,
    allowed_paths: set[str],
    required_paths: set[str] | None = None,
) -> list[dict[str, str]]:
    clean = _coerce_page_outputs(payload)
    failures = _page_validation_failures(
        Path("."),
        clean,
        allowed_paths=allowed_paths,
        required_paths=required_paths,
        skip_contract=True,
    )
    if failures:
        first = failures[0]
        raise IngestFailure(FailureCode.INVALID_LLM_OUTPUT, str(first.get("message", "invalid LLM page output")), first)
    return clean


def _page_validation_failures(
    repo_root: Path,
    pages: list[dict[str, object]],
    *,
    allowed_paths: set[str],
    required_paths: set[str] | None = None,
    skip_contract: bool = False,
) -> list[dict[str, object]]:
    failures: list[dict[str, object]] = []
    if not skip_contract:
        failures.extend(_validate_generated_pages_against_contract(repo_root, pages))
    seen: set[str] = set()
    duplicates: list[str] = []
    for page in pages:
        rel = str(page.get("path", ""))
        if rel in seen and rel not in duplicates:
            duplicates.append(rel)
        seen.add(rel)
        if rel not in allowed_paths and not any(error.get("path") == rel for error in failures):
            failures.append(
                {
                    "code": "unapproved_synthesis_path",
                    "path": rel,
                    "message": "LLM wrote a wiki path outside the allowed synthesis plan",
                }
            )
    if duplicates:
        failures.append(
            {
                "code": FailureCode.INVALID_LLM_OUTPUT.value,
                "message": "LLM output wrote the same wiki page more than once",
                "duplicate_paths": sorted(duplicates),
            }
        )
    required_paths = required_paths or set()
    present = {str(page["path"]) for page in pages}
    missing = sorted(required_paths - present)
    if missing:
        failures.append(
            {
                "code": FailureCode.INVALID_LLM_OUTPUT.value,
                "message": "LLM output omitted required wiki integration pages",
                "missing_paths": missing,
            }
        )
    return failures


def _synthesis_provider_name(client: Any) -> str:
    return str(
        getattr(client, "last_provider", None)
        or getattr(client, "provider_name", None)
        or client.__class__.__name__
    ).lower()


def _normalize_github_models_payload_metadata(
    payload: dict[str, Any],
    *,
    manifests: list[tuple[PacketManifest, Path]],
    provider_name: str,
) -> tuple[dict[str, Any], list[str]]:
    if provider_name != "github-models":
        return payload, []

    original_claim_register = payload.get("claim_register")
    attempted_supported = False
    if isinstance(original_claim_register, list):
        attempted_supported = any(
            isinstance(item, dict) and str(item.get("status", "")).lower() == "supported"
            for item in original_claim_register
        )
    normalized = dict(payload)
    normalized["summary"] = _github_models_manifest_summary(manifests)
    normalized["integration_plan"] = [
        "GitHub Models fallback used compact model output only for route discovery.",
        "Non-entrypoint wiki page bodies were generated from raw packet manifests and metrics_to_verify.",
        "Claim boundaries, metric values, and validation gaps must be reviewed against raw evidence before promotion.",
    ]
    normalized["claim_register"] = _github_models_manifest_claim_register(manifests)
    normalized["open_questions"] = _github_models_manifest_open_questions(manifests)
    normalized["superseded_or_conflicting_claims"] = []
    notes = [
        "GitHub Models fallback metadata was normalized from raw PacketManifest fields instead of compact model prose."
    ]
    if attempted_supported:
        notes.append(
            "GitHub Models fallback cannot promote supported claims; compact claim_register items were replaced with manifest-backed claim records."
        )
    return normalized, notes


def _github_models_manifest_summary(manifests: list[tuple[PacketManifest, Path]]) -> str:
    summaries = [manifest.summary for manifest, _root in manifests if manifest.summary.strip()]
    return " | ".join(summaries) or "GitHub Models fallback manifest-backed synthesis."


def _github_models_manifest_claim_register(manifests: list[tuple[PacketManifest, Path]]) -> list[dict[str, str]]:
    claims: list[dict[str, str]] = []
    for manifest, _root in manifests:
        if manifest.claims:
            for claim in manifest.claims:
                claims.append(
                    {
                        "status": str(claim.status),
                        "text": _fallback_inline_text(claim.text or manifest.summary, max_chars=520),
                    }
                )
            continue
        claims.append(
            {
                "status": str(manifest.claim_status),
                "text": _fallback_inline_text(manifest.summary, max_chars=520),
            }
        )
    return claims


def _github_models_manifest_open_questions(manifests: list[tuple[PacketManifest, Path]]) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for manifest, _root in manifests:
        questions.append(
            {
                "id": f"fallback-review-{_slugify(manifest.id)}",
                "question": f"Review `{manifest.id}` fallback scaffold against raw evidence and decide whether primary LLM or human synthesis should refine it.",
                "priority": "medium",
                "owner_role": "wiki-reviewer",
                "merge_blocker": False,
                "needed_evidence": "Raw packet manifest, metrics_to_verify, and referenced raw paths.",
                "close_condition": "Reviewer confirms scaffold is sufficient or replaces it with primary LLM/human synthesis.",
            }
        )
    return questions


def _preserve_existing_pages_for_github_models(
    repo_root: Path,
    pages: list[dict[str, str]],
    *,
    manifests: list[tuple[PacketManifest, Path]],
    provider_name: str,
) -> tuple[list[dict[str, str]], list[str]]:
    if provider_name != "github-models":
        return pages, []

    entrypoints = {"wiki/index.md", "wiki/log.md", "wiki/latest-context.md", "wiki/overview.md"}
    preserved: list[dict[str, str]] = []
    preserved_paths: list[str] = []
    scaffolded_paths: list[str] = []
    for page in pages:
        path = page["path"]
        existing_path = repo_root / path
        if path in entrypoints:
            preserved.append(page)
            continue
        if existing_path.exists():
            preserved.append(
                {
                    "path": path,
                    "content": _github_models_existing_page_addendum(
                        repo_root,
                        path,
                        page["content"],
                        manifests=manifests,
                    ),
                }
            )
            preserved_paths.append(path)
            continue
        preserved.append(
            {
                "path": path,
                "content": _github_models_new_page_scaffold(path, manifests=manifests),
            }
        )
        scaffolded_paths.append(path)

    notes: list[str] = []
    if preserved_paths:
        notes.append(
            "GitHub Models fallback preserved existing wiki pages with non-destructive addenda: "
            + _preview_paths(preserved_paths)
            + "."
        )
    if scaffolded_paths:
        notes.append(
            "GitHub Models fallback replaced compact new-page bodies with deterministic scaffolds: "
            + _preview_paths(scaffolded_paths)
            + "."
        )
    return preserved, notes


def _preview_paths(paths: list[str], *, limit: int = 8) -> str:
    preview = ", ".join(paths[:limit])
    if len(paths) > limit:
        preview += f", and {len(paths) - limit} more"
    return preview


def _github_models_existing_page_addendum(
    repo_root: Path,
    rel_path: str,
    _generated_content: str,
    *,
    manifests: list[tuple[PacketManifest, Path]],
) -> str:
    existing = (repo_root / rel_path).read_text(encoding="utf-8").rstrip()
    date_slug = _source_date_slug(manifests)
    packet_ids = ", ".join(manifest.id for manifest, _root in manifests) or "unknown"
    marker = f"<!-- llm-synthesis:github-models-nondestructive-addendum:{date_slug}:{_slugify(rel_path)} -->"
    if marker in existing:
        return existing + "\n"
    return (
        existing
        + "\n\n"
        + marker
        + "\n"
        + f"## GitHub Models Synthesis Addendum | {date_slug}\n\n"
        + "- fallback_merge_policy: preserved_existing_page\n"
        + "- fallback_compact_body_applied: false\n"
        + f"- packet_ids: `{packet_ids}`\n"
        + "- note: GitHub Models fallback returned compact content for this existing page, but the body was not applied because compact fallback output can omit or distort metric provenance.\n"
        + "- action: Review the existing page body, raw evidence, and synthesis report instead of treating this addendum as a metric update.\n"
    )


def _github_models_new_page_scaffold(
    rel_path: str,
    *,
    manifests: list[tuple[PacketManifest, Path]],
) -> str:
    title = _fallback_title_from_path(rel_path)
    lines = [
        f"# {title}",
        "",
        "## GitHub Models Deterministic Page Scaffold",
        "",
        "- fallback_merge_policy: deterministic_new_page_scaffold",
        "- fallback_compact_body_applied: false",
        "- note: GitHub Models fallback identified this page as required, but compact model prose was not applied because metric provenance must come from raw packet evidence.",
        "",
        "## Source Packets",
        "",
    ]
    for manifest, _root in manifests:
        lines.extend(
            [
                f"### {manifest.id}",
                "",
                f"- packet_type: `{manifest.type.value}`",
                f"- title: {manifest.title}",
                f"- date: `{manifest.date}`",
                f"- owner: `{manifest.owner}`",
                f"- dataset: `{manifest.dataset.name}` (`{manifest.dataset.version}`)",
                f"- split: `{manifest.split.name}`",
                f"- model: `{manifest.model.family}`",
                f"- claim_boundary: `{manifest.claim_boundary}`",
                f"- claim_status: `{manifest.claim_status}`",
                f"- summary: {_fallback_inline_text(manifest.summary, max_chars=420)}",
                "",
            ]
        )
        metric_lines = _manifest_metric_lines(manifest)
        if metric_lines:
            lines.extend(["#### Raw-backed Metrics", "", *metric_lines, ""])
        claim_lines = _manifest_claim_lines(manifest)
        if claim_lines:
            lines.extend(["#### Manifest Claims", "", *claim_lines, ""])
    lines.extend(
        [
            "## Review Boundary",
            "",
            "- Local OOF, notebook output, DACON public/private leaderboard, and organizer-official validation remain separate evidence surfaces.",
            "- Do not treat this scaffold as a claim promotion; update it with primary LLM synthesis or human review when stronger evidence is available.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _manifest_metric_lines(manifest: PacketManifest) -> list[str]:
    lines: list[str] = []
    for metric in manifest.metrics_to_verify:
        if not hasattr(metric, "metric_key") or not hasattr(metric, "reported_value"):
            continue
        raw_path = getattr(metric, "raw_path", None)
        key = getattr(metric, "metric_key", None)
        value = getattr(metric, "reported_value", None)
        if key is None or value is None:
            continue
        lines.append(f"- `{key}`: `{value}` (raw_path: `{raw_path}`)")
    return lines


def _manifest_claim_lines(manifest: PacketManifest) -> list[str]:
    lines: list[str] = []
    for claim in manifest.claims:
        status = getattr(claim, "status", None)
        text = getattr(claim, "text", None)
        if not status:
            continue
        lines.append(f"- {status}: {_fallback_inline_text(text or '', max_chars=360)}")
    return lines


def _fill_missing_required_pages_for_github_models(
    repo_root: Path,
    pages: list[dict[str, str]],
    *,
    required_paths: list[str],
    manifests: list[tuple[PacketManifest, Path]],
    provider_name: str,
) -> tuple[list[dict[str, str]], list[str]]:
    if provider_name != "github-models":
        return pages, []
    present = {page["path"] for page in pages}
    missing_paths = [path for path in required_paths if path not in present]
    if not missing_paths:
        return pages, []

    filled_pages = [*pages]
    required_set = set(required_paths)
    for path in missing_paths:
        filled_pages.append(
            {
                "path": path,
                "content": _github_models_required_page_fallback_content(
                    repo_root,
                    path,
                    required_paths=required_set,
                    manifests=manifests,
                ),
            }
        )
    preview = ", ".join(missing_paths[:8])
    if len(missing_paths) > 8:
        preview += f", and {len(missing_paths) - 8} more"
    return filled_pages, [f"GitHub Models fallback filled missing required wiki pages: {preview}."]


def _github_models_required_page_fallback_content(
    repo_root: Path,
    rel_path: str,
    *,
    required_paths: set[str],
    manifests: list[tuple[PacketManifest, Path]],
) -> str:
    topic = _topic_slug(manifests)
    date_slug = _source_date_slug(manifests)
    packet_ids = ", ".join(manifest.id for manifest, _root in manifests) or "unknown"
    report_path = next((path for path in required_paths if path.startswith("wiki/reports/")), "wiki/index.md")
    report_link = report_path.removeprefix("wiki/").removesuffix(".md")

    if rel_path == "wiki/index.md":
        entries = [
            _default_index_entry(path)
            for path in sorted(required_paths)
            if _index_target_from_wiki_path(path)
        ]
        return "# Team LLM Wiki Index\n\n" + INDEX_START + "\n" + "\n".join(entries) + "\n" + INDEX_END + "\n"
    if rel_path == "wiki/latest-context.md":
        return (
            "# Latest Context\n\n"
            "[[index]] [[overview]] [[log]]\n\n"
            "## Current Best\n\n"
            f"- Latest synthesized packet topic: `{topic}`.\n"
            "- Claim boundaries are preserved; local OOF, leaderboard, notebook, and official validation evidence remain separate.\n\n"
            "## Active Risks\n\n"
            "- GitHub Models fallback filled some required pages conservatively because the primary LLM provider was unavailable.\n"
            "- Do not promote tentative metric or feature claims without raw evidence and validation lineage.\n\n"
            "## Next Actions\n\n"
            f"- Use `{report_path}` as the entrypoint for this synthesis wave and close any validation evidence gaps.\n\n"
            f"{LATEST_START}\n"
            f"### {date_slug} | {topic} fallback synthesis\n\n"
            f"- link: [[{report_link}]]\n"
            f"- packets: `{packet_ids}`\n"
            f"{LATEST_END}\n"
        )
    if rel_path == "wiki/log.md":
        return (
            "# Log\n\n"
            f"## [{date_slug}] llm-synthesis | {topic}\n\n"
            "- GitHub Models fallback produced a partial synthesis; required wiki pages were conservatively filled in GitHub Actions.\n"
            f"- packets: `{packet_ids}`\n"
            f"- report: `{report_path}`\n"
        )
    if rel_path == "wiki/overview.md":
        return (
            "# Team LLM Wiki Overview\n\n"
            "## Current Focus\n\n"
            f"- Latest packet synthesis topic: `{topic}`.\n"
            f"- Source packets: `{packet_ids}`.\n\n"
            "## Evidence Boundary\n\n"
            "- Local OOF, notebook output, DACON public score, DACON private score, and organizer-official validation remain separate evidence surfaces.\n"
            "- GitHub Models fallback does not promote tentative claims; it preserves review-required integration context.\n\n"
            "## Review Queue\n\n"
            f"- Review `{report_path}` and raw evidence before treating new claims as supported.\n"
        )

    existing_path = repo_root / rel_path
    if not existing_path.exists():
        return _github_models_new_page_scaffold(rel_path, manifests=manifests)
    existing = existing_path.read_text(encoding="utf-8").rstrip()
    marker = f"<!-- llm-synthesis:github-models-required-page-fill:{date_slug}:{_slugify(rel_path)} -->"
    section = (
        f"{marker}\n"
        f"## GitHub Models Fallback Synthesis | {date_slug}\n\n"
        f"- packet_ids: `{packet_ids}`\n"
        f"- packet_summary: {_manifest_summary_for_fallback(manifests)}\n"
        "- claim_status: preserved_from_raw_packet\n"
        "- evidence_boundary: local_oof, notebook_output, DACON_public, DACON_private, and organizer_official evidence must stay separate.\n"
        "- review_note: This page was conservatively filled in GitHub Actions because the compact fallback model omitted a required wiki page.\n"
        f"- synthesis_report: `{report_path}`\n"
    )
    if marker in existing:
        return existing + "\n"
    return existing + "\n\n" + section


def _fallback_title_from_path(rel_path: str) -> str:
    return Path(rel_path).stem.replace("-", " ").title()


def _manifest_summary_for_fallback(manifests: list[tuple[PacketManifest, Path]]) -> str:
    summaries = [f"{manifest.id}: {manifest.summary}" for manifest, _root in manifests]
    return _fallback_inline_text(" | ".join(summaries) or "No packet summary.", max_chars=420)


def _fallback_inline_text(value: Any, *, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", str(value)).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _validate_generated_pages_against_contract(repo_root: Path, pages: list[dict[str, object]]) -> list[dict[str, object]]:
    contract = load_route_contract(repo_root)
    errors: list[dict[str, object]] = []
    entrypoints = {"wiki/index.md", "wiki/log.md", "wiki/latest-context.md", "wiki/overview.md"}
    for page in pages:
        path = str(page.get("path", ""))
        if path in entrypoints:
            continue
        if path.startswith("wiki/team/"):
            errors.append({"code": "policy_synthesis_path", "path": path, "message": "LLM synthesis may not write team policy pages"})
            continue
        if not contract.is_allowed_synthesis_path(path):
            code = "deprecated_synthesis_path" if contract.deprecated_namespace_for_path(path) else "invalid_synthesis_path"
            errors.append({"code": code, "path": path, "message": "LLM synthesis output path is not canonical"})
    return errors


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
        evidence[render_target_path(manifest, packet_root, repo_root=repo_root)] = seen
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
        f"wiki/targets/{topic}-open-issues.md",
        "wiki/claims/current-supported-claims.md",
        "wiki/performance/dacon-leaderboard-history.md",
        "wiki/preprocessing/canonical-split-and-leakage-policy.md",
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
    prefixes = ("wiki/decisions/", "wiki/targets/", "wiki/reports/", "wiki/index.md", "wiki/log.md", "wiki/overview.md")
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


def _finalize_page_content(
    repo_root: Path,
    rel_path: str,
    content: str,
    evidence_paths: list[str],
    generated_page_paths: list[str] | None = None,
) -> str:
    if rel_path == "wiki/log.md":
        return _merge_append_only_log(repo_root, content)
    if rel_path == "wiki/index.md":
        return _merge_index_content(repo_root, content, generated_page_paths or [])
    if rel_path == "wiki/latest-context.md":
        return _merge_latest_context_content(repo_root, content)
    return _ensure_raw_evidence(content, evidence_paths)


def _merge_index_content(repo_root: Path, content: str, generated_page_paths: list[str]) -> str:
    existing_path = repo_root / "wiki" / "index.md"
    existing = existing_path.read_text(encoding="utf-8") if existing_path.exists() else ""
    scaffold = existing if _has_balanced_index_block(existing) else content
    if not _has_balanced_index_block(scaffold):
        scaffold = "# Team LLM Wiki Index\n\n" + INDEX_START + "\n" + INDEX_END + "\n"

    entries: dict[str, str] = {}
    for line in _extract_index_entries(scaffold):
        target = _index_entry_target(line)
        if target:
            entries.setdefault(target, line)
    for line in _extract_index_entries(content):
        target = _index_entry_target(line)
        if target:
            entries[target] = line
    for rel_path in generated_page_paths:
        target = _index_target_from_wiki_path(rel_path)
        if target:
            entries.setdefault(target, _default_index_entry(rel_path))

    merged_lines = sorted(entries.values(), key=lambda line: (_index_entry_target(line) or line).lower())
    return _replace_index_block(scaffold, merged_lines)


def _has_balanced_index_block(text: str) -> bool:
    return text.count(INDEX_START) == 1 and text.count(INDEX_END) == 1 and text.index(INDEX_START) < text.index(INDEX_END)


def _extract_index_entries(text: str) -> list[str]:
    entries: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and _index_entry_target(stripped):
            entries.append(stripped)
    return entries


def _index_entry_target(line: str) -> str | None:
    match = re.search(r"\(([^)]+\.md)\)", line)
    if not match:
        return None
    target = match.group(1).strip()
    if not target or target.startswith(("http://", "https://", "../")):
        return None
    return target.removeprefix("wiki/")


def _index_target_from_wiki_path(rel_path: str) -> str | None:
    if not rel_path.startswith("wiki/") or not rel_path.endswith(".md"):
        return None
    if rel_path in {"wiki/index.md", "wiki/log.md", "wiki/latest-context.md", "wiki/overview.md"}:
        return None
    if rel_path.startswith("wiki/team/") or rel_path.endswith("/README.md"):
        return None
    return rel_path.removeprefix("wiki/")


def _default_index_entry(rel_path: str) -> str:
    target = _index_target_from_wiki_path(rel_path) or rel_path.removeprefix("wiki/")
    title = Path(target).stem.replace("-", " ").title()
    page_type = Path(target).parent.name.rstrip("s") or "page"
    return f"- [{title}]({target}) - `{page_type}`"


def _replace_index_block(scaffold: str, entries: list[str]) -> str:
    start_index = scaffold.index(INDEX_START)
    end_index = scaffold.index(INDEX_END) + len(INDEX_END)
    block = "\n".join([INDEX_START, *entries, INDEX_END])
    return scaffold[:start_index].rstrip() + "\n\n" + block + scaffold[end_index:].rstrip() + "\n"


def _merge_latest_context_content(repo_root: Path, content: str) -> str:
    existing_path = repo_root / "wiki" / "latest-context.md"
    existing = existing_path.read_text(encoding="utf-8") if existing_path.exists() else ""
    scaffold = content if _has_latest_operating_sections(content) else existing
    if not scaffold.strip():
        scaffold = "# Latest Context\n\n[[index]] [[overview]] [[log]]\n\n## Current Best\n\n- Unknown.\n\n## Active Risks\n\n- Unknown.\n\n## Next Actions\n\n- Review latest packet.\n"

    entries = _extract_latest_entries(content)
    if not entries:
        entries = _extract_latest_entries(existing)
    if not entries:
        entries = ["### llm synthesis | latest update", "", "- link: [[index]]"]
    return _replace_latest_block(scaffold, entries)


def _has_latest_operating_sections(text: str) -> bool:
    return all(marker in text for marker in ("[[index]]", "[[overview]]", "[[log]]", "## Current Best", "## Active Risks", "## Next Actions"))


def _extract_latest_entries(text: str) -> list[str]:
    if text.count(LATEST_START) != 1 or text.count(LATEST_END) != 1 or text.index(LATEST_START) > text.index(LATEST_END):
        return []
    start_index = text.index(LATEST_START) + len(LATEST_START)
    end_index = text.index(LATEST_END)
    block = text[start_index:end_index].strip()
    return block.splitlines() if block else []


def _replace_latest_block(scaffold: str, entries: list[str]) -> str:
    clean_entries = "\n".join(line.rstrip() for line in entries).strip()
    block = "\n".join([LATEST_START, clean_entries, LATEST_END]) if clean_entries else "\n".join([LATEST_START, LATEST_END])
    if scaffold.count(LATEST_START) == 1 and scaffold.count(LATEST_END) == 1 and scaffold.index(LATEST_START) < scaffold.index(LATEST_END):
        start_index = scaffold.index(LATEST_START)
        end_index = scaffold.index(LATEST_END) + len(LATEST_END)
        return scaffold[:start_index].rstrip() + "\n\n" + block + scaffold[end_index:].rstrip() + "\n"
    if LATEST_START in scaffold:
        return scaffold[: scaffold.index(LATEST_START)].rstrip() + "\n\n" + block + "\n"
    return scaffold.rstrip() + "\n\n" + block + "\n"


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


def _extract_chat_completion_text(response_payload: dict[str, Any]) -> str:
    choices = response_payload.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                texts = [
                    item.get("text")
                    for item in content
                    if isinstance(item, dict) and isinstance(item.get("text"), str)
                ]
                if texts:
                    return "\n".join(texts)
    if isinstance(response_payload.get("output_text"), str):
        return response_payload["output_text"]
    return ""


def _loads_llm_json(text: str) -> Any:
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean).strip()
    return json.loads(clean)


def _compact_prompt_for_github_models(prompt: str, *, max_chars: int = DEFAULT_GITHUB_MODELS_MAX_PROMPT_CHARS) -> str:
    if len(prompt) <= max_chars:
        return prompt
    matches = list(re.finditer(r"FILE: ([^\n]+)\n```text\n(.*?)\n```", prompt, flags=re.DOTALL))
    if not matches:
        return _truncate_text(prompt, max_chars)

    head = prompt[: matches[0].start()].strip()
    head = _truncate_text(head, min(6500, max_chars // 2))
    intro = (
        head.rstrip()
        + "\n\nGitHub Models fallback compact context: some large raw artifacts are truncated. "
        "Use preserved filenames, metrics, claim boundaries, wiki_plan targets, and existing wiki entrypoints to synthesize concise pages."
    )
    blocks = [
        (
            _github_prompt_file_priority(match.group(1)),
            match.start(),
            _compact_file_block_for_github(match.group(1), match.group(2)),
        )
        for match in matches
    ]
    blocks.sort(key=lambda item: (item[0], item[1]))
    selected: list[str] = []
    omitted: list[str] = []
    current_len = len(intro) + 2
    for _priority, _index, block in blocks:
        needed = len(block) + 2
        if current_len + needed <= max_chars:
            selected.append(block)
            current_len += needed
        else:
            omitted.append(_file_path_from_block(block))
    suffix = ""
    if omitted:
        suffix = "\n\nOmitted compact context files due GitHub Models request limit:\n" + "\n".join(
            f"- {path}" for path in omitted[:80]
        )
    compact = intro + "\n\n" + "\n\n".join(selected) + suffix
    if len(compact) > max_chars:
        compact = _truncate_text(compact, max_chars)
    return compact


def _compact_file_block_for_github(path: str, content: str) -> str:
    budget = _github_prompt_file_budget(path)
    return f"FILE: {path}\n```text\n{_truncate_text(content.strip(), budget)}\n```"


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    marker = "\n<truncated for GitHub Models fallback>\n"
    if max_chars <= len(marker) + 20:
        return text[:max(0, max_chars - len(marker))] + marker.strip()
    head = max_chars - len(marker)
    return text[:head].rstrip() + marker


def _github_prompt_file_priority(path: str) -> int:
    if path in {"AGENTS.md", "CLAUDE.md", "wiki/latest-context.md", "wiki/index.md", "wiki/overview.md"}:
        return 0
    if path.endswith(("/manifest.yaml", "/packet.md", "/metrics.json", "/performance.yaml", "/wiki_plan.yaml")):
        return 0
    if path.endswith(("/semantic_lint.json", "/question_queue.yaml", "/artifact_summary.json", "/source_note.md")):
        return 1
    if path.startswith("wiki/team/") or path.startswith("wiki/claims/") or path.startswith("wiki/preprocessing/"):
        return 1
    if path.startswith("wiki/") or "/source_artifacts/" not in path:
        return 2
    return 3


def _github_prompt_file_budget(path: str) -> int:
    if path in {"AGENTS.md", "CLAUDE.md"}:
        return 2200
    if path in {"wiki/latest-context.md", "wiki/index.md", "wiki/overview.md"}:
        return 1600
    if path.endswith("/packet.md"):
        return 1800
    if path.endswith(("/manifest.yaml", "/metrics.json", "/performance.yaml", "/wiki_plan.yaml")):
        return 1600
    if path.endswith(("/semantic_lint.json", "/question_queue.yaml", "/artifact_summary.json", "/source_note.md")):
        return 900
    if path.startswith("wiki/team/"):
        return 900
    if "/source_artifacts/" in path:
        return 450
    return 900


def _file_path_from_block(block: str) -> str:
    first = block.splitlines()[0] if block.splitlines() else ""
    return first.removeprefix("FILE: ").strip() or "<unknown>"


def _is_recoverable_synthesis_failure(exc: IngestFailure) -> bool:
    if exc.code is FailureCode.MISSING_API_KEY:
        return True
    if exc.code is not FailureCode.LLM_SYNTHESIS_FAILED:
        return False
    details = json.dumps(exc.details, ensure_ascii=False, sort_keys=True) if exc.details else ""
    text = f"{exc.message}\n{details}".lower()
    recoverable_markers = (
        "http 429",
        "insufficient_quota",
        "rate_limit",
        "temporarily",
        "timeout",
        "timed out",
        "http 500",
        "http 502",
        "http 503",
        "http 504",
    )
    return any(marker in text for marker in recoverable_markers)


def _chat_response_schema() -> dict[str, Any]:
    schema = _response_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema["name"],
            "strict": schema["strict"],
            "schema": schema["schema"],
        },
    }


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
                "open_questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "id",
                            "question",
                            "priority",
                            "owner_role",
                            "merge_blocker",
                            "needed_evidence",
                            "close_condition",
                        ],
                        "properties": {
                            "id": {"type": "string"},
                            "question": {"type": "string"},
                            "priority": {"type": "string"},
                            "owner_role": {"type": "string"},
                            "merge_blocker": {"type": "boolean"},
                            "needed_evidence": {"type": "string"},
                            "close_condition": {"type": "string"},
                        },
                    },
                },
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
