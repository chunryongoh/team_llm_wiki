from __future__ import annotations

import re
from pathlib import Path

from .models import FailureCode, GuardResult, GuardViolation, PacketManifest
from .policy import IngestPolicy
from .routes import PACKET_ROUTE_MAP

SECRET_NAME_SUFFIXES = {".env", ".pem", ".key", ".p12", ".pfx"}
SECRET_NAMES = {"id_rsa", "id_dsa", "id_ed25519", "credentials.json"}
MODEL_WEIGHT_SUFFIXES = {".pt", ".pth", ".ckpt", ".safetensors", ".onnx"}
SECRET_CONTENT_RE = re.compile(
    r"(OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY|BEGIN (RSA|OPENSSH|PRIVATE) KEY|sk-[A-Za-z0-9_-]{8,})"
)


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def run_guard_checks(repo_root: Path, packet_root: Path, manifest: PacketManifest, policy: IngestPolicy) -> GuardResult:
    result = GuardResult(warnings=list(policy.warnings))
    files = [path for path in packet_root.rglob("*") if path.is_file()]
    if len(files) > policy.max_packet_files:
        result.failures.append(GuardViolation(FailureCode.PACKET_TOO_LARGE, "packet file count exceeds limit"))

    text_bytes = 0
    for path in files:
        lower_name = path.name.lower()
        lower_suffix = path.suffix.lower()
        if lower_name in SECRET_NAMES or lower_name in SECRET_NAME_SUFFIXES or lower_suffix in SECRET_NAME_SUFFIXES:
            result.failures.append(
                GuardViolation(FailureCode.FORBIDDEN_SECRET_FILE, "forbidden secret filename", path.as_posix())
            )
        if lower_suffix in MODEL_WEIGHT_SUFFIXES:
            result.failures.append(GuardViolation(FailureCode.MODEL_WEIGHT_FILE, "model weight file is forbidden", path.as_posix()))
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        text_bytes += len(content.encode("utf-8"))
        if SECRET_CONTENT_RE.search(content):
            result.failures.append(GuardViolation(FailureCode.SECRET_CONTENT, "secret-like content detected", path.as_posix()))

    if text_bytes > policy.max_packet_text_bytes:
        result.failures.append(GuardViolation(FailureCode.PACKET_TOO_LARGE, "packet text bytes exceed limit"))

    for raw in manifest.raw_paths:
        candidate = (packet_root / raw).resolve()
        if not _is_inside(candidate, packet_root):
            result.failures.append(GuardViolation(FailureCode.PATH_ESCAPE, "raw path escapes packet root", raw))
            continue
        if not candidate.exists():
            result.failures.append(GuardViolation(FailureCode.MISSING_RAW_FILE, "raw path is missing", raw))

    expected_route = PACKET_ROUTE_MAP[manifest.type] + "/"
    for target in manifest.intended_wiki_targets:
        target_path = Path(target)
        if target_path.is_absolute() or ".." in target_path.parts:
            result.failures.append(GuardViolation(FailureCode.PATH_ESCAPE, "target path escapes repo", target))
        elif not target.startswith(expected_route):
            result.failures.append(
                GuardViolation(FailureCode.INVALID_TARGET_ROUTE, f"target must be under {expected_route}", target)
            )

    for metric in manifest.metrics_to_verify:
        if not metric.is_consistent():
            result.failures.append(GuardViolation(FailureCode.METRIC_MISMATCH, f"metric mismatch: {metric.name}"))

    return result
