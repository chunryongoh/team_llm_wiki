from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .models import FailureCode, IngestFailure


@dataclass
class IngestPolicy:
    agents_text: str
    claude_text: str = ""
    warnings: list[str] = field(default_factory=list)
    max_packet_files: int = 100
    max_packet_text_bytes: int = 1_000_000
    latest_context_max_entries: int = 20


def load_policy(repo_root: Path) -> IngestPolicy:
    agents_path = repo_root / "AGENTS.md"
    if not agents_path.exists():
        raise IngestFailure(FailureCode.POLICY_MISSING, "AGENTS.md is required")
    claude_path = repo_root / "CLAUDE.md"
    agents_text = agents_path.read_text(encoding="utf-8")
    claude_text = claude_path.read_text(encoding="utf-8") if claude_path.exists() else ""
    warnings: list[str] = []
    if claude_path.exists() and "@AGENTS.md" not in claude_text:
        warnings.append("CLAUDE.md does not import @AGENTS.md")
    return IngestPolicy(agents_text=agents_text, claude_text=claude_text, warnings=warnings)
