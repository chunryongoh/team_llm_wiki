from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Any


class PacketType(str, Enum):
    REFERENCE = "reference"
    MEETING = "meeting"
    EXPERIMENT = "experiment"
    FEATURE = "feature"
    MODEL = "model"
    PERFORMANCE = "performance"
    PREPROCESSING = "preprocessing"
    AUGMENTATION = "augmentation"


class RiskTier(str, Enum):
    DIRECT_COMMIT = "direct_commit"
    BOT_PR = "bot_pr"
    HARD_FAIL = "hard_fail"


class FailureCode(str, Enum):
    INVALID_CHANGED_PATH = "invalid_changed_path"
    INVALID_MANIFEST = "invalid_manifest"
    POLICY_MISSING = "policy_missing"
    PATH_ESCAPE = "path_escape"
    MISSING_RAW_FILE = "missing_raw_file"
    SECRET_CONTENT = "secret_content"
    FORBIDDEN_SECRET_FILE = "forbidden_secret_file"
    MODEL_WEIGHT_FILE = "model_weight_file"
    INVALID_TARGET_ROUTE = "invalid_target_route"
    METRIC_MISMATCH = "metric_mismatch"
    PACKET_TOO_LARGE = "packet_too_large"
    POLICY_CONFLICT = "policy_conflict"
    BROKEN_WIKI_LINK = "broken_wiki_link"
    UNBALANCED_GENERATED_BLOCK = "unbalanced_generated_block"
    MISSING_REQUIRED_LATEST_LINK = "missing_required_latest_link"


class IngestFailure(Exception):
    def __init__(self, code: FailureCode | str, message: str, details: dict[str, Any] | None = None):
        self.code = FailureCode(code)
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code.value, "message": self.message, "details": as_jsonable(self.details)}


@dataclass
class MetricCheck:
    name: str
    expected: float
    actual: float | None = None
    tolerance: float = 0.0
    raw_path: str | None = None
    key: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip() or CONTROL_RE.search(self.name):
            raise IngestFailure(FailureCode.INVALID_MANIFEST, "metric name is required")
        try:
            self.expected = float(self.expected)
            self.tolerance = float(self.tolerance)
            if self.actual is not None:
                self.actual = float(self.actual)
        except (TypeError, ValueError) as exc:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, f"metric {self.name} has non-numeric values") from exc
        if self.raw_path is not None:
            if not isinstance(self.raw_path, str):
                raise IngestFailure(FailureCode.INVALID_MANIFEST, f"metric {self.name} raw_path must be a string")
            self.raw_path = _validate_manifest_rel_path(self.raw_path)
        if self.actual is None and not self.raw_path:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, f"metric {self.name} requires actual or raw_path")

    def is_consistent(self) -> bool:
        if self.actual is None:
            return True
        return abs(float(self.expected) - float(self.actual)) <= float(self.tolerance)


@dataclass
class Claim:
    status: str
    text: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"tentative", "supported", "disputed", "superseded"}:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, f"invalid claim status: {self.status}")
        if not isinstance(self.text, str):
            raise IngestFailure(FailureCode.INVALID_MANIFEST, "claim text must be a string")


@dataclass
class DatasetRef:
    name: str
    version: str
    hash: str | None = None

    def __post_init__(self) -> None:
        self.name = _require_non_empty_string(self.name, "dataset.name")
        self.version = _require_non_empty_string(self.version, "dataset.version")
        if self.hash is not None:
            self.hash = _require_non_empty_string(self.hash, "dataset.hash")


@dataclass
class SplitRef:
    name: str
    group_key: str | None = None
    fold_file: str | None = None

    def __post_init__(self) -> None:
        self.name = _require_non_empty_string(self.name, "split.name")
        if self.group_key is not None:
            self.group_key = _require_non_empty_string(self.group_key, "split.group_key")
        if self.fold_file is not None:
            self.fold_file = _validate_manifest_rel_path(_require_non_empty_string(self.fold_file, "split.fold_file"))


@dataclass
class ModelRef:
    family: str
    weights_in_repo: bool = False

    def __post_init__(self) -> None:
        self.family = _require_non_empty_string(self.family, "model.family")
        if not isinstance(self.weights_in_repo, bool):
            raise IngestFailure(FailureCode.INVALID_MANIFEST, "model.weights_in_repo must be a boolean")


@dataclass
class PacketManifest:
    id: str
    type: PacketType | str
    title: str
    date: str
    owner: str
    status: str
    task: str
    dataset: DatasetRef | dict[str, Any]
    split: SplitRef | dict[str, Any]
    model: ModelRef | dict[str, Any]
    claim_boundary: str
    claim_status: str
    summary: str
    raw_paths: list[str] | dict[str, str]
    intended_wiki_targets: list[str]
    metrics_to_verify: list[MetricCheck | dict[str, Any]] = field(default_factory=list)
    claims: list[Claim | dict[str, Any]] = field(default_factory=list)
    raw_path_map: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_kebab_id(self.id)
        try:
            self.type = PacketType(self.type)
        except ValueError as exc:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, f"unknown packet type: {self.type}") from exc
        self.title = _require_non_empty_string(self.title, "title")
        self.date = _require_non_empty_string(self.date, "date")
        self.owner = _require_non_empty_string(self.owner, "owner")
        self.status = _require_non_empty_string(self.status, "status")
        self.task = _require_non_empty_string(self.task, "task")
        self.claim_boundary = _require_non_empty_string(self.claim_boundary, "claim_boundary")
        self.summary = _require_non_empty_string(self.summary, "summary")
        if self.claim_status not in {"tentative", "supported", "disputed", "superseded"}:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, f"invalid claim status: {self.claim_status}")
        try:
            if isinstance(self.dataset, DatasetRef):
                pass
            else:
                self.dataset = DatasetRef(**_require_mapping(self.dataset, "dataset"))
            if isinstance(self.split, SplitRef):
                pass
            else:
                self.split = SplitRef(**_require_mapping(self.split, "split"))
            if self.model is None:
                raise IngestFailure(FailureCode.INVALID_MANIFEST, "model is required")
            if not isinstance(self.model, ModelRef):
                self.model = ModelRef(**_require_mapping(self.model, "model"))
        except TypeError as exc:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, str(exc)) from exc
        if isinstance(self.raw_paths, dict):
            self.raw_path_map = {
                str(key): _validate_manifest_rel_path(_require_non_empty_string(value, f"raw_paths.{key}"))
                for key, value in self.raw_paths.items()
            }
            self.raw_paths = list(self.raw_path_map.values())
        elif isinstance(self.raw_paths, list):
            self.raw_paths = [
                _validate_manifest_rel_path(_require_non_empty_string(item, "raw_paths[]")) for item in self.raw_paths
            ]
        else:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, "raw_paths must be a list or mapping")
        try:
            self.metrics_to_verify = [
                item if isinstance(item, MetricCheck) else MetricCheck(**_require_mapping(item, "metric"))
                for item in self.metrics_to_verify
            ]
            self.claims = [
                item if isinstance(item, Claim) else Claim(**_require_mapping(item, "claim")) for item in self.claims
            ]
        except TypeError as exc:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, str(exc)) from exc
        self.intended_wiki_targets = [_validate_manifest_rel_path(str(item)) for item in self.intended_wiki_targets]


@dataclass
class GuardViolation:
    code: FailureCode | str
    message: str
    path: str | None = None

    def __post_init__(self) -> None:
        self.code = FailureCode(self.code)


@dataclass
class GuardResult:
    failures: list[GuardViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


@dataclass
class RiskDecision:
    tier: RiskTier
    reasons: list[str] = field(default_factory=list)


@dataclass
class RenderResult:
    changed_paths: list[str] = field(default_factory=list)


@dataclass
class IngestReport:
    status: str
    run_id: str
    input_changed_paths: list[str] = field(default_factory=list)
    packet_roots: list[str] = field(default_factory=list)
    packets: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    policy_warnings: list[str] = field(default_factory=list)
    generated_paths: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    link_lint_errors: list[dict[str, Any]] = field(default_factory=list)
    report_path: str | None = None
    timing_ms: int = 0


@dataclass
class HealthError:
    code: str
    message: str
    path: str | None = None


@dataclass
class HealthReport:
    ok: bool
    errors: list[HealthError] = field(default_factory=list)
    checked_paths: list[str] = field(default_factory=list)


def as_jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return {key: as_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): as_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [as_jsonable(item) for item in value]
    return value


ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


def _validate_kebab_id(value: str) -> None:
    if not isinstance(value, str) or not ID_RE.fullmatch(value) or "/" in value or "\\" in value or CONTROL_RE.search(value):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, "id must be ASCII kebab-case without separators")


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or CONTROL_RE.search(value):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label} must be a non-empty string")
    return value


def _coerce_optional_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or CONTROL_RE.search(value):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label} must be a string")
    return value


def _validate_manifest_rel_path(value: str) -> str:
    if not value or not value.strip() or "\\" in value or "//" in value or CONTROL_RE.search(value):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"invalid manifest path: {value}")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"manifest path escapes packet or repo: {value}")
    return path.as_posix()


def _validate_loose_rel_path(value: str) -> str:
    if not value or "\\" in value or "//" in value or CONTROL_RE.search(value):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"invalid manifest path: {value}")
    return Path(value).as_posix()


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IngestFailure(FailureCode.INVALID_MANIFEST, f"{label} entry must be a mapping")
    return value
