from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import FailureCode, GuardViolation, IngestFailure


@dataclass
class IngestPolicy:
    agents_text: str
    claude_text: str = ""
    warnings: list[str] = field(default_factory=list)
    failures: list[GuardViolation] = field(default_factory=list)
    max_packet_files: int = 100
    max_packet_text_bytes: int = 1_000_000
    latest_context_max_entries: int = 12
    latest_context_max_chars: int = 6_000


def load_policy(repo_root: Path) -> IngestPolicy:
    agents_path = repo_root / "AGENTS.md"
    if not agents_path.exists():
        raise IngestFailure(FailureCode.POLICY_MISSING, "AGENTS.md is required")
    claude_path = repo_root / "CLAUDE.md"
    agents_text = agents_path.read_text(encoding="utf-8")
    claude_text = claude_path.read_text(encoding="utf-8") if claude_path.exists() else ""
    warnings: list[str] = []
    failures: list[GuardViolation] = []
    if claude_path.exists() and "@AGENTS.md" not in claude_text:
        warnings.append("CLAUDE.md does not import @AGENTS.md")
    lower = claude_text.lower()
    protected_conflicts = [
        ("raw immutability", ["rewrite raw", "raw files are mutable", "raw/ is mutable"]),
        ("secret handling", ["ignore secrets", "allow secrets", "commit secrets"]),
        ("claim promotion", ["promote supported claims without review", "supported claims without review"]),
        ("protected paths", ["edit generated wiki directly", "bypass protected paths"]),
    ]
    for label, phrases in protected_conflicts:
        if any(phrase in lower for phrase in phrases):
            failures.append(
                GuardViolation(FailureCode.POLICY_CONFLICT, f"CLAUDE.md conflicts with AGENTS.md on {label}", "CLAUDE.md")
            )
    return IngestPolicy(agents_text=agents_text, claude_text=claude_text, warnings=warnings, failures=failures)
