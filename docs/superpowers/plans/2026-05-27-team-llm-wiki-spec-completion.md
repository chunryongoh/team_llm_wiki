# Team LLM Wiki Spec Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every known gap between the 2026-05-26 collaboration spec/eng-review plan and the standalone `team_llm_wiki` repository.

**Architecture:** Keep the current deterministic Python package and extend it in place. Add first-class manifest metadata, packet-specific validators, raw-only metric and split guards, compiled packet JSON, PR preview, broader wiki health checks, brief generation, and workflow hardening. Preserve the existing staged render/copy-back model so hard failures never mutate `wiki/`.

**Tech Stack:** Python 3.13, PyYAML, pytest, GitHub Actions, markdown files under `raw/` and `wiki/`.

---

## Source Requirements

Use these as authoritative requirement sources while implementing:

- `/home/chunoh/ETRI/docs/superpowers/specs/2026-05-26-team-llm-wiki-collaboration-design.md`
- `/home/chunoh/ETRI/docs/superpowers/plans/2026-05-26-team-llm-wiki-hybrid-main-ingest.md`
- `/home/chunoh/.gstack/projects/ETRI/chunoh-unknown-eng-review-test-plan-20260526-194337.md`
- Current drift audit in `/home/chunoh/ETRI/wiki/reports/2026-05-26-team-llm-wiki-collaboration-spec.md`

Current worktree:

- `/home/chunoh/ETRI/team_llm_wiki/.worktrees/spec-complete`
- Branch: `feature/spec-complete`

Baseline command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
```

Expected baseline before implementation: `67 passed`.

---

## File Structure

Modify existing files:

- `src/team_llm_wiki/wiki_ingest/models.py`: add first-class manifest fields, structured metadata dataclasses, raw-only metric shape, report fields for compiled paths and brief paths.
- `src/team_llm_wiki/wiki_ingest/manifest.py`: parse full manifest schema, normalize legacy fields, validate required spec fields.
- `src/team_llm_wiki/wiki_ingest/guards.py`: enforce packet-specific schemas, raw metric evidence, split leakage checks, PII-ish content checks.
- `src/team_llm_wiki/wiki_ingest/render.py`: render owner/task/dataset/split/model/claim boundary/status and compiled packet links into wiki pages.
- `src/team_llm_wiki/wiki_ingest/runner.py`: write compiled packet JSON in staging, include compiled/report/brief paths in reports, keep no-mutation guarantees.
- `src/team_llm_wiki/wiki_ingest/health.py`: expand scheduled/manual health checks.
- `src/team_llm_wiki/wiki_ingest/github_actions.py`: add PR comment rendering and safer workflow helper outputs.
- `src/team_llm_wiki/cli.py`: add `preview-wiki-ingest` and `generate-wiki-brief`.
- `.github/workflows/wiki-main-ingest.yml`: add concurrency and stricter loop guards.
- `.github/workflows/tests.yml`: keep pytest coverage.
- `README.md`, `wiki/team/contribution-workflow.md`, `wiki/team/wiki-ingest-policy.md`: update operator documentation.
- `automation/schemas/wiki-packet-manifest.schema.json`: align manifest schema with runtime.
- `raw/shared/templates/wiki-packet/*.yaml`: upgrade templates to full schema.

Create new files:

- `src/team_llm_wiki/wiki_ingest/packet_schemas.py`: deterministic validators for preprocessing, feature, model, performance, and augmentation packet YAML evidence.
- `src/team_llm_wiki/wiki_ingest/compile.py`: build normalized compiled packet JSON.
- `src/team_llm_wiki/wiki_ingest/brief.py`: generate daily/weekly markdown briefs from latest wiki/log/report state.
- `.github/workflows/wiki-pr-validate.yml`: PR packet validation and preview/comment workflow.
- `tests/wiki_ingest/test_packet_schemas.py`
- `tests/wiki_ingest/test_compile.py`
- `tests/wiki_ingest/test_brief.py`
- `tests/e2e/test_pr_preview_cli.py`
- `wiki/briefs/.gitkeep`

---

## Task 1: Full Manifest Model And Schema Alignment

**Files:**
- Modify: `src/team_llm_wiki/wiki_ingest/models.py`
- Modify: `src/team_llm_wiki/wiki_ingest/manifest.py`
- Modify: `automation/schemas/wiki-packet-manifest.schema.json`
- Modify: `raw/shared/templates/wiki-packet/manifest.yaml`
- Test: `tests/wiki_ingest/test_manifest.py`
- Test: `tests/wiki_ingest/test_models.py`

- [ ] **Step 1: Write failing tests for full manifest parsing**

Append tests to `tests/wiki_ingest/test_manifest.py`:

```python
def test_load_manifest_requires_full_spec_fields(tmp_path):
    packet = tmp_path / "raw" / "users" / "alice" / "experiments" / "demo"
    write_manifest(
        packet,
        date="2026-05-27",
        owner="alice",
        packet_type="experiment",
        type=None,
        status="submitted",
        task="sleep-health-hackathon",
        dataset={"name": "sleep-lifelog-2024", "version": "ch2026", "hash": "sha256:abc"},
        split={"name": "groupkfold-subject-5fold", "group_key": "subject_id", "fold_file": "folds.csv"},
        model={"family": "lightgbm-catboost", "weights_in_repo": False},
        claim_boundary="local_oof_diagnostic_only",
        claim_status="tentative",
        summary="Full experiment packet.",
        raw_paths={"performance": "performance.yaml", "folds": "folds.csv"},
        intended_wiki_targets=["wiki/experiments/"],
        metrics_to_verify=[],
    )

    manifest = load_packet_manifest(packet)

    assert manifest.id == "demo"
    assert manifest.owner == "alice"
    assert manifest.task == "sleep-health-hackathon"
    assert manifest.dataset.name == "sleep-lifelog-2024"
    assert manifest.dataset.version == "ch2026"
    assert manifest.split.name == "groupkfold-subject-5fold"
    assert manifest.split.group_key == "subject_id"
    assert manifest.split.fold_file == "folds.csv"
    assert manifest.model.family == "lightgbm-catboost"
    assert manifest.claim_boundary == "local_oof_diagnostic_only"
    assert manifest.claim_status == "tentative"
    assert manifest.raw_path_map["performance"] == "performance.yaml"
```

Append a missing-field test:

```python
@pytest.mark.parametrize("field", ["date", "owner", "status", "task", "dataset", "split", "claim_boundary", "summary", "raw_paths", "intended_wiki_targets"])
def test_load_manifest_rejects_missing_spec_required_fields(tmp_path, field):
    packet = tmp_path / "raw" / "users" / "alice" / "experiments" / "demo"
    data = {
        "id": "demo",
        "packet_type": "experiment",
        "title": "Demo",
        "date": "2026-05-27",
        "owner": "alice",
        "status": "submitted",
        "task": "sleep-health-hackathon",
        "dataset": {"name": "sleep-lifelog-2024", "version": "ch2026"},
        "split": {"name": "groupkfold-subject-5fold"},
        "claim_boundary": "local_oof_diagnostic_only",
        "summary": "Demo.",
        "raw_paths": {"performance": "performance.yaml"},
        "intended_wiki_targets": ["wiki/experiments/"],
    }
    data.pop(field)
    write_manifest(packet, **data)

    with pytest.raises(IngestFailure) as exc:
        load_packet_manifest(packet)

    assert exc.value.code is FailureCode.INVALID_MANIFEST
    assert field in exc.value.message
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_manifest.py::test_load_manifest_requires_full_spec_fields tests/wiki_ingest/test_manifest.py::test_load_manifest_rejects_missing_spec_required_fields -q
```

Expected: fail because `PacketManifest` has no first-class `owner`, `dataset`, `split`, `model`, `claim_boundary`, or `claim_status`.

- [ ] **Step 3: Implement structured manifest fields**

In `models.py`, add dataclasses:

```python
@dataclass
class DatasetRef:
    name: str
    version: str
    hash: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.version:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, "dataset.name and dataset.version are required")


@dataclass
class SplitRef:
    name: str
    group_key: str | None = None
    fold_file: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, "split.name is required")
        if self.fold_file:
            self.fold_file = _validate_manifest_rel_path(self.fold_file)


@dataclass
class ModelRef:
    family: str
    weights_in_repo: bool = False

    def __post_init__(self) -> None:
        if not self.family:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, "model.family is required")
```

Extend `PacketManifest` with:

```python
owner: str
task: str
dataset: DatasetRef | dict[str, Any]
split: SplitRef | dict[str, Any]
claim_boundary: str
claim_status: str = "tentative"
model: ModelRef | dict[str, Any] | None = None
```

Normalize dicts in `__post_init__`, validate `owner`, `task`, `claim_boundary`, and `claim_status in {"tentative", "supported", "disputed", "superseded"}`.

In `manifest.py`, add the new keys to `known` and require:

```python
required = ["id", "type", "title", "date", "owner", "status", "task", "dataset", "split", "claim_boundary", "summary", "raw_paths", "intended_wiki_targets"]
```

- [ ] **Step 4: Update schema and templates**

Update `automation/schemas/wiki-packet-manifest.schema.json` so the top-level `required` list includes all full spec required fields, and add object schemas for `dataset`, `split`, and `model`.

Update `raw/shared/templates/wiki-packet/manifest.yaml` to include every required field with safe example values.

- [ ] **Step 5: Run and commit**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_models.py tests/wiki_ingest/test_manifest.py -q
```

Expected: pass.

Commit:

```bash
git add src/team_llm_wiki/wiki_ingest/models.py src/team_llm_wiki/wiki_ingest/manifest.py automation/schemas/wiki-packet-manifest.schema.json raw/shared/templates/wiki-packet/manifest.yaml tests/wiki_ingest/test_models.py tests/wiki_ingest/test_manifest.py
git commit -m "feat: enforce full wiki packet manifest"
```

---

## Task 2: Packet-Specific Schema Validators

**Files:**
- Create: `src/team_llm_wiki/wiki_ingest/packet_schemas.py`
- Modify: `src/team_llm_wiki/wiki_ingest/guards.py`
- Modify: `raw/shared/templates/wiki-packet/preprocessing.yaml`
- Modify: `raw/shared/templates/wiki-packet/features.yaml`
- Modify: `raw/shared/templates/wiki-packet/model.yaml`
- Modify: `raw/shared/templates/wiki-packet/performance.yaml`
- Test: `tests/wiki_ingest/test_packet_schemas.py`
- Test: `tests/wiki_ingest/test_guards.py`

- [ ] **Step 1: Write failing packet schema tests**

Create `tests/wiki_ingest/test_packet_schemas.py`:

```python
from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest.models import FailureCode, IngestFailure, PacketType
from team_llm_wiki.wiki_ingest.packet_schemas import validate_packet_specific_schema


def write_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_feature_schema_requires_feature_family_fields(tmp_path):
    feature_file = tmp_path / "features.yaml"
    write_yaml(feature_file, {"feature_families": [{"name": "screen-charge"}]})

    with pytest.raises(IngestFailure) as exc:
        validate_packet_specific_schema(PacketType.FEATURE, {"features": "features.yaml"}, tmp_path)

    assert exc.value.code is FailureCode.INVALID_MANIFEST
    assert "source_modalities" in exc.value.message


def test_feature_schema_accepts_complete_family(tmp_path):
    write_yaml(
        tmp_path / "features.yaml",
        {
            "feature_families": [
                {
                    "name": "screen-charge",
                    "owner": "alice",
                    "source_modalities": ["screen", "charge"],
                    "feature_prefixes": ["sct_"],
                    "anchor": "date",
                    "window": "D-1",
                    "formula": "counts by hour",
                    "expected_dtype": "numeric",
                    "missing_policy": "fill_zero",
                    "leakage_risk": "low",
                    "target_hypothesis": "S1",
                    "evidence": "manual rationale",
                    "compute_cost": "low",
                    "dependencies": [],
                }
            ]
        },
    )

    validate_packet_specific_schema(PacketType.FEATURE, {"features": "features.yaml"}, tmp_path)


def test_performance_schema_requires_comparable_metrics(tmp_path):
    write_yaml(tmp_path / "performance.yaml", {"primary_metric": "grouped_macro_log_loss"})

    with pytest.raises(IngestFailure) as exc:
        validate_packet_specific_schema(PacketType.PERFORMANCE, {"performance": "performance.yaml"}, tmp_path)

    assert "overall_metrics" in exc.value.message
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_packet_schemas.py -q
```

Expected: fail because module does not exist.

- [ ] **Step 3: Implement packet schema validators**

Create `packet_schemas.py` with:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import FailureCode, IngestFailure, PacketType

REQUIRED_BY_PACKET_TYPE: dict[PacketType, dict[str, tuple[str, ...]]] = {
    PacketType.PREPROCESSING: {
        "preprocessing": (
            "input_sources", "row_identity", "target_scope", "split_strategy", "fold_assignment",
            "leakage_guards", "normalization", "feature_window_policy", "imputation", "code_entrypoint",
        )
    },
    PacketType.FEATURE: {
        "features": ("feature_families",)
    },
    PacketType.MODEL: {
        "model": (
            "family", "library_versions", "objective", "target_handling", "hyperparameters",
            "training_strategy", "validation_strategy", "calibration", "ensembling", "hardware",
            "inference_contract", "weights_policy",
        )
    },
    PacketType.PERFORMANCE: {
        "performance": (
            "primary_metric", "metric_definitions", "targets", "split_id", "overall_metrics",
            "target_metrics", "baseline_comparison", "claim_status",
        )
    },
    PacketType.AUGMENTATION: {
        "augmentation": (
            "source_data_scope", "generator", "prompt_or_recipe", "privacy_guard", "label_policy",
            "validation_policy", "failure_modes",
        )
    },
}

FEATURE_FAMILY_REQUIRED = (
    "name", "owner", "source_modalities", "feature_prefixes", "anchor", "window", "formula",
    "expected_dtype", "missing_policy", "leakage_risk", "target_hypothesis", "evidence",
    "compute_cost", "dependencies",
)


def _load_packet_yaml(packet_root: Path, raw_path_map: dict[str, str], label: str) -> dict[str, Any]:
    if label not in raw_path_map:
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label}.yaml raw_paths entry is required")
    path = (packet_root / raw_path_map[label]).resolve()
    try:
        path.relative_to(packet_root.resolve())
    except ValueError as exc:
        raise IngestFailure(FailureCode.PATH_ESCAPE, f"{label} path escapes packet root") from exc
    if not path.exists():
        raise IngestFailure(FailureCode.MISSING_RAW_FILE, f"{label} file is missing")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label} file must be a mapping")
    return data


def _require_keys(data: dict[str, Any], keys: tuple[str, ...], label: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label} missing required fields: {', '.join(missing)}")


def validate_packet_specific_schema(packet_type: PacketType, raw_path_map: dict[str, str], packet_root: Path) -> None:
    for label, required in REQUIRED_BY_PACKET_TYPE.get(packet_type, {}).items():
        data = _load_packet_yaml(packet_root, raw_path_map, label)
        _require_keys(data, required, label)
        if packet_type is PacketType.FEATURE:
            families = data.get("feature_families")
            if not isinstance(families, list) or not families:
                raise IngestFailure(FailureCode.INVALID_MANIFEST, "features.feature_families must be a non-empty list")
            for family in families:
                if not isinstance(family, dict):
                    raise IngestFailure(FailureCode.INVALID_MANIFEST, "feature family entry must be a mapping")
                _require_keys(family, FEATURE_FAMILY_REQUIRED, "feature family")
```

Call this from `guards.run_guard_checks()` after raw path existence checks:

```python
try:
    validate_packet_specific_schema(manifest.type, manifest.raw_path_map, packet_root)
except IngestFailure as exc:
    result.failures.append(GuardViolation(exc.code, exc.message, exc.details.get("path")))
```

- [ ] **Step 4: Upgrade packet templates**

Update each packet template so a copied template can pass its own packet-specific validator after placeholder evidence files are added.

- [ ] **Step 5: Run and commit**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_packet_schemas.py tests/wiki_ingest/test_guards.py -q
```

Commit:

```bash
git add src/team_llm_wiki/wiki_ingest/packet_schemas.py src/team_llm_wiki/wiki_ingest/guards.py raw/shared/templates/wiki-packet tests/wiki_ingest/test_packet_schemas.py tests/wiki_ingest/test_guards.py
git commit -m "feat: validate packet-specific evidence schemas"
```

---

## Task 3: Raw-Only Metrics And Split Leakage Guards

**Files:**
- Modify: `src/team_llm_wiki/wiki_ingest/models.py`
- Modify: `src/team_llm_wiki/wiki_ingest/guards.py`
- Test: `tests/wiki_ingest/test_guards.py`
- Test: `tests/e2e/test_cli.py`

- [ ] **Step 1: Add failing tests for raw-only metric evidence**

Append to `tests/wiki_ingest/test_guards.py`:

```python
def test_metric_check_requires_raw_path_not_manifest_actual(tmp_path):
    repo, packet_root, manifest, policy = seed_guard_repo(
        tmp_path,
        packet_type="performance",
        raw_paths={"performance": "performance.yaml"},
        metrics_to_verify=[{"name": "accuracy", "expected": 0.8, "actual": 0.8}],
    )
    (packet_root / "performance.yaml").write_text("accuracy: 0.7\n", encoding="utf-8")

    result = run_guard_checks(repo, packet_root, manifest, policy)

    assert any(failure.code is FailureCode.METRIC_MISMATCH for failure in result.failures)
```

Add a passing raw metric test using the spec field names:

```python
def test_metric_check_reads_raw_path_metric_key_and_reported_value(tmp_path):
    repo, packet_root, manifest, policy = seed_guard_repo(
        tmp_path,
        packet_type="performance",
        raw_paths={"performance": "performance.yaml"},
        metrics_to_verify=[
            {
                "raw_path": "performance.yaml",
                "metric_key": "overall_metrics.grouped_macro_log_loss",
                "reported_value": 0.6198,
            }
        ],
    )
    (packet_root / "performance.yaml").write_text("overall_metrics:\n  grouped_macro_log_loss: 0.6198\n", encoding="utf-8")

    result = run_guard_checks(repo, packet_root, manifest, policy)

    assert result.failures == []
```

- [ ] **Step 2: Add failing tests for grouped split overlap**

Append:

```python
def test_grouped_split_overlap_hard_fails(tmp_path):
    repo, packet_root, manifest, policy = seed_guard_repo(
        tmp_path,
        packet_type="experiment",
        raw_paths={"folds": "folds.csv", "performance": "performance.yaml"},
        split={"name": "groupkfold-subject-5fold", "group_key": "subject_id", "fold_file": "folds.csv"},
    )
    (packet_root / "performance.yaml").write_text("overall_metrics:\n  grouped_macro_log_loss: 0.5\n", encoding="utf-8")
    (packet_root / "folds.csv").write_text(
        "fold,split,subject_id\n0,train,A\n0,valid,A\n",
        encoding="utf-8",
    )

    result = run_guard_checks(repo, packet_root, manifest, policy)

    assert any(failure.code.value == "split_group_overlap" for failure in result.failures)
```

Add `SPLIT_GROUP_OVERLAP = "split_group_overlap"` to `FailureCode`.

- [ ] **Step 3: Run tests to verify failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_guards.py -q
```

Expected: fail on metric and split overlap tests.

- [ ] **Step 4: Implement raw metric and split guards**

In `MetricCheck`, support both spec and legacy names but normalize to raw-only:

```python
raw_path: str
metric_key: str
reported_value: float
tolerance: float = 0.0
```

In `__post_init__`, map `name/key/expected` to `metric_key/reported_value` only for legacy tests if `raw_path` exists. Reject `actual` without `raw_path`.

In `guards.py`, add CSV split validation:

```python
import csv

def _check_grouped_split_overlap(packet_root: Path, manifest: PacketManifest) -> list[GuardViolation]:
    if not manifest.split.fold_file or not manifest.split.group_key:
        return []
    path = (packet_root / manifest.split.fold_file).resolve()
    if not _is_inside(path, packet_root) or not path.exists():
        return [GuardViolation(FailureCode.MISSING_RAW_FILE, "split fold file is missing", manifest.split.fold_file)]
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    by_fold: dict[str, dict[str, set[str]]] = {}
    for row in rows:
        fold = row.get("fold", "0")
        split = (row.get("split") or row.get("role") or "").lower()
        group = row.get(manifest.split.group_key)
        if not group or split not in {"train", "valid", "validation", "val"}:
            continue
        normalized = "valid" if split in {"valid", "validation", "val"} else "train"
        by_fold.setdefault(fold, {"train": set(), "valid": set()})[normalized].add(group)
    failures = []
    for fold, groups in by_fold.items():
        overlap = groups["train"] & groups["valid"]
        if overlap:
            failures.append(GuardViolation(FailureCode.SPLIT_GROUP_OVERLAP, f"group overlap in fold {fold}: {', '.join(sorted(overlap))}", manifest.split.fold_file))
    return failures
```

Call it inside `run_guard_checks`.

- [ ] **Step 5: Run and commit**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_guards.py tests/e2e/test_cli.py -q
```

Commit:

```bash
git add src/team_llm_wiki/wiki_ingest/models.py src/team_llm_wiki/wiki_ingest/guards.py tests/wiki_ingest/test_guards.py tests/e2e/test_cli.py
git commit -m "feat: require raw metric and split evidence"
```

---

## Task 4: Compiled Packet JSON And Rich Wiki Rendering

**Files:**
- Create: `src/team_llm_wiki/wiki_ingest/compile.py`
- Modify: `src/team_llm_wiki/wiki_ingest/render.py`
- Modify: `src/team_llm_wiki/wiki_ingest/runner.py`
- Test: `tests/wiki_ingest/test_compile.py`
- Test: `tests/wiki_ingest/test_render.py`
- Test: `tests/wiki_ingest/test_runner.py`

- [ ] **Step 1: Add failing compile tests**

Create `tests/wiki_ingest/test_compile.py`:

```python
import json

from team_llm_wiki.wiki_ingest.compile import compile_packet
from team_llm_wiki.wiki_ingest.models import PacketManifest, PacketType


def test_compile_packet_contains_normalized_lineage_fields():
    manifest = PacketManifest(
        id="demo",
        type=PacketType.EXPERIMENT,
        title="Demo",
        date="2026-05-27",
        owner="alice",
        status="submitted",
        task="sleep-health-hackathon",
        dataset={"name": "sleep-lifelog-2024", "version": "ch2026"},
        split={"name": "groupkfold-subject-5fold", "group_key": "subject_id", "fold_file": "folds.csv"},
        model={"family": "lightgbm-catboost"},
        claim_boundary="local_oof_diagnostic_only",
        claim_status="tentative",
        summary="Demo.",
        raw_paths={"performance": "performance.yaml"},
        intended_wiki_targets=["wiki/experiments/"],
    )

    compiled = compile_packet(
        manifest,
        packet_root="raw/users/alice/experiments/demo",
        risk_tier="tier3-performance",
        publish_action="bot_pr",
    )

    assert compiled["id"] == "demo"
    assert compiled["owner"] == "alice"
    assert compiled["dataset"]["name"] == "sleep-lifelog-2024"
    assert compiled["split"]["group_key"] == "subject_id"
    assert compiled["model"]["family"] == "lightgbm-catboost"
    assert compiled["claim_status"] == "tentative"
    json.dumps(compiled, sort_keys=True)
```

- [ ] **Step 2: Add failing render test for lineage fields**

Append to `tests/wiki_ingest/test_render.py`:

```python
def test_render_packet_page_includes_full_lineage_fields(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    manifest = PacketManifest(
        id="exp-lineage",
        type="experiment",
        title="Experiment Lineage",
        date="2026-05-27",
        owner="alice",
        status="submitted",
        task="sleep-health-hackathon",
        dataset={"name": "sleep-lifelog-2024", "version": "ch2026"},
        split={"name": "groupkfold-subject-5fold", "group_key": "subject_id"},
        model={"family": "lightgbm-catboost"},
        claim_boundary="local_oof_diagnostic_only",
        claim_status="tentative",
        summary="Lineage summary.",
        raw_paths={"performance": "performance.yaml"},
        intended_wiki_targets=["wiki/experiments/"],
    )

    render_packets(tmp_path, [(manifest, RiskTier.BOT_PR)], run_id="run-lineage")

    page = (tmp_path / "wiki" / "experiments" / "exp-lineage.md").read_text(encoding="utf-8")
    assert "owner: alice" in page
    assert "task: sleep-health-hackathon" in page
    assert "dataset: sleep-lifelog-2024@ch2026" in page
    assert "split: groupkfold-subject-5fold" in page
    assert "claim_boundary: local_oof_diagnostic_only" in page
    assert "claim_status: tentative" in page
```

- [ ] **Step 3: Implement compile and rendering**

Create `compile.py`:

```python
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from .models import PacketManifest, as_jsonable


def compile_packet(manifest: PacketManifest, packet_root: str, risk_tier: str) -> dict[str, Any]:
    return {
        "id": manifest.id,
        "packet_type": manifest.type.value,
        "title": manifest.title,
        "date": manifest.date,
        "owner": manifest.owner,
        "status": manifest.status,
        "task": manifest.task,
        "dataset": as_jsonable(manifest.dataset),
        "split": as_jsonable(manifest.split),
        "model": as_jsonable(manifest.model) if manifest.model else None,
        "claim_boundary": manifest.claim_boundary,
        "claim_status": manifest.claim_status,
        "summary": manifest.summary,
        "raw_paths": manifest.raw_path_map,
        "intended_wiki_targets": manifest.intended_wiki_targets,
        "metrics_to_verify": as_jsonable(manifest.metrics_to_verify),
        "claims": as_jsonable(manifest.claims),
        "packet_root": packet_root,
        "risk_tier": risk_tier,
    }
```

In `runner.py`, after `_build_report` succeeds and before render copy-back, write compiled JSON under:

```text
automation/.cache/compiled/<packet-id>.json
```

Add generated compiled paths to `report.generated_paths` and `report.changed_paths`.

In `render.py`, include full manifest fields in frontmatter and body.

- [ ] **Step 4: Run and commit**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_compile.py tests/wiki_ingest/test_render.py tests/wiki_ingest/test_runner.py -q
```

Commit:

```bash
git add src/team_llm_wiki/wiki_ingest/compile.py src/team_llm_wiki/wiki_ingest/render.py src/team_llm_wiki/wiki_ingest/runner.py tests/wiki_ingest/test_compile.py tests/wiki_ingest/test_render.py tests/wiki_ingest/test_runner.py
git commit -m "feat: compile packet lineage into wiki updates"
```

---

## Task 5: PR Validation Preview Workflow

**Files:**
- Modify: `src/team_llm_wiki/cli.py`
- Modify: `src/team_llm_wiki/wiki_ingest/github_actions.py`
- Create: `.github/workflows/wiki-pr-validate.yml`
- Test: `tests/wiki_ingest/test_github_actions.py`
- Test: `tests/e2e/test_pr_preview_cli.py`

- [ ] **Step 1: Add failing helper tests**

Append to `tests/wiki_ingest/test_github_actions.py`:

```python
def test_render_pr_comment_includes_preview_and_failures():
    from team_llm_wiki.wiki_ingest.github_actions import render_pr_comment

    comment = render_pr_comment(
        {
            "status": "bot_pr",
            "packet_roots": ["raw/users/alice/experiments/demo"],
            "packets": [{"id": "demo", "type": "experiment", "publish_action": "bot_pr", "risk_tier": "tier3-performance"}],
            "generated_paths": ["wiki/experiments/demo.md"],
            "failures": [{"code": "metric_mismatch", "message": "raw mismatch"}],
        }
    )

    assert "Wiki ingest preview" in comment
    assert "raw/users/alice/experiments/demo" in comment
    assert "wiki/experiments/demo.md" in comment
    assert "metric_mismatch" in comment
```

- [ ] **Step 2: Add failing CLI E2E test**

Create `tests/e2e/test_pr_preview_cli.py`:

```python
import json
import subprocess
import sys
from pathlib import Path


def test_preview_wiki_ingest_outputs_json_without_wiki_mutation(tmp_path):
    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("@AGENTS.md", encoding="utf-8")
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "wiki" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (tmp_path / "wiki" / "log.md").write_text("# Log\n", encoding="utf-8")
    packet = tmp_path / "raw" / "users" / "alice" / "references" / "demo"
    packet.mkdir(parents=True)
    (packet / "README.md").write_text("note", encoding="utf-8")
    (packet / "manifest.yaml").write_text(
        "id: demo\npacket_type: reference\ntitle: Demo\ndate: '2026-05-27'\nowner: alice\nstatus: submitted\ntask: sleep-health-hackathon\ndataset: {name: sleep-lifelog-2024, version: ch2026}\nsplit: {name: none}\nclaim_boundary: local_oof_diagnostic_only\nsummary: Demo.\nraw_paths: {readme: README.md}\nintended_wiki_targets: [wiki/sources/]\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "team_llm_wiki.cli",
            "preview-wiki-ingest",
            "--repo-root",
            str(tmp_path),
            "--changed-path",
            "raw/users/alice/references/demo/manifest.yaml",
        ],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "direct_commit"
    assert not (tmp_path / "wiki" / "sources").exists()
```

- [ ] **Step 3: Implement helper, CLI, and workflow**

Add `render_pr_comment(payload: dict) -> str` to `github_actions.py`.

Add CLI subcommand:

```text
preview-wiki-ingest --repo-root . --changed-path-file changed-paths.txt
```

It should call `plan_wiki_main_ingest`, print JSON, and never write wiki files.

Create `.github/workflows/wiki-pr-validate.yml`:

```yaml
name: wiki-pr-validate

on:
  pull_request:
    paths:
      - "raw/users/**"
      - "AGENTS.md"
      - "CLAUDE.md"
      - "automation/schemas/**"

permissions:
  contents: read
  pull-requests: write

jobs:
  preview:
    if: ${{ !startsWith(github.event.pull_request.title || '', '[wiki-bot]') }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: python -m pip install -e .[test]
      - name: Collect changed paths
        run: git diff --name-only origin/${{ github.base_ref }}...HEAD > changed-paths.txt
      - name: Preview wiki ingest
        env:
          PYTHONPATH: src
        run: |
          python -m team_llm_wiki.cli preview-wiki-ingest \
            --repo-root . \
            --changed-path-file changed-paths.txt > preview.json
      - name: Comment preview
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const payload = JSON.parse(fs.readFileSync('preview.json', 'utf8'));
            const body = [
              '## Wiki ingest preview',
              '',
              `- status: \`${payload.status}\``,
              `- packets: \`${payload.packet_roots.length}\``,
              `- generated paths: \`${payload.generated_paths.length}\``,
              '',
              '```json',
              JSON.stringify(payload, null, 2).slice(0, 6000),
              '```'
            ].join('\n');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body
            });
```

- [ ] **Step 4: Run and commit**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_github_actions.py tests/e2e/test_pr_preview_cli.py -q
python - <<'PY'
from pathlib import Path
import yaml
for path in Path('.github/workflows').glob('*.yml'):
    yaml.safe_load(path.read_text(encoding='utf-8'))
PY
```

Commit:

```bash
git add src/team_llm_wiki/cli.py src/team_llm_wiki/wiki_ingest/github_actions.py .github/workflows/wiki-pr-validate.yml tests/wiki_ingest/test_github_actions.py tests/e2e/test_pr_preview_cli.py
git commit -m "feat: add wiki packet PR preview"
```

---

## Task 6: Expanded Scheduled Health Checks

**Files:**
- Modify: `src/team_llm_wiki/wiki_ingest/health.py`
- Test: `tests/wiki_ingest/test_health.py`

- [ ] **Step 1: Add failing health tests**

Append to `tests/wiki_ingest/test_health.py`:

```python
def test_health_detects_orphan_wiki_page_missing_from_index(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "features").mkdir()
    (tmp_path / "wiki" / "features" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")

    report = check_wiki_health(tmp_path)

    assert any(error.code == "orphan_wiki_page" for error in report.errors)


def test_health_detects_supported_claim_without_raw_evidence(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "sources").mkdir()
    (tmp_path / "wiki" / "sources" / "supported.md").write_text(
        "---\nclaim_status: supported\n---\n\n# Supported\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert any(error.code == "supported_claim_missing_raw" for error in report.errors)


def test_health_detects_stale_tentative_claim(tmp_path):
    seed_clean(tmp_path)
    (tmp_path / "wiki" / "sources").mkdir()
    (tmp_path / "wiki" / "sources" / "old.md").write_text(
        "---\nclaim_status: tentative\ndate: 2026-01-01\n---\n\n# Old\n",
        encoding="utf-8",
    )

    report = check_wiki_health(tmp_path)

    assert any(error.code == "stale_tentative_claim" for error in report.errors)
```

- [ ] **Step 2: Implement new health errors**

Add `HealthError` codes as plain strings:

- `orphan_wiki_page`
- `supported_claim_missing_raw`
- `stale_tentative_claim`
- `performance_metric_unverified`

Implement simple frontmatter parser for top-of-file `---` blocks. Rules:

- Ignore `wiki/index.md`, `wiki/log.md`, `wiki/latest-context.md`, `wiki/overview.md`, and `wiki/team/**`.
- A generated page is indexed if `wiki/index.md` contains either its relative path with `.md` or its wiki link without `.md`.
- `claim_status: supported` requires `raw_evidence:` in page text or `related_raw` frontmatter.
- `claim_status: tentative` older than 14 days from `date.today()` emits stale warning.

- [ ] **Step 3: Run and commit**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_health.py -q
```

Commit:

```bash
git add src/team_llm_wiki/wiki_ingest/health.py tests/wiki_ingest/test_health.py
git commit -m "feat: expand wiki health checks"
```

---

## Task 7: Brief Generation And Context Distribution

**Files:**
- Create: `src/team_llm_wiki/wiki_ingest/brief.py`
- Modify: `src/team_llm_wiki/cli.py`
- Modify: `.github/workflows/wiki-health-check.yml`
- Create: `wiki/briefs/.gitkeep`
- Test: `tests/wiki_ingest/test_brief.py`
- Test: `tests/e2e/test_cli.py`

- [ ] **Step 1: Add failing brief tests**

Create `tests/wiki_ingest/test_brief.py`:

```python
from team_llm_wiki.wiki_ingest.brief import generate_daily_brief


def test_generate_daily_brief_writes_dated_brief_and_latest_pointer(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "log.md").write_text("# Log\n\n## [2026-05-27] ingest | demo\n\n- target: `wiki/sources/demo.md`\n", encoding="utf-8")
    (tmp_path / "wiki" / "latest-context.md").write_text("# Latest Context\n\n[[index]] [[overview]] [[log]]\n", encoding="utf-8")

    paths = generate_daily_brief(tmp_path, date="2026-05-27")

    brief = tmp_path / "wiki" / "briefs" / "2026-05-27-daily.md"
    latest = tmp_path / "wiki" / "briefs" / "latest.md"
    assert paths == ["wiki/briefs/2026-05-27-daily.md", "wiki/briefs/latest.md"]
    assert "New packets ingested" in brief.read_text(encoding="utf-8")
    assert "[[2026-05-27-daily]]" in latest.read_text(encoding="utf-8")
```

- [ ] **Step 2: Implement brief generator**

Create `brief.py`:

```python
from __future__ import annotations

from datetime import date as date_type
from pathlib import Path


def generate_daily_brief(repo_root: Path, date: str | None = None) -> list[str]:
    today = date or date_type.today().isoformat()
    briefs = repo_root / "wiki" / "briefs"
    briefs.mkdir(parents=True, exist_ok=True)
    log_text = (repo_root / "wiki" / "log.md").read_text(encoding="utf-8") if (repo_root / "wiki" / "log.md").exists() else ""
    recent_lines = [line for line in log_text.splitlines() if today in line or line.startswith("- target:")]
    body = "\n".join(
        [
            "---",
            f"date: {today}",
            "type: daily-brief",
            "---",
            "",
            f"# {today} Daily Brief",
            "",
            "## New packets ingested",
            "",
            *(recent_lines or ["- No packet ingests recorded for this date."]),
            "",
            "## Session context",
            "",
            "- Start from [[latest-context]].",
        ]
    )
    brief_path = briefs / f"{today}-daily.md"
    latest_path = briefs / "latest.md"
    brief_path.write_text(body.rstrip() + "\n", encoding="utf-8")
    latest_path.write_text(f"# Latest Brief\n\n[[{today}-daily]]\n", encoding="utf-8")
    return [brief_path.relative_to(repo_root).as_posix(), latest_path.relative_to(repo_root).as_posix()]
```

Add CLI:

```text
generate-wiki-brief --repo-root . --date YYYY-MM-DD
```

Update `wiki-health-check.yml` to run health, then generate a daily brief on schedule/manual and upload both report and brief artifacts. Do not modify `raw/`.

- [ ] **Step 3: Run and commit**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest tests/wiki_ingest/test_brief.py tests/e2e/test_cli.py -q
```

Commit:

```bash
git add src/team_llm_wiki/wiki_ingest/brief.py src/team_llm_wiki/cli.py .github/workflows/wiki-health-check.yml wiki/briefs/.gitkeep tests/wiki_ingest/test_brief.py tests/e2e/test_cli.py
git commit -m "feat: generate wiki daily briefs"
```

---

## Task 8: Workflow Loop Guards, Docs, And Final Verification

**Files:**
- Modify: `.github/workflows/wiki-main-ingest.yml`
- Modify: `.github/workflows/tests.yml`
- Modify: `README.md`
- Modify: `wiki/team/contribution-workflow.md`
- Modify: `wiki/team/wiki-ingest-policy.md`
- Modify: `docs/spec.md`
- Modify: `docs/test-plan.md`
- Test: `tests/wiki_ingest/test_github_actions.py`

- [ ] **Step 1: Add workflow helper tests**

Append to `tests/wiki_ingest/test_github_actions.py`:

```python
def test_should_skip_wiki_ingest_for_bot_commit_prefix():
    from team_llm_wiki.wiki_ingest.github_actions import should_skip_wiki_ingest

    assert should_skip_wiki_ingest(actor="github-actions[bot]", commit_message="[wiki-bot] ingest demo", pr_title=None)
    assert should_skip_wiki_ingest(actor="alice", commit_message="docs", pr_title="[wiki-bot] ingest demo")
    assert not should_skip_wiki_ingest(actor="alice", commit_message="raw packet", pr_title=None)
```

- [ ] **Step 2: Implement helper and workflow hardening**

Add helper:

```python
def should_skip_wiki_ingest(actor: str, commit_message: str | None = None, pr_title: str | None = None) -> bool:
    if actor == "github-actions[bot]" and (commit_message or "").startswith("[wiki-bot]"):
        return True
    if (pr_title or "").startswith("[wiki-bot]"):
        return True
    return False
```

Update `wiki-main-ingest.yml`:

- Add:

```yaml
concurrency:
  group: wiki-ingest-${{ github.ref }}
  cancel-in-progress: false
```

- Use commit prefix `[wiki-bot] ingest wiki packets`.
- Preserve `github-actions[bot]` loop skip.
- Avoid `[skip ci]` unless explicitly intentional.

- [ ] **Step 3: Update docs**

Update README and team wiki docs to describe:

- full manifest required fields
- packet-specific YAML required fields
- raw-only metric evidence
- grouped split fold-file contract
- PR preview workflow
- daily brief generation
- known GitHub workflow dispatch caveat if still observed

- [ ] **Step 4: Final verification**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
python -m pip install -e . --dry-run
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root . --report-path /tmp/team-llm-wiki-health-spec-complete.json
python - <<'PY'
from pathlib import Path
import yaml
for path in sorted(Path(".github/workflows").glob("*.yml")):
    yaml.safe_load(path.read_text(encoding="utf-8"))
    print(path)
PY
git diff --check
```

Expected:

- All pytest tests pass.
- Editable install dry-run succeeds.
- Health report returns `ok: true`.
- All workflow YAML files parse.
- `git diff --check` has no output.

Commit:

```bash
git add .github/workflows README.md wiki/team docs tests/wiki_ingest/test_github_actions.py src/team_llm_wiki/wiki_ingest/github_actions.py
git commit -m "chore: document completed wiki ingest spec"
```

---

## Self-Review Checklist

- Spec coverage:
  - Full manifest fields: Task 1.
  - Packet-specific schemas: Task 2.
  - Raw-only metric and split evidence: Task 3.
  - Compiled packet JSON: Task 4.
  - PR validation preview/comment: Task 5.
  - Expanded scheduled lint: Task 6.
  - Daily brief and latest pointer: Task 7.
  - Loop guards/docs/final verification: Task 8.
- Placeholder scan: no `TBD`, `TODO`, or "implement later" instructions are allowed in this plan.
- Type consistency:
  - Use `manifest.id`, `manifest.type`, `manifest.owner`, `manifest.dataset`, `manifest.split`, `manifest.model`, `manifest.claim_boundary`, and `manifest.claim_status`.
  - Use `MetricCheck.raw_path`, `MetricCheck.metric_key`, and `MetricCheck.reported_value`.
  - Use `IngestReport.status` with values `direct_commit`, `bot_pr`, `hard_fail`, and `skipped`.

## Completion Gate

Do not mark the feature complete until all of these are true in the current repository state:

- All tasks above are committed on `feature/spec-complete`.
- Spec compliance review reports no missing Phase 0-3 requirements from the drift audit.
- Code-quality/security review reports no P0/P1 blockers.
- Final verification commands from Task 8 pass.
- Branch is merged into `main` and pushed to `https://github.com/chunryongoh/team_llm_wiki`.
- Parent wiki report and log are updated with the final implementation result.
