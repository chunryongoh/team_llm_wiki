from __future__ import annotations

import html
from pathlib import Path
import re
from typing import Any

import yaml

from .models import PacketManifest, PacketType, RenderResult, RiskTier, RiskTierLabel, _validate_kebab_id, as_jsonable
from .policy import IngestPolicy
from .routes import packet_target_path

INDEX_START = "<!-- wiki-ingest:index:start -->"
INDEX_END = "<!-- wiki-ingest:index:end -->"
LATEST_START = "<!-- wiki-ingest:latest:start -->"
LATEST_END = "<!-- wiki-ingest:latest:end -->"
REVIEW_TYPES = {
    PacketType.PERFORMANCE,
    PacketType.MODEL,
    PacketType.FEATURE,
    PacketType.EXPERIMENT,
    PacketType.DATASET,
    PacketType.BENCHMARK,
}


def _replace_block(text: str, start: str, end: str, body: str) -> str:
    block = f"{start}\n{body.rstrip()}\n{end}"
    if start in text and end in text and text.index(start) < text.index(end):
        before = text[: text.index(start)].rstrip()
        after = text[text.index(end) + len(end) :].lstrip()
        return "\n\n".join(part for part in [before, block, after] if part) + "\n"
    return text.rstrip() + "\n\n" + block + "\n"


def _existing_block_lines(text: str, start: str, end: str) -> list[str]:
    if start not in text or end not in text or text.index(start) > text.index(end):
        return []
    body = text[text.index(start) + len(start) : text.index(end)]
    return [line for line in body.splitlines() if line.strip()]


def _split_latest_entries(body: str) -> list[str]:
    entries: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        if line.startswith("### ") and current:
            entries.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current and "\n".join(current).strip():
        entries.append("\n".join(current).strip())
    return entries


def _append_once(path: Path, entry: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else "# Log\n"
    if entry.splitlines()[0] not in text:
        path.write_text(text.rstrip() + "\n\n" + entry.rstrip() + "\n", encoding="utf-8")


PacketRenderInput = tuple[PacketManifest, RiskTier] | tuple[PacketManifest, RiskTier, RiskTierLabel | str]


def _default_risk_tier_label(publish_action: RiskTier) -> str:
    if publish_action is RiskTier.HARD_FAIL:
        return RiskTierLabel.TIER4_GOVERNANCE.value
    if publish_action is RiskTier.BOT_PR:
        return RiskTierLabel.TIER2_INTERPRETATION.value
    return RiskTierLabel.TIER0_CATALOG.value


def _normalize_packet_input(packet: PacketRenderInput) -> tuple[PacketManifest, RiskTier, str]:
    if len(packet) == 2:
        manifest, publish_action = packet
        return manifest, publish_action, _default_risk_tier_label(publish_action)
    manifest, publish_action, risk_tier = packet
    risk_tier_value = risk_tier.value if isinstance(risk_tier, RiskTierLabel) else str(risk_tier)
    return manifest, publish_action, risk_tier_value


def _packet_frontmatter(manifest: PacketManifest, publish_action: RiskTier, risk_tier: str) -> str:
    frontmatter = {
        "id": manifest.id,
        "packet_type": manifest.type,
        "type": manifest.type,
        "title": manifest.title,
        "date": manifest.date,
        "owner": manifest.owner,
        "status": manifest.status,
        "task": manifest.task,
        "dataset": manifest.dataset,
        "split": manifest.split,
        "model": manifest.model,
        "claim_boundary": manifest.claim_boundary,
        "claim_status": manifest.claim_status,
        "summary": manifest.summary,
        "raw_paths": manifest.raw_paths,
        "intended_wiki_targets": manifest.intended_wiki_targets,
        "metrics_to_verify": manifest.metrics_to_verify,
        "claims": manifest.claims,
        "publish_action": publish_action.value,
        "risk_tier": risk_tier,
    }
    return yaml.safe_dump(as_jsonable(frontmatter), sort_keys=False).strip()


def _load_packet_mapping(packet_root: Path | None, manifest: PacketManifest, label: str) -> dict[str, Any]:
    if packet_root is None:
        return {}
    raw_path = manifest.raw_path_map.get(label)
    if not raw_path:
        return {}
    source = packet_root / raw_path
    if not source.exists() or not source.is_file():
        return {}
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def _slug_from_value(value: Any, fallback: str) -> str:
    if isinstance(value, str):
        candidate = value.strip().lower()
    else:
        candidate = ""
    candidate = re.sub(r"[^a-z0-9]+", "-", candidate).strip("-")
    candidate = candidate or fallback
    _validate_kebab_id(candidate)
    return candidate


def render_target_path(manifest: PacketManifest, packet_root: Path | None = None) -> str:
    if manifest.type is PacketType.DATASET:
        data = _load_packet_mapping(packet_root, manifest, "dataset")
        page_id = _slug_from_value(data.get("name") or manifest.dataset.name, manifest.id)
        return packet_target_path(manifest.type, page_id)
    if manifest.type is PacketType.BENCHMARK:
        data = _load_packet_mapping(packet_root, manifest, "benchmark")
        page_id = _slug_from_value(data.get("name"), manifest.id)
        return packet_target_path(manifest.type, page_id)
    return packet_target_path(manifest.type, manifest.id)


def _lineage_lines(manifest: PacketManifest) -> list[str]:
    dataset = manifest.dataset
    split = manifest.split
    model = manifest.model
    return [
        f"- owner: `{manifest.owner}`",
        f"- status: `{manifest.status}`",
        f"- task: `{manifest.task}`",
        f"- dataset: `{dataset.name}` (`{dataset.version}`)",
        f"- split: `{split.name}`",
        f"- model: `{model.family}`",
        f"- claim_boundary: {manifest.claim_boundary}",
        f"- claim_status: `{manifest.claim_status}`",
    ]


def _format_scalar(value: Any) -> str:
    if value is None:
        return "`null`"
    if isinstance(value, bool):
        return "`true`" if value else "`false`"
    if isinstance(value, (int, float)):
        return f"`{value}`"
    return f"`{str(value)}`"


def _mapping_lines(data: dict[str, Any], skip: set[str] | None = None) -> list[str]:
    skip = skip or set()
    lines: list[str] = []
    for key, value in data.items():
        if key in skip:
            continue
        if isinstance(value, dict):
            lines.append(f"- {key}:")
            lines.extend(f"  - {inner_key}: {_format_scalar(inner_value)}" for inner_key, inner_value in value.items())
        elif isinstance(value, list):
            lines.append(f"- {key}:")
            lines.extend(f"  - {_format_scalar(item)}" for item in value)
        else:
            lines.append(f"- {key}: {_format_scalar(value)}")
    return lines


def _dataset_entity_section(data: dict[str, Any]) -> list[str]:
    if not data:
        return []
    lines = ["", "## Dataset Entity", ""]
    for key in ["name", "version"]:
        if key in data:
            lines.append(f"- {key}: {_format_scalar(data[key])}")
    if data.get("modalities"):
        lines.extend(["", "### Modalities", ""])
        lines.extend(f"- {_format_scalar(item)}" for item in data["modalities"])
    if data.get("package_files"):
        lines.extend(["", "### Package Files", ""])
        lines.extend(f"- {_format_scalar(item)}" for item in data["package_files"])
    if isinstance(data.get("splits"), dict):
        lines.extend(["", "### Split Policy", ""])
        lines.extend(_mapping_lines(data["splits"]))
    if data.get("leakage_risks"):
        lines.extend(["", "### Leakage Risks", ""])
        lines.extend(f"- {_format_scalar(item)}" for item in data["leakage_risks"])
    if isinstance(data.get("provenance"), dict):
        lines.extend(["", "### Provenance", ""])
        lines.extend(_mapping_lines(data["provenance"]))
    return lines


def _benchmark_entity_section(data: dict[str, Any]) -> list[str]:
    if not data:
        return []
    lines = ["", "## Benchmark Entity", ""]
    for key in ["name", "dataset_ref", "task_family"]:
        if key in data:
            lines.append(f"- {key}: {_format_scalar(data[key])}")
    targets = data.get("targets")
    if isinstance(targets, list) and targets:
        lines.extend(["", "### Targets", "", "| id | kind | description |", "| --- | --- | --- |"])
        for target in targets:
            if isinstance(target, dict):
                lines.append(
                    f"| {target.get('id', '')} | {target.get('kind', '')} | {target.get('description', '')} |"
                )
            else:
                lines.append(f"| {target} |  |  |")
    if isinstance(data.get("primary_metric"), dict):
        lines.extend(["", "### Primary Metric", ""])
        lines.extend(_mapping_lines(data["primary_metric"]))
    if isinstance(data.get("evaluation_policy"), dict):
        lines.extend(["", "### Evaluation Policy", ""])
        lines.extend(_mapping_lines(data["evaluation_policy"]))
    if data.get("claim_boundaries"):
        lines.extend(["", "### Claim Boundaries", ""])
        lines.extend(f"- {_format_scalar(item)}" for item in data["claim_boundaries"])
    if isinstance(data.get("public_leaderboard"), dict):
        lines.extend(["", "### Public Leaderboard", ""])
        lines.extend(_mapping_lines(data["public_leaderboard"]))
    if data.get("working_implications"):
        lines.extend(["", "### Working Implications", ""])
        lines.extend(f"- {_format_scalar(item)}" for item in data["working_implications"])
    return lines


def _strip_packet_markdown(text: str, title: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end_index = None
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_index = index
                break
        if end_index is not None:
            lines = lines[end_index + 1 :]
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        heading = lines[0][2:].strip()
        if heading == title:
            lines = lines[1:]
    return "\n".join(lines).strip()


def _packet_markdown_body(packet_root: Path | None, title: str, target_by_packet_id: dict[str, str]) -> str:
    if packet_root is None:
        return ""
    packet_path = packet_root / "packet.md"
    if not packet_path.exists() or not packet_path.is_file():
        return ""
    try:
        body = _strip_packet_markdown(packet_path.read_text(encoding="utf-8"), title)
    except (OSError, UnicodeDecodeError):
        return ""
    for packet_id, target in target_by_packet_id.items():
        body = body.replace(f"[[datasets/{packet_id}]]", f"[[{target}]]")
        body = body.replace(f"[[benchmarks/{packet_id}]]", f"[[{target}]]")
        body = body.replace(f"[[sources/{packet_id}]]", f"[[{target}]]")
    return body


def _structured_sections(manifest: PacketManifest, packet_root: Path | None) -> list[str]:
    if manifest.type is PacketType.DATASET:
        return _dataset_entity_section(_load_packet_mapping(packet_root, manifest, "dataset"))
    if manifest.type is PacketType.BENCHMARK:
        return _benchmark_entity_section(_load_packet_mapping(packet_root, manifest, "benchmark"))
    return []


def _packet_page(
    manifest: PacketManifest,
    publish_action: RiskTier,
    risk_tier: str,
    run_id: str,
    packet_root: Path | None,
    target_by_packet_id: dict[str, str],
) -> str:
    lines = [
        "---",
        _packet_frontmatter(manifest, publish_action, risk_tier),
        "---",
        "",
        f"# {manifest.title}",
        "",
        f"- packet: `{manifest.id}`",
        f"- generated_by_run: `{run_id}`",
        f"- publish_action: `{publish_action.value}`",
        f"- risk_tier: `{risk_tier}`",
        f"- compiled_packet: [automation/.cache/compiled/{manifest.id}.json](../../automation/.cache/compiled/{manifest.id}.json)",
        *_lineage_lines(manifest),
    ]
    if manifest.date:
        lines.append(f"- date: `{manifest.date}`")
    if manifest.raw_paths:
        lines.append("- raw_evidence:")
        lines.extend(f"  - `{path}`" for path in manifest.raw_paths)
    if manifest.type in REVIEW_TYPES or any(claim.status == "supported" for claim in manifest.claims):
        lines.append("- review-required: true")
    lines.extend(["", "## Summary", "", manifest.summary or "No summary provided."])
    lines.extend(_structured_sections(manifest, packet_root))
    packet_body = _packet_markdown_body(packet_root, manifest.title, target_by_packet_id)
    if packet_body:
        lines.extend(["", "## Packet Synthesis", "", packet_body])
    if manifest.metrics_to_verify:
        lines.extend(["", "## Metrics", "", "raw-evidence-backed metric checks:"])
        lines.extend(
            f"- `{metric.metric_key}`: reported `{metric.reported_value}`, raw_path `{metric.raw_path}`, tolerance `{metric.tolerance}`"
            for metric in manifest.metrics_to_verify
        )
    if manifest.claims:
        lines.extend(["", "## Claims", ""])
        lines.extend(f"- {claim.status}: {claim.text}" for claim in manifest.claims)
    return "\n".join(lines).rstrip() + "\n"


def _read(path: Path, default: str) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else default


def _markdown_link_text(value: str) -> str:
    escaped = html.escape(value, quote=False)
    return escaped.replace("[", "\\[").replace("]", "\\]").replace("\n", " ")


def _wiki_index_href(rel: str) -> str:
    return rel.removeprefix("wiki/")


def _bounded_latest_page(prefix: str, entries: list[str], policy: IngestPolicy | None) -> str:
    max_entries = policy.latest_context_max_entries if policy else IngestPolicy(agents_text="").latest_context_max_entries
    max_chars = policy.latest_context_max_chars if policy else IngestPolicy(agents_text="").latest_context_max_chars
    trimmed = entries[:max_entries]
    while trimmed:
        page = _replace_block(prefix, LATEST_START, LATEST_END, "\n\n".join(trimmed))
        if len(page) <= max_chars:
            return page
        trimmed.pop()
    return _replace_block(prefix, LATEST_START, LATEST_END, "")


def render_packets(
    repo_root: Path,
    packets: list[PacketRenderInput],
    run_id: str,
    policy: IngestPolicy | None = None,
    packet_roots: dict[str, Path] | None = None,
) -> RenderResult:
    changed: list[str] = []
    wiki = repo_root / "wiki"
    wiki.mkdir(exist_ok=True)
    rendered_targets: list[tuple[PacketManifest, str]] = []
    normalized_packets = [_normalize_packet_input(packet) for packet in packets]
    roots = packet_roots or {}
    target_by_packet_id = {
        manifest.id: Path(render_target_path(manifest, roots.get(manifest.id)))
        .with_suffix("")
        .as_posix()
        .removeprefix("wiki/")
        for manifest, _publish_action, _risk_tier in normalized_packets
    }
    for manifest, publish_action, risk_tier in normalized_packets:
        packet_root = roots.get(manifest.id)
        rel = render_target_path(manifest, packet_root)
        target = repo_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            _packet_page(manifest, publish_action, risk_tier, run_id, packet_root, target_by_packet_id),
            encoding="utf-8",
        )
        rendered_targets.append((manifest, rel))
        changed.append(rel)

    index = wiki / "index.md"
    index_text = _read(index, "# Index\n")
    entries = sorted(
        set(
            [
                *_existing_block_lines(index_text, INDEX_START, INDEX_END),
                *[
                    f"- [{_markdown_link_text(manifest.title)}]({_wiki_index_href(rel)}) - `{manifest.type.value}`"
                    for manifest, rel in rendered_targets
                ],
            ]
        )
    )
    index.write_text(_replace_block(index_text, INDEX_START, INDEX_END, "\n".join(entries)), encoding="utf-8")
    changed.append("wiki/index.md")

    log = wiki / "log.md"
    for manifest, rel in rendered_targets:
        date = manifest.date or "undated"
        _append_once(log, f"## [{date}] ingest | {manifest.id}\n\n- target: `{rel}`\n- run: `{run_id}`")
    changed.append("wiki/log.md")

    latest = wiki / "latest-context.md"
    latest_text = _read(latest, "# Latest Context\n\n[[index]] [[overview]] [[log]]\n")
    previous = ""
    if LATEST_START in latest_text and LATEST_END in latest_text and latest_text.index(LATEST_START) < latest_text.index(LATEST_END):
        previous = latest_text[latest_text.index(LATEST_START) + len(LATEST_START) : latest_text.index(LATEST_END)].strip()
    new_entries = []
    rendered_rel_by_id = {manifest.id: rel for manifest, rel in rendered_targets}
    for manifest, publish_action, risk_tier in normalized_packets:
        rel = rendered_rel_by_id[manifest.id]
        lines = [
            f"### {run_id} | {manifest.id}",
            "",
            f"- link: [[{Path(rel).with_suffix('').as_posix().removeprefix('wiki/')}]]",
            f"- publish_action: `{publish_action.value}`",
            f"- risk_tier: `{risk_tier}`",
        ]
        if publish_action is RiskTier.BOT_PR or manifest.type in REVIEW_TYPES:
            lines.append("- review-required: true")
        new_entries.append("\n".join(lines))
    prefix = "# Latest Context\n\n[[index]] [[overview]] [[log]]\n"
    latest.write_text(_bounded_latest_page(prefix, [*new_entries, *_split_latest_entries(previous)], policy), encoding="utf-8")
    changed.append("wiki/latest-context.md")

    deduped = list(dict.fromkeys(changed))
    return RenderResult(changed_paths=deduped)
