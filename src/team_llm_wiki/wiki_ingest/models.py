from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from pathlib import Path
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
    actual: float
    tolerance: float = 0.0

    def is_consistent(self) -> bool:
        return abs(float(self.expected) - float(self.actual)) <= float(self.tolerance)


@dataclass
class Claim:
    status: str
    text: str = ""


@dataclass
class PacketManifest:
    id: str
    type: PacketType | str
    title: str
    date: str | None = None
    status: str = "draft"
    summary: str = ""
    raw_paths: list[str] = field(default_factory=list)
    intended_wiki_targets: list[str] = field(default_factory=list)
    metrics_to_verify: list[MetricCheck | dict[str, Any]] = field(default_factory=list)
    claims: list[Claim | dict[str, Any]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            self.type = PacketType(self.type)
        except ValueError as exc:
            raise IngestFailure(FailureCode.INVALID_MANIFEST, f"unknown packet type: {self.type}") from exc
        self.metrics_to_verify = [
            item if isinstance(item, MetricCheck) else MetricCheck(**item) for item in self.metrics_to_verify
        ]
        self.claims = [item if isinstance(item, Claim) else Claim(**item) for item in self.claims]


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
    packet_roots: list[str] = field(default_factory=list)
    packets: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    link_lint_errors: list[dict[str, Any]] = field(default_factory=list)


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
