# Wiki Policy Structure Renovation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Renovate Team LLM Wiki so packet skill, ingest, synthesis, health checks, workflows, and migrated wiki content all follow one canonical route contract.

**Architecture:** Add a machine-readable wiki route contract and a single Python interpreter for it, then route all repo-side consumers through that interpreter. Vendor the same contract into the packet skill repo, verify parity, then use a first-class migration CLI to move deprecated wiki pages into canonical namespaces with tombstones and link rewrites.

**Tech Stack:** Python 3.13, pytest, unittest, PyYAML `safe_load`, GitHub Actions YAML, markdown wiki files, `team_llm_wiki` CLI, packet skill scripts.

---

## Source Documents

- `/home/chunoh/.gstack/projects/ETRI/ceo-plans/2026-06-12-wiki-policy-structure-renovation.md`
- `/home/chunoh/.gstack/projects/ETRI/chunoh-main-eng-review-test-plan-20260612-175838.md`
- `/home/chunoh/ETRI/team_llm_wiki/AGENTS.md`
- `/home/chunoh/ETRI/team_llm_wiki/CLAUDE.md`
- `/home/chunoh/ETRI/team-llm-wiki-packet-skill/SKILL.md`

## Scope Split

This is intentionally one implementation wave with two PRs.

PR 1: contract and automation alignment.

- Add and parse `wiki-route-contract.v1.yaml`.
- Route repo ingest, preview, synthesis, health, risk, and workflow guards through the contract.
- Vendor the same contract into packet skill and update skill route helpers.
- Do not physically migrate current wiki pages.

PR 2: content migration and final smoke.

- Run contract-backed migration CLI.
- Move or merge deprecated wiki pages.
- Leave tombstones at old paths.
- Rewrite non-log wiki links.
- Run full tests, packet skill tests, install verification, and one DACON GPT-5.5 smoke.

## File Structure

### `/home/chunoh/ETRI/team_llm_wiki`

- Create `automation/contracts/wiki-route-contract.v1.yaml`: source-of-truth route contract.
- Create `src/team_llm_wiki/wiki_ingest/route_contract.py`: parser, semantic validator, and route helper API.
- Create `src/team_llm_wiki/wiki_ingest/migration.py`: migration dry-run/run engine, inventory, tombstones, link rewrites, and report model.
- Modify `src/team_llm_wiki/wiki_ingest/routes.py`: keep compatibility exports backed by `route_contract.py`.
- Modify `src/team_llm_wiki/wiki_ingest/wiki_plan.py`: route-contract synthesis path checks and migration compatibility flag handling.
- Modify `src/team_llm_wiki/wiki_ingest/guards.py`: expected packet target route from the contract.
- Modify `src/team_llm_wiki/wiki_ingest/render.py`: canonical render target paths.
- Modify `src/team_llm_wiki/wiki_ingest/risk.py`: canonical/deprecated route risk from the contract.
- Modify `src/team_llm_wiki/wiki_ingest/health.py`: canonical required pages, deprecated namespace policy, tombstone checks.
- Modify `src/team_llm_wiki/wiki_ingest/brief.py`: treat `wiki/briefs` as generated compatibility only.
- Modify `src/team_llm_wiki/wiki_ingest/llm_synthesis.py`: canonical integration paths, prompt policy, output path validation.
- Modify `src/team_llm_wiki/wiki_ingest/packet_skill_compatibility.py`: contract-backed packet skill page checks.
- Modify `src/team_llm_wiki/cli.py`: add `plan-wiki-route-migration`, `run-wiki-route-migration`, and migration mode flags.
- Modify `.github/workflows/wiki-pr-validate.yml`: preview deprecated path failures without enabling migration mode.
- Modify `.github/workflows/wiki-main-ingest.yml`: default-off migration mode and route-contract checks.
- Modify `.github/workflows/wiki-llm-synthesis.yml`: default-off migration mode and canonical synthesis validation.
- Modify `.github/workflows/wiki-health-check.yml`: generated-compatibility brief handling.
- Create or extend tests under `tests/wiki_ingest/` and `tests/e2e/`.
- Modify `README.md`, `AGENTS.md`, `CLAUDE.md`, and `wiki/team/*.md` to describe the canonical policy.
- PR2 modifies current `wiki/**` files according to the migration report.

### `/home/chunoh/ETRI/team-llm-wiki-packet-skill`

- Create `references/wiki-route-contract.v1.yaml`: vendored contract matching the wiki repo.
- Modify `scripts/packet_skill_common.py`: shared contract loader and `packet_route()`.
- Modify `scripts/merge_packet_graph.py`: canonical proposed pages for model, preprocessing, performance, claim, target, and report nodes.
- Modify `scripts/make_packet_draft.py`: canonical `route` and `intended_wiki_targets`.
- Modify `scripts/preview_packet.py`: preview canonical routes and deprecated warnings.
- Modify `scripts/render_packet.py`: render canonical route metadata.
- Modify `scripts/verify_install.py`: require vendored route contract and verify it loads.
- Modify `README.md`, `SKILL.md`, and `references/*.md` to describe the 9 canonical wiki namespaces.
- Extend packet skill tests under `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests`.

## Commit Protocol

Every commit must follow the workspace Lore protocol. Use this pattern, adjusting the intent line and verification lines:

```bash
git commit -m "Centralize wiki route policy in a contract" \
  -m "Constraint: wiki and packet skill routes must not drift." \
  -m "Rejected: keep hardcoded route dictionaries | they already diverged across repos." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: future route changes must update wiki-route-contract.v1.yaml first." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_routes.py -q" \
  -m "Not-tested: full suite deferred to PR checkpoint"
```

## Task 1: Add Route Contract And Parser

**Files:**

- Create: `/home/chunoh/ETRI/team_llm_wiki/automation/contracts/wiki-route-contract.v1.yaml`
- Create: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/route_contract.py`
- Create: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_routes.py`

- [ ] **Step 1: Write the failing route contract tests**

Create `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_routes.py` with this content:

```python
from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest.models import IngestFailure, PacketType
from team_llm_wiki.wiki_ingest.route_contract import (
    DEFAULT_CONTRACT_PATH,
    load_route_contract,
)


def test_load_default_route_contract_exposes_canonical_routes():
    contract = load_route_contract(Path("."))

    assert contract.version == 1
    assert contract.packet_route(PacketType.DATASET) == "wiki/preprocessing"
    assert contract.packet_route(PacketType.BENCHMARK) == "wiki/performance"
    assert contract.packet_route(PacketType.EXPERIMENT) == "wiki/reports"
    assert contract.packet_route(PacketType.REFERENCE) == "wiki/reports"
    assert contract.packet_route(PacketType.MEETING) == "wiki/reports"
    assert contract.is_canonical_path("wiki/performance/dacon-leaderboard-history.md")
    assert not contract.is_canonical_path("wiki/questions/sleep-lifelog-open-questions.md")


def test_deprecated_namespace_metadata_is_complete():
    contract = load_route_contract(Path("."))

    datasets = contract.deprecated_namespace_for_path("wiki/datasets/sleep-lifelog-2024.md")
    assert datasets is not None
    assert datasets.name == "datasets"
    assert datasets.path == "wiki/datasets"
    assert datasets.replacement == "wiki/preprocessing"
    assert datasets.allowed_mode == "tombstone_only"

    briefs = contract.deprecated_namespace_for_path("wiki/briefs/latest.md")
    assert briefs is not None
    assert briefs.allowed_mode == "generated_compatibility_only"


def test_safe_synthesis_paths_reject_deprecated_namespaces_outside_migration_mode():
    contract = load_route_contract(Path("."))

    assert contract.is_allowed_synthesis_path("wiki/features/app-context-windows.md")
    assert not contract.is_allowed_synthesis_path("wiki/questions/sleep-lifelog-open-questions.md")
    assert contract.is_allowed_synthesis_path(
        "wiki/questions/sleep-lifelog-open-questions.md",
        migration_mode=True,
    )


def test_contract_load_fails_closed_for_missing_file(tmp_path):
    with pytest.raises(IngestFailure) as exc:
        load_route_contract(tmp_path)

    assert exc.value.code.value == "policy_missing"
    assert str(DEFAULT_CONTRACT_PATH) in exc.value.message


def test_contract_load_fails_closed_for_bad_packet_route(tmp_path):
    contract_path = tmp_path / DEFAULT_CONTRACT_PATH
    contract_path.parent.mkdir(parents=True)
    data = yaml.safe_load(Path(DEFAULT_CONTRACT_PATH).read_text(encoding="utf-8"))
    data["packet_routes"].pop("dataset")
    contract_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(IngestFailure) as exc:
        load_route_contract(tmp_path)

    assert exc.value.code.value == "policy_conflict"
    assert "missing packet route: dataset" in exc.value.message


def test_tombstone_validator_accepts_only_compatibility_body():
    contract = load_route_contract(Path("."))
    text = """---
page_role: compatibility
status: deprecated
canonical_target: wiki/preprocessing/sleep-lifelog-2024.md
---
# Deprecated Compatibility Page

This page has moved to [[preprocessing/sleep-lifelog-2024]].

Do not add new substantive content here. This file exists to preserve historical links and provenance.
"""

    assert contract.validate_tombstone("wiki/datasets/sleep-lifelog-2024.md", text) == []


def test_tombstone_validator_rejects_substantive_sections():
    contract = load_route_contract(Path("."))
    text = """---
page_role: compatibility
status: deprecated
canonical_target: wiki/preprocessing/sleep-lifelog-2024.md
---
# Deprecated Compatibility Page

## Metrics

- public_lb: 0.5917
"""

    errors = contract.validate_tombstone("wiki/datasets/sleep-lifelog-2024.md", text)
    assert any(error.code == "deprecated_tombstone_substantive_content" for error in errors)
```

- [ ] **Step 2: Run the route tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_routes.py -q
```

Expected: fails with `ModuleNotFoundError: No module named 'team_llm_wiki.wiki_ingest.route_contract'`.

- [ ] **Step 3: Add the route contract YAML**

Create `/home/chunoh/ETRI/team_llm_wiki/automation/contracts/wiki-route-contract.v1.yaml`:

```yaml
version: 1
canonical_namespaces:
  preprocessing:
    path: wiki/preprocessing
    required: true
  features:
    path: wiki/features
    required: true
  models:
    path: wiki/models
    required: true
  performance:
    path: wiki/performance
    required: true
  claims:
    path: wiki/claims
    required: true
  targets:
    path: wiki/targets
    required: true
  decisions:
    path: wiki/decisions
    required: true
  reports:
    path: wiki/reports
    required: true
  team:
    path: wiki/team
    required: true
deprecated_namespaces:
  datasets:
    path: wiki/datasets
    replacement: wiki/preprocessing
    allowed_mode: tombstone_only
  benchmarks:
    path: wiki/benchmarks
    replacement: wiki/performance
    allowed_mode: tombstone_only
  submissions:
    path: wiki/submissions
    replacement: wiki/performance
    allowed_mode: tombstone_only
  questions:
    path: wiki/questions
    replacement: wiki/targets
    allowed_mode: tombstone_only
  experiments:
    path: wiki/experiments
    replacement: wiki/reports
    allowed_mode: tombstone_only
  sources:
    path: wiki/sources
    replacement: wiki/reports
    allowed_mode: tombstone_only
  briefs:
    path: wiki/briefs
    replacement: wiki/reports
    allowed_mode: generated_compatibility_only
packet_routes:
  reference: wiki/reports
  meeting: wiki/reports
  experiment: wiki/reports
  feature: wiki/features
  model: wiki/models
  performance: wiki/performance
  preprocessing: wiki/preprocessing
  augmentation: wiki/preprocessing
  dataset: wiki/preprocessing
  benchmark: wiki/performance
allowed_page_roles:
  - entrypoint
  - registry
  - hub
  - leaf
  - packet_review
  - report
  - policy
required_entrypoints:
  - wiki/latest-context.md
  - wiki/index.md
  - wiki/overview.md
  - wiki/log.md
required_pages:
  - wiki/team/ml-ai-hackathon-entity-model.md
  - wiki/team/packet-quality-standard.md
  - wiki/team/page-taxonomy.md
  - wiki/team/llm-wiki-operating-harness.md
  - wiki/claims/current-supported-claims.md
  - wiki/preprocessing/canonical-split-and-leakage-policy.md
  - wiki/performance/dacon-leaderboard-history.md
migration_map:
  wiki/datasets/sleep-lifelog-2024.md: wiki/preprocessing/sleep-lifelog-2024.md
  wiki/benchmarks/sleep-health-hackathon-v0.md: wiki/performance/sleep-health-hackathon-evaluation-policy.md
  wiki/submissions/dacon-leaderboard-history.md: wiki/performance/dacon-leaderboard-history.md
  wiki/questions/sleep-lifelog-open-questions.md: wiki/targets/sleep-lifelog-open-issues.md
  wiki/questions/section07-followup-backlog.md: wiki/targets/section07-followup-backlog.md
  wiki/experiments/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md: wiki/reports/2026-05-29-labelwise-weekly-progress-target-bottlenecks.md
  wiki/experiments/2026-05-29-v200-v209-sparse-splice-review.md: wiki/reports/2026-05-29-v200-v209-sparse-splice-review.md
  wiki/experiments/2026-06-01-lifelog-section07-notebook-overview.md: wiki/reports/2026-06-01-lifelog-section07-notebook-overview.md
  wiki/experiments/2026-06-01-lifelog-section07-working-notes.md: wiki/reports/2026-06-01-lifelog-section07-working-notes.md
  wiki/sources/2026-06-01-dacon-leaderboard-claim-boundary.md: wiki/performance/2026-06-01-dacon-leaderboard-claim-boundary.md
```

- [ ] **Step 4: Implement `route_contract.py`**

Create `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/route_contract.py` with these public names and behavior:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import FailureCode, HealthError, IngestFailure, PacketType

DEFAULT_CONTRACT_PATH = Path("automation/contracts/wiki-route-contract.v1.yaml")
SUPPORTED_VERSION = 1
TOMBSTONE_HEADING = "# Deprecated Compatibility Page"
SUBSTANTIVE_TOMBSTONE_MARKERS = (
    "## Raw Evidence",
    "raw_evidence:",
    "## Metrics",
    "## Claim",
    "## Claims",
    "## Open Questions",
    "## Questions",
    "| metric |",
    "public_lb:",
    "local_oof:",
)


@dataclass(frozen=True)
class NamespaceRoute:
    name: str
    path: str
    required: bool = False


@dataclass(frozen=True)
class DeprecatedNamespace:
    name: str
    path: str
    replacement: str
    allowed_mode: str


@dataclass(frozen=True)
class WikiRouteContract:
    version: int
    canonical_namespaces: dict[str, NamespaceRoute]
    deprecated_namespaces: dict[str, DeprecatedNamespace]
    packet_routes: dict[str, str]
    allowed_page_roles: set[str]
    required_entrypoints: tuple[str, ...]
    required_pages: tuple[str, ...]
    migration_map: dict[str, str]
    source_path: str

    @property
    def canonical_paths(self) -> tuple[str, ...]:
        return tuple(route.path for route in self.canonical_namespaces.values())

    @property
    def deprecated_paths(self) -> tuple[str, ...]:
        return tuple(route.path for route in self.deprecated_namespaces.values())

    def packet_route(self, packet_type: PacketType | str) -> str:
        key = packet_type.value if isinstance(packet_type, PacketType) else str(packet_type)
        try:
            return self.packet_routes[key]
        except KeyError as exc:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"missing packet route: {key}") from exc

    def is_canonical_path(self, rel_path: str) -> bool:
        return any(rel_path == prefix or rel_path.startswith(prefix + "/") for prefix in self.canonical_paths)

    def deprecated_namespace_for_path(self, rel_path: str) -> DeprecatedNamespace | None:
        for namespace in self.deprecated_namespaces.values():
            if rel_path == namespace.path or rel_path.startswith(namespace.path + "/"):
                return namespace
        return None

    def is_allowed_synthesis_path(self, rel_path: str, *, migration_mode: bool = False) -> bool:
        path = Path(rel_path)
        parts = path.parts
        if path.is_absolute() or ".." in parts:
            return False
        if len(parts) < 3 or parts[0] != "wiki" or not rel_path.endswith(".md"):
            return False
        if self.is_canonical_path(rel_path):
            return True
        return migration_mode and self.deprecated_namespace_for_path(rel_path) is not None

    def is_generated_compatibility_path(self, rel_path: str) -> bool:
        namespace = self.deprecated_namespace_for_path(rel_path)
        return namespace is not None and namespace.allowed_mode == "generated_compatibility_only"

    def validate_tombstone(self, rel_path: str, text: str) -> list[HealthError]:
        errors: list[HealthError] = []
        namespace = self.deprecated_namespace_for_path(rel_path)
        if namespace is None:
            return errors
        if namespace.allowed_mode == "generated_compatibility_only":
            return errors
        if "page_role: compatibility" not in text:
            errors.append(HealthError("invalid_deprecated_tombstone", "tombstone missing page_role: compatibility", rel_path))
        if "status: deprecated" not in text:
            errors.append(HealthError("invalid_deprecated_tombstone", "tombstone missing status: deprecated", rel_path))
        if "canonical_target:" not in text:
            errors.append(HealthError("invalid_deprecated_tombstone", "tombstone missing canonical_target", rel_path))
        headings = [line.strip() for line in text.splitlines() if line.startswith("#")]
        if headings != [TOMBSTONE_HEADING]:
            errors.append(HealthError("invalid_deprecated_tombstone", "tombstone must contain only the deprecated compatibility heading", rel_path))
        for marker in SUBSTANTIVE_TOMBSTONE_MARKERS:
            if marker in text:
                errors.append(HealthError("deprecated_tombstone_substantive_content", f"tombstone contains substantive marker: {marker}", rel_path))
        return errors


def load_route_contract(repo_root: Path, contract_path: Path | None = None) -> WikiRouteContract:
    rel_path = contract_path or DEFAULT_CONTRACT_PATH
    path = rel_path if rel_path.is_absolute() else repo_root / rel_path
    if not path.exists():
        raise IngestFailure(FailureCode.POLICY_MISSING, f"route contract is missing: {rel_path}")
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"route contract could not be parsed: {exc}") from exc
    if not isinstance(payload, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "route contract must be a mapping")
    version = payload.get("version")
    if version != SUPPORTED_VERSION:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"unsupported route contract version: {version}")

    canonical = _canonical_namespaces(payload.get("canonical_namespaces"))
    deprecated = _deprecated_namespaces(payload.get("deprecated_namespaces"))
    packet_routes = _packet_routes(payload.get("packet_routes"), canonical)
    allowed_roles = _string_set(payload.get("allowed_page_roles"), "allowed_page_roles")
    required_entrypoints = tuple(_string_list(payload.get("required_entrypoints"), "required_entrypoints"))
    required_pages = tuple(_string_list(payload.get("required_pages"), "required_pages"))
    migration_map = _migration_map(payload.get("migration_map"), deprecated)
    _validate_replacements(deprecated, canonical)
    return WikiRouteContract(
        version=version,
        canonical_namespaces=canonical,
        deprecated_namespaces=deprecated,
        packet_routes=packet_routes,
        allowed_page_roles=allowed_roles,
        required_entrypoints=required_entrypoints,
        required_pages=required_pages,
        migration_map=migration_map,
        source_path=path.as_posix(),
    )
```

Add private helpers in the same file:

```python
def _canonical_namespaces(value: Any) -> dict[str, NamespaceRoute]:
    if not isinstance(value, dict) or not value:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "canonical_namespaces must be a non-empty mapping")
    result: dict[str, NamespaceRoute] = {}
    seen_paths: set[str] = set()
    for name, data in value.items():
        if not isinstance(data, dict):
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"canonical namespace must be a mapping: {name}")
        path = _wiki_dir(data.get("path"), f"canonical namespace {name}")
        if path in seen_paths:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"duplicate namespace path: {path}")
        seen_paths.add(path)
        result[str(name)] = NamespaceRoute(str(name), path, bool(data.get("required")))
    return result


def _deprecated_namespaces(value: Any) -> dict[str, DeprecatedNamespace]:
    if not isinstance(value, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "deprecated_namespaces must be a mapping")
    result: dict[str, DeprecatedNamespace] = {}
    seen_paths: set[str] = set()
    for name, data in value.items():
        if not isinstance(data, dict):
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"deprecated namespace must be a mapping: {name}")
        path = _wiki_dir(data.get("path"), f"deprecated namespace {name}")
        replacement = _wiki_dir(data.get("replacement"), f"deprecated namespace {name} replacement")
        allowed_mode = str(data.get("allowed_mode", "")).strip()
        if allowed_mode not in {"tombstone_only", "generated_compatibility_only"}:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"invalid deprecated namespace mode: {name}")
        if path in seen_paths:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"duplicate deprecated namespace path: {path}")
        seen_paths.add(path)
        result[str(name)] = DeprecatedNamespace(str(name), path, replacement, allowed_mode)
    return result


def _packet_routes(value: Any, canonical: dict[str, NamespaceRoute]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "packet_routes must be a mapping")
    required = {packet_type.value for packet_type in PacketType}
    missing = sorted(required - set(value))
    if missing:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"missing packet route: {missing[0]}")
    canonical_paths = {route.path for route in canonical.values()}
    routes: dict[str, str] = {}
    for key, raw_path in value.items():
        path = _wiki_dir(raw_path, f"packet route {key}")
        if path not in canonical_paths:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"packet route must target canonical namespace: {key} -> {path}")
        routes[str(key)] = path
    return routes


def _migration_map(value: Any, deprecated: dict[str, DeprecatedNamespace]) -> dict[str, str]:
    if not isinstance(value, dict):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, "migration_map must be a mapping")
    result: dict[str, str] = {}
    for source, target in value.items():
        source_path = _wiki_file(source, f"migration source {source}")
        target_path = _wiki_file(target, f"migration target {source}")
        if not any(source_path == route.path or source_path.startswith(route.path + "/") for route in deprecated.values()):
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"migration source is not deprecated: {source_path}")
        result[source_path] = target_path
    return result


def _validate_replacements(deprecated: dict[str, DeprecatedNamespace], canonical: dict[str, NamespaceRoute]) -> None:
    canonical_paths = {route.path for route in canonical.values()}
    for namespace in deprecated.values():
        if namespace.replacement not in canonical_paths:
            raise IngestFailure(FailureCode.POLICY_CONFLICT, f"deprecated namespace replacement is not canonical: {namespace.name}")


def _wiki_dir(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("wiki/") or value.endswith(".md") or ".." in Path(value).parts:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"{label} must be a relative wiki directory")
    return value.rstrip("/")


def _wiki_file(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.startswith("wiki/") or not value.endswith(".md") or ".." in Path(value).parts:
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"{label} must be a relative wiki markdown file")
    return value


def _string_list(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise IngestFailure(FailureCode.POLICY_CONFLICT, f"{label} must be a list of strings")
    return [item.strip() for item in value]


def _string_set(value: Any, label: str) -> set[str]:
    return set(_string_list(value, label))
```

- [ ] **Step 5: Run route tests and verify they pass**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_routes.py -q
```

Expected: `7 passed`.

- [ ] **Step 6: Commit Task 1**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add automation/contracts/wiki-route-contract.v1.yaml src/team_llm_wiki/wiki_ingest/route_contract.py tests/wiki_ingest/test_routes.py
git commit -m "Centralize wiki route policy in a contract" \
  -m "Constraint: wiki ingest and packet skill routes must not drift." \
  -m "Rejected: keep hardcoded route dictionaries | they already diverged across repo modules and skill scripts." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: future route changes must update automation/contracts/wiki-route-contract.v1.yaml first." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_routes.py -q" \
  -m "Not-tested: full suite deferred to PR1 checkpoint"
```

## Task 2: Wire Repo Route Consumers To The Contract

**Files:**

- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/routes.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/wiki_plan.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/guards.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/render.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/risk.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_guards.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_render.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_risk.py`
- Create: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_wiki_plan.py`

- [ ] **Step 1: Write failing tests for canonical routing**

Add these tests to the indicated files.

In `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_wiki_plan.py`:

```python
from pathlib import Path

import yaml

from team_llm_wiki.wiki_ingest.wiki_plan import load_wiki_plan


def test_wiki_plan_accepts_canonical_pages(tmp_path):
    packet_root = tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-run"
    packet_root.mkdir(parents=True)
    (packet_root / "wiki_plan.yaml").write_text(
        yaml.safe_dump(
            {
                "stable_entities": [
                    {
                        "id": "performance:dacon-public-05917",
                        "kind": "performance",
                        "page": "wiki/performance/dacon-public-05917-lgbm-xgb-anchor-reference.md",
                        "page_role": "leaf",
                    }
                ],
                "affected_pages": [
                    {"path": "wiki/claims/current-supported-claims.md", "role": "registry"}
                ],
            }
        ),
        encoding="utf-8",
    )

    result = load_wiki_plan(packet_root, repo_root=tmp_path)

    assert result.ok
    assert result.safe_paths == [
        "wiki/performance/dacon-public-05917-lgbm-xgb-anchor-reference.md",
        "wiki/claims/current-supported-claims.md",
    ]


def test_wiki_plan_rejects_deprecated_pages_outside_migration_mode(tmp_path):
    packet_root = tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-run"
    packet_root.mkdir(parents=True)
    (packet_root / "wiki_plan.yaml").write_text(
        yaml.safe_dump(
            {
                "affected_pages": [
                    {"path": "wiki/questions/sleep-lifelog-open-questions.md", "role": "hub"}
                ]
            }
        ),
        encoding="utf-8",
    )

    result = load_wiki_plan(packet_root, repo_root=Path("."))

    assert not result.safe_paths
    assert any("not an allowed synthesis wiki path" in warning for warning in result.warnings)


def test_wiki_plan_allows_deprecated_pages_in_migration_mode(tmp_path):
    packet_root = tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-run"
    packet_root.mkdir(parents=True)
    (packet_root / "wiki_plan.yaml").write_text(
        yaml.safe_dump(
            {
                "affected_pages": [
                    {
                        "path": "wiki/questions/sleep-lifelog-open-questions.md",
                        "role": "hub",
                        "migration_compatibility": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = load_wiki_plan(packet_root, repo_root=Path("."), migration_mode=True)

    assert result.safe_paths == ["wiki/questions/sleep-lifelog-open-questions.md"]
```

In `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_render.py`, update the existing render import:

```python
from team_llm_wiki.wiki_ingest.render import render_packets, render_target_path
```

Then append:

```python
def test_render_target_path_uses_contract_canonical_routes(tmp_path):
    packet = manifest(
        id="2026-05-29-sleep-lifelog-2024",
        type=PacketType.DATASET,
        intended_wiki_targets=["wiki/preprocessing/2026-05-29-sleep-lifelog-2024.md"],
    )

    assert render_target_path(packet) == "wiki/preprocessing/2026-05-29-sleep-lifelog-2024.md"
```

- [ ] **Step 2: Run focused tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest \
  tests/wiki_ingest/test_wiki_plan.py \
  tests/wiki_ingest/test_render.py::test_render_target_path_uses_contract_canonical_routes \
  -q
```

Expected: failures showing `load_wiki_plan()` does not accept `repo_root` or deprecated old route assertions still expect `wiki/datasets`.

- [ ] **Step 3: Update `routes.py`**

Replace the hardcoded `PACKET_ROUTE_MAP` construction in `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/routes.py` with contract-backed values:

```python
from __future__ import annotations

from pathlib import Path

from .models import PacketType
from .models import _validate_kebab_id
from .route_contract import load_route_contract


def _default_route_map() -> dict[PacketType, str]:
    contract = load_route_contract(Path("."))
    return {packet_type: contract.packet_route(packet_type) for packet_type in PacketType}


PACKET_ROUTE_MAP = _default_route_map()


def packet_route(packet_type: PacketType, *, repo_root: Path | None = None) -> str:
    contract = load_route_contract(repo_root or Path("."))
    return contract.packet_route(packet_type)


def packet_target_path(packet_type: PacketType, packet_id: str, *, repo_root: Path | None = None) -> str:
    _validate_kebab_id(packet_id)
    return f"{packet_route(packet_type, repo_root=repo_root)}/{packet_id}.md"
```

- [ ] **Step 4: Update `wiki_plan.py` signature and path validation**

Change `load_wiki_plan(packet_root: Path)` to:

```python
def load_wiki_plan(packet_root: Path, *, repo_root: Path | None = None, migration_mode: bool = False) -> WikiPlanParseResult:
```

Pass `repo_root` and `migration_mode` through `_validate_page_paths()` and `_is_safe_synthesis_path()`. The safe path helper should call:

```python
contract = load_route_contract(repo_root or Path("."))
return contract.is_allowed_synthesis_path(value, migration_mode=migration_mode)
```

Also extend `WikiPlanPage` with:

```python
migration_compatibility: bool = False
```

When parsing dict entries, set it from `bool(item.get("migration_compatibility"))`. If a deprecated path has `migration_compatibility: true` but `migration_mode` is false, keep it out of `safe_paths` and add the existing warning.

- [ ] **Step 5: Update guard, render, and risk imports**

In `guards.py`, replace:

```python
expected_route = PACKET_ROUTE_MAP[manifest.type] + "/"
```

with:

```python
expected_route = packet_route(manifest.type, repo_root=repo_root) + "/"
```

In `render.py`, call:

```python
return packet_target_path(manifest.type, page_id, repo_root=Path("."))
```

for dataset and benchmark paths, and the same helper for all other packet types.

In `risk.py`, replace hardcoded `HIGH_RISK_PATH_PREFIXES` with a function:

```python
def _high_risk_path_prefixes() -> tuple[str, ...]:
    contract = load_route_contract(Path("."))
    return tuple(f"{path}/" for path in contract.canonical_paths if path != "wiki/team")
```

Then call it inside `classify_risk()` so route changes come from the contract.

- [ ] **Step 6: Update old route assertions in tests**

Search:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
rg -n "wiki/datasets|wiki/benchmarks|wiki/experiments|wiki/questions|wiki/submissions|wiki/sources" tests/wiki_ingest tests/e2e
```

Update assertions that refer to generated new output so they expect canonical routes. Keep historical fixture content only when the test is explicitly about deprecated compatibility.

- [ ] **Step 7: Run focused route consumer tests**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest \
  tests/wiki_ingest/test_routes.py \
  tests/wiki_ingest/test_wiki_plan.py \
  tests/wiki_ingest/test_guards.py \
  tests/wiki_ingest/test_render.py \
  tests/wiki_ingest/test_risk.py \
  -q
```

Expected: all selected tests pass.

- [ ] **Step 8: Commit Task 2**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add src/team_llm_wiki/wiki_ingest/routes.py src/team_llm_wiki/wiki_ingest/wiki_plan.py src/team_llm_wiki/wiki_ingest/guards.py src/team_llm_wiki/wiki_ingest/render.py src/team_llm_wiki/wiki_ingest/risk.py tests/wiki_ingest tests/e2e
git commit -m "Route ingest consumers through the wiki contract" \
  -m "Constraint: generated packet targets must use canonical namespaces." \
  -m "Rejected: update literals while keeping old route maps | that would recreate drift." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: tests for generated paths should assert contract behavior, not old namespace literals." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_routes.py tests/wiki_ingest/test_wiki_plan.py tests/wiki_ingest/test_guards.py tests/wiki_ingest/test_render.py tests/wiki_ingest/test_risk.py -q" \
  -m "Not-tested: workflow and LLM synthesis paths deferred to later tasks"
```

## Task 3: Strengthen Health Checks And Brief Compatibility

**Files:**

- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/health.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/brief.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_health.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_brief.py`

- [ ] **Step 1: Add health tests for canonical requirements and tombstones**

Append to `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_health.py`:

```python
def test_health_requires_canonical_leaderboard_history(tmp_path):
    seed_clean(tmp_path)
    old = tmp_path / "wiki" / "submissions" / "dacon-leaderboard-history.md"
    old.parent.mkdir(parents=True, exist_ok=True)
    old.write_text("# Old Leaderboard\n", encoding="utf-8")
    new = tmp_path / "wiki" / "performance" / "dacon-leaderboard-history.md"
    new.unlink()

    report = check_wiki_health(tmp_path)

    assert not report.ok
    assert any(error.path == "wiki/performance/dacon-leaderboard-history.md" for error in report.errors)


def test_health_rejects_substantive_deprecated_page_after_migration(tmp_path):
    seed_clean(tmp_path)
    deprecated = tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md"
    deprecated.parent.mkdir(parents=True, exist_ok=True)
    deprecated.write_text("# Sleep Lifelog\n\n## Metrics\n\n- public_lb: 0.5917\n", encoding="utf-8")

    report = check_wiki_health(tmp_path, deprecated_mode="strict")

    assert not report.ok
    assert any(error.code == "deprecated_namespace_substantive_content" for error in report.errors)


def test_health_accepts_deprecated_tombstone_in_strict_mode(tmp_path):
    seed_clean(tmp_path)
    deprecated = tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md"
    deprecated.parent.mkdir(parents=True, exist_ok=True)
    deprecated.write_text(
        """---
page_role: compatibility
status: deprecated
canonical_target: wiki/preprocessing/sleep-lifelog-2024.md
---
# Deprecated Compatibility Page

This page has moved to [[preprocessing/sleep-lifelog-2024]].

Do not add new substantive content here. This file exists to preserve historical links and provenance.
""",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path, deprecated_mode="strict")

    assert report.ok
```

- [ ] **Step 2: Run health tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_health.py -q
```

Expected: failures for missing `deprecated_mode` argument and old required `wiki/submissions/dacon-leaderboard-history.md`.

- [ ] **Step 3: Update `health.py` required pages and deprecated checks**

Change `check_wiki_health()` signature:

```python
def check_wiki_health(repo_root: Path, report_path: Path | None = None, *, deprecated_mode: str = "warn_existing") -> HealthReport:
```

Load the contract once:

```python
contract = load_route_contract(repo_root)
```

Replace `REQUIRED_ENTITY_MODEL_PAGES` usage with:

```python
required_pages = set(contract.required_pages)
```

Add a helper:

```python
def _deprecated_namespace_errors(repo_root: Path, contract: WikiRouteContract, *, deprecated_mode: str) -> list[HealthError]:
    wiki_root = repo_root / "wiki"
    if not wiki_root.exists():
        return []
    errors: list[HealthError] = []
    for path in sorted(wiki_root.rglob("*.md")):
        rel_path = path.relative_to(repo_root).as_posix()
        namespace = contract.deprecated_namespace_for_path(rel_path)
        if namespace is None:
            continue
        text = path.read_text(encoding="utf-8")
        if namespace.allowed_mode == "generated_compatibility_only":
            if path.name == ".gitkeep":
                continue
            if "<!-- wiki-brief:generated -->" not in text and path.name != ".gitkeep":
                errors.append(HealthError("deprecated_generated_compatibility_unmarked", f"{rel_path} is not marked as generated compatibility", rel_path))
            continue
        tombstone_errors = contract.validate_tombstone(rel_path, text)
        if tombstone_errors:
            if deprecated_mode == "strict":
                errors.extend(tombstone_errors)
            elif _looks_substantive_deprecated_page(text):
                errors.append(HealthError("deprecated_namespace_substantive_content", f"{rel_path} contains substantive content in deprecated namespace", rel_path))
    return errors
```

Add:

```python
def _looks_substantive_deprecated_page(text: str) -> bool:
    markers = ("## Metrics", "raw_evidence:", "## Open Questions", "claim_status:", "public_lb", "local_oof")
    return any(marker in text for marker in markers)
```

Call `_deprecated_namespace_errors()` inside `check_wiki_health()`.

- [ ] **Step 4: Mark generated briefs**

In `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/brief.py`, add this marker near the top of every generated brief body:

```markdown
<!-- wiki-brief:generated -->
```

Update `tests/wiki_ingest/test_brief.py` assertions so generated daily, weekly, stale-claims, and latest briefs include the marker.

- [ ] **Step 5: Run health and brief tests**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_health.py tests/wiki_ingest/test_brief.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit Task 3**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add src/team_llm_wiki/wiki_ingest/health.py src/team_llm_wiki/wiki_ingest/brief.py tests/wiki_ingest/test_health.py tests/wiki_ingest/test_brief.py
git commit -m "Enforce canonical wiki health policy" \
  -m "Constraint: deprecated namespaces may not regain substantive content." \
  -m "Rejected: warnings only for invalid tombstones | PR2 must make old paths review-safe." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: generated wiki/briefs files must remain marked compatibility artifacts." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_health.py tests/wiki_ingest/test_brief.py -q" \
  -m "Not-tested: full suite deferred to PR1 checkpoint"
```

## Task 4: Add Migration CLI And Report Engine

**Files:**

- Create: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/migration.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/cli.py`
- Create: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_migration.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/e2e/test_cli.py`

- [ ] **Step 1: Write migration tests**

Create `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_migration.py`:

```python
import json
from pathlib import Path

from team_llm_wiki.wiki_ingest.migration import plan_route_migration, run_route_migration


def seed_deprecated_page(root: Path) -> None:
    wiki = root / "wiki"
    (wiki / "datasets").mkdir(parents=True)
    (wiki / "preprocessing").mkdir(parents=True)
    (wiki / "index.md").write_text(
        "- [Sleep Lifelog](datasets/sleep-lifelog-2024.md)\n",
        encoding="utf-8",
    )
    (wiki / "datasets" / "sleep-lifelog-2024.md").write_text(
        "---\nclaim_status: tentative\n---\n# Sleep Lifelog 2024\n\n## Split Policy\n\n- GroupKFold by subject.\n",
        encoding="utf-8",
    )


def test_plan_route_migration_is_dry_run(tmp_path):
    seed_deprecated_page(tmp_path)
    report_path = tmp_path / "raw" / "results" / "wiki-renovation" / "dry" / "report.json"

    report = plan_route_migration(tmp_path, run_id="dry", report_path=report_path)

    assert report["status"] == "planned"
    assert "wiki/datasets/sleep-lifelog-2024.md" in report["inventory"]
    assert report["planned_moves"][0]["source"] == "wiki/datasets/sleep-lifelog-2024.md"
    assert report_path.exists()
    assert (tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md").read_text(encoding="utf-8").startswith("---")


def test_run_route_migration_moves_page_leaves_tombstone_and_rewrites_links(tmp_path):
    seed_deprecated_page(tmp_path)
    report_path = tmp_path / "raw" / "results" / "wiki-renovation" / "run" / "report.json"

    report = run_route_migration(tmp_path, run_id="run", report_path=report_path, migration_mode=True)

    assert report["status"] == "migrated"
    assert (tmp_path / "wiki" / "preprocessing" / "sleep-lifelog-2024.md").exists()
    tombstone = (tmp_path / "wiki" / "datasets" / "sleep-lifelog-2024.md").read_text(encoding="utf-8")
    assert "page_role: compatibility" in tombstone
    assert "canonical_target: wiki/preprocessing/sleep-lifelog-2024.md" in tombstone
    assert "preprocessing/sleep-lifelog-2024.md" in (tmp_path / "wiki" / "index.md").read_text(encoding="utf-8")
    assert json.loads(report_path.read_text(encoding="utf-8"))["status"] == "migrated"


def test_run_route_migration_requires_explicit_migration_mode(tmp_path):
    seed_deprecated_page(tmp_path)

    report = run_route_migration(tmp_path, run_id="blocked", migration_mode=False)

    assert report["status"] == "blocked"
    assert any(error["code"] == "migration_mode_required" for error in report["errors"])
```

- [ ] **Step 2: Add CLI e2e tests**

Append to `/home/chunoh/ETRI/team_llm_wiki/tests/e2e/test_cli.py`:

```python
def test_cli_plan_wiki_route_migration_writes_report(tmp_path):
    seed_repo(tmp_path)
    report_path = tmp_path / "raw" / "results" / "wiki-renovation" / "cli" / "report.json"

    result = run_cli(
        [
            "plan-wiki-route-migration",
            "--repo-root",
            str(tmp_path),
            "--run-id",
            "cli",
            "--report-path",
            str(report_path),
        ],
        cwd=Path.cwd(),
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] in {"planned", "clean"}
    assert report_path.exists()


def test_cli_run_wiki_route_migration_requires_flag(tmp_path):
    seed_repo(tmp_path)

    result = run_cli(
        ["run-wiki-route-migration", "--repo-root", str(tmp_path), "--run-id", "blocked"],
        cwd=Path.cwd(),
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
```

- [ ] **Step 3: Run migration tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_migration.py tests/e2e/test_cli.py::test_cli_plan_wiki_route_migration_writes_report tests/e2e/test_cli.py::test_cli_run_wiki_route_migration_requires_flag -q
```

Expected: failures for missing `migration.py` and missing CLI commands.

- [ ] **Step 4: Implement `migration.py`**

Create `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/migration.py` with:

```python
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .links import lint_wiki_links
from .route_contract import load_route_contract


def plan_route_migration(repo_root: Path, *, run_id: str, report_path: Path | None = None) -> dict[str, Any]:
    contract = load_route_contract(repo_root)
    report = _build_report(repo_root, contract, run_id=run_id)
    report["status"] = "clean" if not report["inventory"] else "planned"
    _write_report(repo_root, report, report_path)
    return report


def run_route_migration(
    repo_root: Path,
    *,
    run_id: str,
    report_path: Path | None = None,
    migration_mode: bool = False,
) -> dict[str, Any]:
    contract = load_route_contract(repo_root)
    if not migration_mode:
        report = _build_report(repo_root, contract, run_id=run_id)
        report["status"] = "blocked"
        report["errors"].append({"code": "migration_mode_required", "message": "run-wiki-route-migration requires explicit migration mode"})
        _write_report(repo_root, report, report_path)
        return report

    report = _build_report(repo_root, contract, run_id=run_id)
    for item in report["planned_moves"]:
        source = repo_root / item["source"]
        target = repo_root / item["target"]
        if not source.exists():
            report["errors"].append({"code": "migration_source_missing", "path": item["source"]})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            _append_migrated_notes(target, source)
            source.write_text(_tombstone(item["target"]), encoding="utf-8")
            report["merged"].append(item)
        else:
            shutil.copy2(source, target)
            source.write_text(_tombstone(item["target"]), encoding="utf-8")
            report["moved"].append(item)
    report["link_rewrites"] = _rewrite_links(repo_root, contract.migration_map)
    report["broken_links"] = [error.__dict__ for error in lint_wiki_links(repo_root)]
    report["status"] = "failed" if report["errors"] or report["broken_links"] else "migrated"
    _write_report(repo_root, report, report_path)
    return report
```

Add helpers in the same file:

```python
def _build_report(repo_root: Path, contract, *, run_id: str) -> dict[str, Any]:
    inventory: list[str] = []
    wiki_root = repo_root / "wiki"
    if wiki_root.exists():
        for path in sorted(wiki_root.rglob("*.md")):
            rel = path.relative_to(repo_root).as_posix()
            if contract.deprecated_namespace_for_path(rel):
                inventory.append(rel)
    planned_moves = [
        {"source": source, "target": target}
        for source, target in sorted(contract.migration_map.items())
        if (repo_root / source).exists()
    ]
    classified = {move["source"] for move in planned_moves}
    generated = [path for path in inventory if contract.is_generated_compatibility_path(path)]
    deferred = [
        {"path": path, "reason": "no migration_map entry yet"}
        for path in inventory
        if path not in classified and path not in generated
    ]
    errors = []
    if deferred:
        errors.append({"code": "migration_inventory_incomplete", "paths": [item["path"] for item in deferred]})
    return {
        "run_id": run_id,
        "status": "planned",
        "contract_version": contract.version,
        "contract_path": contract.source_path,
        "inventory": inventory,
        "planned_moves": planned_moves,
        "moved": [],
        "merged": [],
        "generated_compatibility": generated,
        "deferred_with_reason": deferred,
        "link_rewrites": [],
        "broken_links": [],
        "errors": errors,
    }


def _append_migrated_notes(target: Path, source: Path) -> None:
    source_text = source.read_text(encoding="utf-8").strip()
    target_text = target.read_text(encoding="utf-8").rstrip()
    if source_text and source_text not in target_text:
        target.write_text(target_text + "\n\n## Migrated Notes\n\n" + source_text + "\n", encoding="utf-8")


def _tombstone(canonical_target: str) -> str:
    wiki_link = canonical_target.removeprefix("wiki/").removesuffix(".md")
    return (
        "---\n"
        "page_role: compatibility\n"
        "status: deprecated\n"
        f"canonical_target: {canonical_target}\n"
        "---\n"
        "# Deprecated Compatibility Page\n\n"
        f"This page has moved to [[{wiki_link}]].\n\n"
        "Do not add new substantive content here. This file exists to preserve historical links and provenance.\n"
    )


def _rewrite_links(repo_root: Path, migration_map: dict[str, str]) -> list[dict[str, str]]:
    rewrites: list[dict[str, str]] = []
    wiki_root = repo_root / "wiki"
    if not wiki_root.exists():
        return rewrites
    replacements = _link_replacements(migration_map)
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(repo_root).as_posix()
        if rel == "wiki/log.md":
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            rewrites.append({"path": rel, "status": "rewritten"})
    return rewrites


def _link_replacements(migration_map: dict[str, str]) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for old, new in migration_map.items():
        old_rel = old.removeprefix("wiki/")
        new_rel = new.removeprefix("wiki/")
        replacements[f"]({old_rel})"] = f"]({new_rel})"
        replacements[f"]({old})"] = f"]({new})"
        replacements[f"[[{old_rel.removesuffix('.md')}]]"] = f"[[{new_rel.removesuffix('.md')}]]"
        replacements[f"[[{old.removesuffix('.md')}]]"] = f"[[{new.removesuffix('.md')}]]"
    return replacements


def _write_report(repo_root: Path, report: dict[str, Any], report_path: Path | None) -> None:
    if report_path is None:
        return
    target = report_path if report_path.is_absolute() else repo_root / report_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
```

- [ ] **Step 5: Wire CLI commands**

In `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/cli.py`, import:

```python
from .wiki_ingest.migration import plan_route_migration, run_route_migration
```

Add parsers:

```python
migration_plan = sub.add_parser("plan-wiki-route-migration")
migration_plan.add_argument("--repo-root", required=True)
migration_plan.add_argument("--run-id", default="route-migration-plan")
migration_plan.add_argument("--report-path")

migration_run = sub.add_parser("run-wiki-route-migration")
migration_run.add_argument("--repo-root", required=True)
migration_run.add_argument("--run-id", default="route-migration-run")
migration_run.add_argument("--report-path")
migration_run.add_argument("--migration-mode", action="store_true")
```

Add handlers:

```python
if args.command == "plan-wiki-route-migration":
    report = plan_route_migration(
        Path(args.repo_root),
        run_id=args.run_id,
        report_path=Path(args.report_path) if args.report_path else None,
    )
    _print_json(report, sys.stdout)
    return 1 if report.get("status") == "failed" else 0
if args.command == "run-wiki-route-migration":
    report = run_route_migration(
        Path(args.repo_root),
        run_id=args.run_id,
        report_path=Path(args.report_path) if args.report_path else None,
        migration_mode=args.migration_mode,
    )
    _print_json(report, sys.stdout)
    return 0 if report.get("status") == "migrated" else 1
```

- [ ] **Step 6: Run migration tests**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_migration.py tests/e2e/test_cli.py -q
```

Expected: all selected tests pass.

- [ ] **Step 7: Commit Task 4**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add src/team_llm_wiki/wiki_ingest/migration.py src/team_llm_wiki/cli.py tests/wiki_ingest/test_migration.py tests/e2e/test_cli.py
git commit -m "Add route migration planning and execution CLI" \
  -m "Constraint: physical wiki migration must be reviewable before mutation." \
  -m "Rejected: manual git mv migration | reviewers cannot reliably audit inventory and link rewrites by eye." \
  -m "Confidence: high" \
  -m "Scope-risk: broad" \
  -m "Directive: run plan-wiki-route-migration before run-wiki-route-migration in PR2." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_migration.py tests/e2e/test_cli.py -q" \
  -m "Not-tested: real repository migration deferred to PR2"
```

## Task 5: Constrain LLM Synthesis To Canonical Wiki Paths

**Files:**

- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/llm_synthesis.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_llm_synthesis.py`

- [ ] **Step 1: Add tests for canonical LLM paths**

In `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_llm_synthesis.py`, replace the current LLM synthesis import block with:

```python
from team_llm_wiki.wiki_ingest.llm_synthesis import OpenAIResponsesClient
from team_llm_wiki.wiki_ingest.llm_synthesis import _integration_paths
from team_llm_wiki.wiki_ingest.llm_synthesis import _validate_generated_pages_against_contract
from team_llm_wiki.wiki_ingest.llm_synthesis import run_llm_wiki_synthesis
```

In `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_llm_synthesis.py`, update existing old-path assertions and add:

```python
def test_llm_synthesis_integration_paths_are_canonical():
    paths = _integration_paths([])

    assert "wiki/claims/current-supported-claims.md" in paths
    assert "wiki/performance/dacon-leaderboard-history.md" in paths
    assert "wiki/preprocessing/canonical-split-and-leakage-policy.md" in paths
    assert all(not path.startswith("wiki/questions/") for path in paths)
    assert all(not path.startswith("wiki/submissions/") for path in paths)
    assert all(not path.startswith("wiki/datasets/") for path in paths)
    assert all(not path.startswith("wiki/benchmarks/") for path in paths)


def test_llm_synthesis_rejects_deprecated_output_path(tmp_path):
    page = {"path": "wiki/questions/sleep-lifelog-open-questions.md", "content": "# Old Questions\n"}

    errors = _validate_generated_pages_against_contract(tmp_path, [page])

    assert any(error["code"] == "deprecated_synthesis_path" for error in errors)
```

- [ ] **Step 2: Run LLM synthesis tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_llm_synthesis.py -q
```

Expected: failures showing old `wiki/questions` and `wiki/submissions` paths.

- [ ] **Step 3: Update integration paths and output validation**

In `llm_synthesis.py`, change `_integration_paths()` to return:

```python
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
```

Add:

```python
def _validate_generated_pages_against_contract(repo_root: Path, pages: list[dict[str, object]]) -> list[dict[str, object]]:
    contract = load_route_contract(repo_root)
    errors: list[dict[str, object]] = []
    for page in pages:
        path = str(page.get("path", ""))
        if path in {"wiki/index.md", "wiki/log.md", "wiki/latest-context.md", "wiki/overview.md"}:
            continue
        if not contract.is_allowed_synthesis_path(path):
            code = "deprecated_synthesis_path" if contract.deprecated_namespace_for_path(path) else "invalid_synthesis_path"
            errors.append({"code": code, "path": path, "message": "LLM synthesis output path is not canonical"})
    return errors
```

Call this helper immediately after parsing LLM output and before writing to the staging directory. If errors are returned, produce a hard-fail synthesis report and do not copy generated pages.

- [ ] **Step 4: Update prompt policy text**

In the prompt construction section of `llm_synthesis.py`, replace old namespace instructions with:

```text
- Use only canonical wiki namespaces for durable pages: preprocessing, features, models, performance, claims, targets, decisions, reports, team.
- Do not create wiki/datasets, wiki/benchmarks, wiki/submissions, wiki/questions, wiki/experiments, or wiki/sources pages.
- Put open questions into wiki/targets/* or wiki/reports/* with close conditions.
- Put leaderboard and metric history into wiki/performance/*.
- Put dataset, split, leakage, and fit-scope policy into wiki/preprocessing/*.
```

- [ ] **Step 5: Run LLM synthesis tests**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_llm_synthesis.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit Task 5**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add src/team_llm_wiki/wiki_ingest/llm_synthesis.py tests/wiki_ingest/test_llm_synthesis.py
git commit -m "Constrain LLM synthesis to canonical wiki paths" \
  -m "Constraint: GPT-5.5 output remains review-required but must fail before writing deprecated paths." \
  -m "Rejected: prompt-only policy | parser validation must catch model drift." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: any new synthesis page namespace must be added to the route contract first." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_llm_synthesis.py -q" \
  -m "Not-tested: real GPT-5.5 smoke deferred to PR2"
```

## Task 6: Add Workflow Migration-Mode Gates

**Files:**

- Modify: `/home/chunoh/ETRI/team_llm_wiki/.github/workflows/wiki-pr-validate.yml`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/.github/workflows/wiki-main-ingest.yml`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/.github/workflows/wiki-llm-synthesis.yml`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/.github/workflows/wiki-health-check.yml`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_workflows.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_github_actions.py`

- [ ] **Step 1: Add workflow tests**

Append to `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_workflows.py`:

```python
def test_normal_workflows_do_not_enable_migration_mode():
    for rel in [
        ".github/workflows/wiki-pr-validate.yml",
        ".github/workflows/wiki-main-ingest.yml",
        ".github/workflows/wiki-llm-synthesis.yml",
        ".github/workflows/wiki-health-check.yml",
    ]:
        workflow = Path(rel).read_text(encoding="utf-8")
        assert "WIKI_MIGRATION_MODE: 1" not in workflow
        assert "WIKI_MIGRATION_MODE=1" not in workflow


def test_main_ingest_migration_dispatch_is_branch_gated():
    workflow = Path(".github/workflows/wiki-main-ingest.yml").read_text(encoding="utf-8")

    assert "migration_mode:" in workflow
    assert "migration/wiki-" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "--migration-mode" in workflow


def test_llm_synthesis_migration_dispatch_is_branch_gated():
    workflow = Path(".github/workflows/wiki-llm-synthesis.yml").read_text(encoding="utf-8")

    assert "migration_mode:" in workflow
    assert "migration/wiki-" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
```

- [ ] **Step 2: Run workflow tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_workflows.py -q
```

Expected: failures because workflows do not expose migration dispatch inputs yet.

- [ ] **Step 3: Update workflow dispatch inputs**

In `wiki-main-ingest.yml` and `wiki-llm-synthesis.yml`, add:

```yaml
      migration_mode:
        description: "Allow migration-only deprecated namespace handling. Requires migration/wiki-* branch."
        required: false
        type: boolean
        default: false
```

Add an environment variable to run steps:

```yaml
          WIKI_MIGRATION_MODE: ${{ github.event_name == 'workflow_dispatch' && inputs.migration_mode && startsWith(github.ref_name, 'migration/wiki-') && '1' || '0' }}
```

When invoking CLI commands that support migration mode, include:

```bash
if [ "$WIKI_MIGRATION_MODE" = "1" ]; then
  migration_args="--migration-mode"
else
  migration_args=""
fi
```

Then pass `$migration_args` only to migration-aware commands.

- [ ] **Step 4: Ensure PR validate reports but does not enable migration**

In `wiki-pr-validate.yml`, do not add any `WIKI_MIGRATION_MODE=1`. The preview command should stay normal and hard-fail deprecated packet outputs.

- [ ] **Step 5: Run workflow tests**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_workflows.py tests/wiki_ingest/test_github_actions.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit Task 6**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add .github/workflows/wiki-pr-validate.yml .github/workflows/wiki-main-ingest.yml .github/workflows/wiki-llm-synthesis.yml .github/workflows/wiki-health-check.yml tests/wiki_ingest/test_workflows.py tests/wiki_ingest/test_github_actions.py
git commit -m "Gate wiki migration mode in Actions" \
  -m "Constraint: migration mode must never turn on during normal packet PRs or bot PRs." \
  -m "Rejected: environment-only switch | manual dispatch and branch gating are both needed." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: migration workflow runs must use migration/wiki-* branches." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_workflows.py tests/wiki_ingest/test_github_actions.py -q" \
  -m "Not-tested: live GitHub Actions dispatch deferred to PR validation"
```

## Task 7: Update Packet Skill Contract And Routes

**Files:**

- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/wiki-route-contract.v1.yaml`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/packet_skill_common.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/verify_install.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_common.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_install_local.py`

- [ ] **Step 1: Copy the route contract into packet skill**

Run:

```bash
cp /home/chunoh/ETRI/team_llm_wiki/automation/contracts/wiki-route-contract.v1.yaml \
  /home/chunoh/ETRI/team-llm-wiki-packet-skill/references/wiki-route-contract.v1.yaml
```

Then verify:

```bash
cmp /home/chunoh/ETRI/team_llm_wiki/automation/contracts/wiki-route-contract.v1.yaml \
  /home/chunoh/ETRI/team-llm-wiki-packet-skill/references/wiki-route-contract.v1.yaml
```

Expected: no output.

- [ ] **Step 2: Add packet skill tests**

In `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_common.py`, update route assertions to:

```python
def test_packet_routes_follow_wiki_route_contract(self):
    self.assertEqual(packet_route("dataset"), "wiki/preprocessing")
    self.assertEqual(packet_route("benchmark"), "wiki/performance")
    self.assertEqual(packet_route("experiment"), "wiki/reports")
    self.assertEqual(packet_route("reference"), "wiki/reports")
    self.assertEqual(ROUTES["dataset"], "wiki/preprocessing")
    self.assertEqual(ROUTES["benchmark"], "wiki/performance")
```

Add:

```python
def test_route_contract_is_loadable(self):
    contract = load_route_contract(importable_repo_root())
    self.assertEqual(contract["version"], 1)
    self.assertEqual(contract["packet_routes"]["dataset"], "wiki/preprocessing")
```

In `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_install_local.py`, assert `references/wiki-route-contract.v1.yaml` is copied and verified.

- [ ] **Step 3: Run packet skill tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_common tests.test_install_local -q
```

Expected: failures because `load_route_contract` does not exist in `packet_skill_common.py` and old route constants still point to deprecated namespaces.

- [ ] **Step 4: Implement packet skill contract loading**

In `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/packet_skill_common.py`, replace the hardcoded `ROUTES` body with contract-backed loading:

```python
def load_route_contract(skill_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(skill_root) if skill_root is not None else importable_repo_root()
    path = root / "references" / "wiki-route-contract.v1.yaml"
    if not path.exists():
        raise Failure(f"missing wiki route contract: {path}", code="missing_route_contract")
    try:
        data = _read_simple_yaml(path)
    except OSError as exc:
        raise Failure(f"could not read wiki route contract: {exc}", code="invalid_route_contract") from exc
    if data.get("version") != 1:
        raise Failure("unsupported wiki route contract version", code="invalid_route_contract")
    packet_routes = data.get("packet_routes", {})
    missing = sorted(PACKET_TYPES - set(packet_routes))
    if missing:
        raise Failure(f"route contract missing packet routes: {', '.join(missing)}", code="invalid_route_contract")
    return data
```

Add a simple YAML reader using PyYAML if available, falling back to the existing minimal renderer only for tests:

```python
def _read_simple_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise Failure("PyYAML is required to read the wiki route contract", code="missing_dependency") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise Failure("wiki route contract must be a mapping", code="invalid_route_contract")
    return data
```

Set:

```python
ROUTES = load_route_contract(importable_repo_root())["packet_routes"]
```

Keep `packet_route(packet_type: str)` unchanged except that it now reads the contract-backed `ROUTES`.

- [ ] **Step 5: Update `verify_install.py` required files**

Add `"references/wiki-route-contract.v1.yaml"` to `REQUIRED_RUNTIME_FILES`.

In `verify_install()`, after missing-file checks:

```python
from scripts.packet_skill_common import load_route_contract

contract = load_route_contract(root)
if contract["packet_routes"]["dataset"] != "wiki/preprocessing":
    raise Failure("installed route contract does not use canonical dataset route", code="invalid_route_contract")
```

Use the local import fallback pattern already present in this script if direct `scripts.*` import fails.

- [ ] **Step 6: Run packet skill common and install tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_common tests.test_install_local -q
python scripts/verify_install.py --skill-root .
```

Expected: tests pass and verify_install emits JSON with `"ok": true`.

- [ ] **Step 7: Commit Task 7 in packet skill repo**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add references/wiki-route-contract.v1.yaml scripts/packet_skill_common.py scripts/verify_install.py tests/test_common.py tests/test_install_local.py
git commit -m "Align packet skill routes with wiki contract" \
  -m "Constraint: packet skill output must match team_llm_wiki canonical routes." \
  -m "Rejected: maintain a separate skill route dictionary | it already drifted from repo policy." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: update references/wiki-route-contract.v1.yaml from the wiki repo for every route change." \
  -m "Tested: python -m unittest tests.test_common tests.test_install_local -q; python scripts/verify_install.py --skill-root ." \
  -m "Not-tested: full packet skill suite deferred to Task 8"
```

## Task 8: Update Packet Skill Graph, Draft, Preview, Render, And Docs

**Files:**

- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/merge_packet_graph.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/make_packet_draft.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/preview_packet.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/render_packet.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_merge_packet_graph.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_make_packet_draft.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_preview_packet.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_render_packet.py`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/README.md`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/SKILL.md`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/wiki-policy-alignment.md`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/ml-ai-hackathon-entity-rules.md`
- Modify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/etri-dacon-sleep-health-context.md`

- [ ] **Step 1: Update graph tests to canonical pages**

In `tests/test_merge_packet_graph.py`, change expected proposed pages:

```python
self.assertEqual(preprocessing_node["proposed_page"], "wiki/preprocessing/subject-hole-cv.md")
self.assertEqual(claim_node["proposed_page"], "wiki/performance/dacon-public-lb-07000.md")
```

In `tests/test_make_packet_draft.py`, change dataset and benchmark route expectations:

```python
self.assertEqual(draft["route"], "wiki/preprocessing")
self.assertEqual(draft["intended_wiki_targets"], ["wiki/preprocessing/2026-05-29-sleep-lifelog-2024.md"])
self.assertEqual(benchmark_draft["route"], "wiki/performance")
self.assertEqual(benchmark_draft["intended_wiki_targets"], ["wiki/performance/2026-05-29-sleep-health-hackathon-v0.md"])
```

In `tests/test_render_packet.py`, replace `wiki/sources`, `wiki/datasets`, and `wiki/benchmarks` expectations for newly rendered output with `wiki/reports`, `wiki/preprocessing`, and `wiki/performance`.

- [ ] **Step 2: Run packet skill targeted tests and verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_merge_packet_graph tests.test_make_packet_draft tests.test_preview_packet tests.test_render_packet -q
```

Expected: failures showing old proposed pages and old routes.

- [ ] **Step 3: Update graph proposed pages**

In `scripts/merge_packet_graph.py`, change:

```python
"proposed_page": "wiki/datasets/subject-hole-cv.md",
```

to:

```python
"proposed_page": "wiki/preprocessing/subject-hole-cv.md",
```

Change:

```python
"proposed_page": f"wiki/benchmarks/{claim.page_slug}.md",
```

to:

```python
"proposed_page": f"wiki/performance/{claim.page_slug}.md",
```

For external code-share packet synthesis reports, use:

```python
"proposed_page": f"wiki/reports/{claim.page_slug}.md",
```

only when the node is a packet review/report rather than the durable metric claim.

- [ ] **Step 4: Update draft, preview, and render scripts**

In `make_packet_draft.py`, ensure `route = packet_route(packet_type)` comes from contract-backed `packet_skill_common.py`. Do not hardcode route dictionaries in this file.

In `preview_packet.py`, add a canonical route section:

```text
Canonical wiki targets
- route: wiki/performance
- intended_wiki_targets: wiki/performance/<packet-id>.md
```

In `render_packet.py`, preserve `draft["route"]` and `draft["intended_wiki_targets"]` exactly as created by `make_packet_draft.py`; do not infer old routes during render.

- [ ] **Step 5: Update packet skill documentation**

Update these docs so they list only canonical human-facing namespaces:

```text
wiki/preprocessing
wiki/features
wiki/models
wiki/performance
wiki/claims
wiki/targets
wiki/decisions
wiki/reports
wiki/team
```

Remove guidance that points new durable output to `wiki/datasets`, `wiki/benchmarks`, `wiki/questions`, `wiki/submissions`, `wiki/experiments`, or `wiki/sources`.

- [ ] **Step 6: Run full packet skill test suite and install verification**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest discover -s tests -q
./install.sh --verify
git diff --check
```

Expected: `OK`, install verification succeeds, diff check is clean.

- [ ] **Step 7: Commit Task 8 in packet skill repo**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add scripts/merge_packet_graph.py scripts/make_packet_draft.py scripts/preview_packet.py scripts/render_packet.py tests README.md SKILL.md references
git commit -m "Generate canonical wiki packet targets" \
  -m "Constraint: team members should submit raw packets without learning deprecated wiki routes." \
  -m "Rejected: keep graph proposals under old namespaces | synthesis would keep recreating migrated pages." \
  -m "Confidence: high" \
  -m "Scope-risk: moderate" \
  -m "Directive: packet skill previews must show canonical wiki targets before upload." \
  -m "Tested: python -m unittest discover -s tests -q; ./install.sh --verify; git diff --check" \
  -m "Not-tested: live GitHub PR upload"
```

## Task 9: Add Cross-Repo Contract Parity In Wiki Repo

**Files:**

- Modify: `/home/chunoh/ETRI/team_llm_wiki/src/team_llm_wiki/wiki_ingest/packet_skill_compatibility.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_packet_skill_compatibility.py`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/tests/wiki_ingest/test_packaging.py`

- [ ] **Step 1: Add parity tests**

In `tests/wiki_ingest/test_packet_skill_compatibility.py`, add:

```python
def test_packet_skill_contract_parity_with_source_repo():
    source_contract = Path("automation/contracts/wiki-route-contract.v1.yaml").read_text(encoding="utf-8")
    skill_contract = Path("/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/wiki-route-contract.v1.yaml").read_text(encoding="utf-8")

    assert skill_contract == source_contract
```

Add a packet compatibility test that expects canonical `wiki_plan.yaml` pages:

```python
def test_packet_skill_compatibility_warns_on_deprecated_wiki_plan_path(tmp_path):
    packet_root = write_packet(
        tmp_path,
        tmp_path / "raw" / "users" / "alice" / "performance" / "2026-06-12-old-route",
        metrics_to_verify=[{"raw_path": "result.json", "metric_key": "logloss", "reported_value": 0.42}],
        wiki_plan={
            "stable_entities": [
                {"id": "question:old", "page": "wiki/questions/old-open-questions.md", "page_role": "hub"}
            ],
            "affected_pages": [{"path": "wiki/questions/old-open-questions.md", "role": "hub"}],
            "semantic_lint": ["Old route should be rejected."],
        },
    )
    manifest = load_packet_manifest(packet_root)

    result = evaluate_packet_skill_compatibility(
        tmp_path,
        changed_paths=[str(packet_root.relative_to(tmp_path) / "manifest.yaml")],
        packet_roots=[packet_root],
        manifests_by_root={packet_root: manifest},
    )

    entity_check = next(check for check in result["checks"] if check["id"] == "entity_coverage")
    assert entity_check["status"] == "warning"
    assert any("not an allowed synthesis wiki path" in warning for warning in entity_check["warnings"])
```

- [ ] **Step 2: Run compatibility tests and verify failures if parity is absent**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_packet_skill_compatibility.py -q
```

Expected: passes if Task 7 and 8 are complete; otherwise fails on parity or old route warnings.

- [ ] **Step 3: Update compatibility code to pass repo root and migration mode**

In `packet_skill_compatibility.py`, change:

```python
plan = load_wiki_plan(packet_root)
```

to:

```python
plan = load_wiki_plan(packet_root, repo_root=repo_root)
```

Ensure `proposed_pages` in compatibility output lists canonical paths and warnings for deprecated paths.

- [ ] **Step 4: Run compatibility tests**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_packet_skill_compatibility.py tests/wiki_ingest/test_packaging.py -q
```

Expected: selected tests pass.

- [ ] **Step 5: Commit Task 9**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add src/team_llm_wiki/wiki_ingest/packet_skill_compatibility.py tests/wiki_ingest/test_packet_skill_compatibility.py tests/wiki_ingest/test_packaging.py
git commit -m "Verify packet skill route contract parity" \
  -m "Constraint: source wiki repo and packet skill repo must agree before team distribution." \
  -m "Rejected: rely on docs to keep repos aligned | tests should catch drift." \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Directive: update both contract copies in the same change wave." \
  -m "Tested: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_packet_skill_compatibility.py tests/wiki_ingest/test_packaging.py -q" \
  -m "Not-tested: live installed skill in ~/.codex/skills"
```

## Task 10: Update Wiki Repo Docs And Policy Text

**Files:**

- Modify: `/home/chunoh/ETRI/team_llm_wiki/README.md`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/AGENTS.md`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/CLAUDE.md`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/wiki/team/page-taxonomy.md`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/wiki/team/llm-wiki-operating-harness.md`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/wiki/team/wiki-ingest-policy.md`
- Modify: `/home/chunoh/ETRI/team_llm_wiki/wiki/team/contribution-workflow.md`

- [ ] **Step 1: Search old namespace guidance**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
rg -n "wiki/datasets|wiki/benchmarks|wiki/questions|wiki/submissions|wiki/experiments|wiki/sources|wiki/briefs" README.md AGENTS.md CLAUDE.md wiki/team
```

Expected: matches exist and should be updated to canonical policy or deprecated compatibility notes.

- [ ] **Step 2: Update README canonical structure section**

Add this concise structure block near the top of `README.md`:

````markdown
## Canonical wiki structure

Durable wiki pages live in these namespaces:

```text
wiki/preprocessing
wiki/features
wiki/models
wiki/performance
wiki/claims
wiki/targets
wiki/decisions
wiki/reports
wiki/team
```

Deprecated namespaces such as `wiki/datasets`, `wiki/benchmarks`, `wiki/questions`, `wiki/submissions`, `wiki/experiments`, and `wiki/sources` are compatibility-only. New packet PRs and bot outputs must not create substantive pages there.
````

- [ ] **Step 3: Update AGENTS and CLAUDE query/ingest loop wording**

Replace old sentence:

```markdown
If the answer creates durable value, crystallize it back into `wiki/reports/`, `wiki/questions/`, `wiki/decisions/`, or the relevant leaf entity page.
```

with:

```markdown
If the answer creates durable value, crystallize it back into `wiki/reports/`, `wiki/targets/`, `wiki/claims/`, `wiki/decisions/`, or the relevant canonical leaf entity page.
```

Replace old dataset/benchmark guidance with:

```markdown
Dataset, split, leakage, and fit-scope policy belongs under `wiki/preprocessing/`. Metric, evaluation, leaderboard, and submission history belongs under `wiki/performance/`.
```

- [ ] **Step 4: Update wiki/team policy pages**

Ensure each policy page names the route contract:

```markdown
Route policy source of truth: `automation/contracts/wiki-route-contract.v1.yaml`.

Automation must read the contract through `src/team_llm_wiki/wiki_ingest/route_contract.py`; packet skill must vendor the same contract under `references/wiki-route-contract.v1.yaml`.
```

- [ ] **Step 5: Verify docs have no new-route guidance in deprecated namespaces**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
rg -n "create .*wiki/(datasets|benchmarks|questions|submissions|experiments|sources)|new .*wiki/(datasets|benchmarks|questions|submissions|experiments|sources)" README.md AGENTS.md CLAUDE.md wiki/team
```

Expected: no output.

- [ ] **Step 6: Commit Task 10**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add README.md AGENTS.md CLAUDE.md wiki/team/page-taxonomy.md wiki/team/llm-wiki-operating-harness.md wiki/team/wiki-ingest-policy.md wiki/team/contribution-workflow.md
git commit -m "Document canonical wiki route policy" \
  -m "Constraint: teammates need one simple human-facing wiki structure." \
  -m "Rejected: keep docs describing old namespaces as normal targets | that conflicts with automation." \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Directive: docs must describe deprecated namespaces as compatibility-only." \
  -m "Tested: rg checks for deprecated namespace creation guidance" \
  -m "Not-tested: full docs link audit deferred to PR checkpoint"
```

## Task 11: PR1 Full Verification

**Files:**

- No new source files.
- Verify both repos.

- [ ] **Step 1: Run full wiki repo tests**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run wiki health**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
```

Expected: `ok` is `true`. Existing deprecated pages may only appear as allowed warning/inventory behavior before PR2.

- [ ] **Step 3: Run packet skill tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest discover -s tests -q
./install.sh --verify
```

Expected: unittest `OK` and install verification succeeds.

- [ ] **Step 4: Run cross-repo contract parity**

Run:

```bash
cmp /home/chunoh/ETRI/team_llm_wiki/automation/contracts/wiki-route-contract.v1.yaml \
  /home/chunoh/ETRI/team-llm-wiki-packet-skill/references/wiki-route-contract.v1.yaml
```

Expected: no output.

- [ ] **Step 5: Run diff checks**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git diff --check
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git diff --check
```

Expected: no output.

- [ ] **Step 6: Open PR1s**

Open a `team_llm_wiki` PR and a `team-llm-wiki-packet-skill` PR. The PR bodies must include:

````markdown
## Summary

- Added canonical wiki route contract.
- Wired ingest, synthesis, health, workflow checks, and packet skill output to the same route policy.
- Kept physical wiki content migration out of PR1.

## Rollback

Revert this PR, then run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
```

For packet skill:

```bash
python -m unittest discover -s tests -q
./install.sh --verify
```

## Verification

- Full wiki repo tests:
- Wiki health:
- Packet skill tests:
- Install verification:
- Contract parity:
````

Do not start Task 12 until PR1 is merged in both repos.

## Task 12: PR2 Dry-Run Migration

**Files:**

- Generated report: `/home/chunoh/ETRI/team_llm_wiki/raw/results/wiki-renovation/<run-id>/report.json`
- No intended wiki mutation in dry-run step.

- [ ] **Step 1: Create migration branch**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git checkout -b migration/wiki-policy-structure-renovation-20260612
```

Expected: new branch checked out.

- [ ] **Step 2: Run dry-run migration**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONPATH=src python -m team_llm_wiki.cli plan-wiki-route-migration \
  --repo-root . \
  --run-id 20260612-dry-run \
  --report-path raw/results/wiki-renovation/20260612-dry-run/report.json
```

Expected: JSON status `planned` or `clean`. If status is `failed`, fix migration map coverage in the route contract before proceeding.

- [ ] **Step 3: Inspect report classifications**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
python - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("raw/results/wiki-renovation/20260612-dry-run/report.json").read_text(encoding="utf-8"))
print("status", report["status"])
print("inventory", len(report["inventory"]))
print("planned_moves", len(report["planned_moves"]))
print("generated_compatibility", len(report["generated_compatibility"]))
print("deferred", len(report["deferred_with_reason"]))
print("errors", report["errors"])
PY
```

Expected: every deprecated file is classified as a planned move, generated compatibility, tombstone, or a specific deferred item. PR2 should not proceed with `migration_inventory_incomplete`.

- [ ] **Step 4: Commit dry-run report if useful for reviewer**

If the report contains reviewer-useful inventory, commit it:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add raw/results/wiki-renovation/20260612-dry-run/report.json
git commit -m "Record wiki route migration dry run" \
  -m "Constraint: PR2 reviewers need the deprecated namespace inventory before mutation." \
  -m "Rejected: review migration only from git diff | report classification is easier to audit." \
  -m "Confidence: high" \
  -m "Scope-risk: narrow" \
  -m "Directive: do not run mutation until dry-run inventory has no unclassified deprecated pages." \
  -m "Tested: PYTHONPATH=src python -m team_llm_wiki.cli plan-wiki-route-migration --repo-root . --run-id 20260612-dry-run --report-path raw/results/wiki-renovation/20260612-dry-run/report.json" \
  -m "Not-tested: mutation deferred to next task"
```

## Task 13: PR2 Run Migration And Verify Wiki Content

**Files:**

- Modify or create canonical pages under `/home/chunoh/ETRI/team_llm_wiki/wiki/preprocessing/`
- Modify or create canonical pages under `/home/chunoh/ETRI/team_llm_wiki/wiki/performance/`
- Modify or create canonical pages under `/home/chunoh/ETRI/team_llm_wiki/wiki/targets/`
- Modify or create canonical pages under `/home/chunoh/ETRI/team_llm_wiki/wiki/reports/`
- Modify tombstones under deprecated namespaces.
- Modify `wiki/index.md`, `wiki/latest-context.md`, and `wiki/log.md` if migration command or follow-up link fixes require it.

- [ ] **Step 1: Run migration mutation**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONPATH=src python -m team_llm_wiki.cli run-wiki-route-migration \
  --repo-root . \
  --run-id 20260612-run \
  --migration-mode \
  --report-path raw/results/wiki-renovation/20260612-run/report.json
```

Expected: JSON status `migrated`.

- [ ] **Step 2: Verify deprecated namespaces contain only tombstones or generated compatibility**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
python - <<'PY'
from pathlib import Path
for path in sorted(Path("wiki").glob("*/*.md")):
    rel = path.as_posix()
    if rel.startswith(("wiki/datasets/", "wiki/benchmarks/", "wiki/submissions/", "wiki/questions/", "wiki/experiments/", "wiki/sources/")):
        text = path.read_text(encoding="utf-8")
        if "page_role: compatibility" not in text or "status: deprecated" not in text:
            raise SystemExit(f"not a tombstone: {rel}")
print("deprecated namespaces are tombstones")
PY
```

Expected: `deprecated namespaces are tombstones`.

- [ ] **Step 3: Run strict health**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
```

Expected: `ok` is `true`.

- [ ] **Step 4: Inspect canonical destination pages**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
for path in \
  wiki/preprocessing/sleep-lifelog-2024.md \
  wiki/performance/sleep-health-hackathon-evaluation-policy.md \
  wiki/performance/dacon-leaderboard-history.md \
  wiki/targets/sleep-lifelog-open-issues.md \
  wiki/targets/section07-followup-backlog.md
do
  test -s "$path" || { echo "missing $path"; exit 1; }
done
```

Expected: no output.

- [ ] **Step 5: Run full test suite**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
git diff --check
```

Expected: all tests pass and diff check is clean.

- [ ] **Step 6: Commit PR2 migration**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
git add wiki raw/results/wiki-renovation/20260612-run/report.json
git commit -m "Migrate deprecated wiki namespaces to canonical pages" \
  -m "Constraint: team-facing wiki structure must match the canonical route contract." \
  -m "Rejected: leave old pages substantive indefinitely | team lead feedback requires a simpler wiki surface." \
  -m "Confidence: high" \
  -m "Scope-risk: broad" \
  -m "Directive: old namespace pages are compatibility tombstones only after this migration." \
  -m "Tested: PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .; PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q; git diff --check" \
  -m "Not-tested: live GPT-5.5 smoke deferred to final task"
```

## Task 14: Final DACON GPT-5.5 Smoke And PR2 Handoff

**Files:**

- Generated report: `/home/chunoh/ETRI/team_llm_wiki/raw/results/llm-synthesis/manual-dacon-smoke/report.json`
- Possible canonical wiki updates from smoke if accepted by reviewer.

- [ ] **Step 1: Choose DACON packet smoke input**

Use the existing DACON packet evidence:

```text
raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/manifest.yaml
```

- [ ] **Step 2: Run deterministic ingest preview on the smoke input**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
printf '%s\n' raw/users/dacon-community/performance/2026-06-12-dacon-public-05917-lgbm-xgb-anchor-graph-first-recheck/manifest.yaml > /tmp/dacon-smoke-changed-paths.txt
PYTHONPATH=src python -m team_llm_wiki.cli preview-wiki-ingest \
  --repo-root . \
  --changed-path-file /tmp/dacon-smoke-changed-paths.txt \
  --run-id manual-dacon-preview
```

Expected: generated paths are canonical only.

- [ ] **Step 3: Run real GPT-5.5 synthesis smoke**

Run only if `OPENAI_API_KEY` is present:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONPATH=src python -m team_llm_wiki.cli run-llm-wiki-synthesis \
  --repo-root . \
  --changed-path-file /tmp/dacon-smoke-changed-paths.txt \
  --run-id manual-dacon-smoke \
  --model gpt-5.5 \
  --reasoning-effort high \
  --max-output-tokens 60000 \
  --report-path raw/results/llm-synthesis/manual-dacon-smoke/report.json
```

Expected: no generated path starts with:

```text
wiki/questions/
wiki/submissions/
wiki/datasets/
wiki/benchmarks/
wiki/experiments/
wiki/sources/
```

- [ ] **Step 4: Verify generated path policy**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
python - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("raw/results/llm-synthesis/manual-dacon-smoke/report.json").read_text(encoding="utf-8"))
bad = [
    path for path in report.get("generated_paths", [])
    if path.startswith(("wiki/questions/", "wiki/submissions/", "wiki/datasets/", "wiki/benchmarks/", "wiki/experiments/", "wiki/sources/"))
]
if bad:
    raise SystemExit("deprecated generated paths: " + ", ".join(bad))
print("canonical synthesis paths only")
PY
```

Expected: `canonical synthesis paths only`.

- [ ] **Step 5: Final cross-repo verification**

Run:

```bash
cd /home/chunoh/ETRI/team_llm_wiki
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
git diff --check

cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest discover -s tests -q
./install.sh --verify
git diff --check

cmp /home/chunoh/ETRI/team_llm_wiki/automation/contracts/wiki-route-contract.v1.yaml \
  /home/chunoh/ETRI/team-llm-wiki-packet-skill/references/wiki-route-contract.v1.yaml
```

Expected: all commands pass.

- [ ] **Step 6: Open PR2**

PR2 body must include:

````markdown
## Summary

- Migrated deprecated wiki namespaces into canonical wiki pages.
- Left old paths as compatibility tombstones.
- Rewrote non-log wiki links.
- Verified DACON GPT-5.5 smoke creates canonical paths only.

## Rollback

Revert this PR only. Keep PR1 contract and validators.

After revert, run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
```

## Verification

- Migration dry-run report:
- Migration run report:
- Wiki health:
- Full pytest:
- Packet skill tests:
- Install verification:
- Contract parity:
- DACON GPT-5.5 smoke:
````

## Final Self-Review

- Spec coverage: every CEO and Eng review requirement maps to Tasks 1-14.
- Red-flag scan: avoid undefined future work inside implementation tasks; deferred work remains in the source design docs, not this execution path.
- Type consistency: `WikiRouteContract`, `NamespaceRoute`, `DeprecatedNamespace`, `load_route_contract()`, `plan_route_migration()`, and `run_route_migration()` are used consistently across tasks.
- Test coverage: route contract, repo consumers, health, migration CLI, LLM synthesis, workflows, packet skill, cross-repo parity, and DACON smoke are covered.
- Scope boundary: MCP/context reader, removal of `wiki/briefs`, semantic contradiction classifier, historical raw packet rewrites, and synthesis replay are outside this wave.
