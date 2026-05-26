from __future__ import annotations

import re
from pathlib import Path

from .models import FailureCode, HealthError

WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _resolve_wiki_link(wiki_root: Path, source: Path, label: str) -> Path:
    name = label.split("|", 1)[0].strip()
    if name.endswith(".md") or "/" in name:
        rel = name if name.endswith(".md") else f"{name}.md"
        return wiki_root / rel
    return wiki_root / f"{name}.md"


def lint_wiki_links(repo_root: Path, paths: list[str] | None = None) -> list[HealthError]:
    wiki_root = repo_root / "wiki"
    if paths is None:
        markdown_paths = list(wiki_root.rglob("*.md")) if wiki_root.exists() else []
    else:
        markdown_paths = [repo_root / path for path in paths if path.startswith("wiki/") and path.endswith(".md")]
    errors: list[HealthError] = []
    for source in markdown_paths:
        if not source.exists():
            continue
        text = source.read_text(encoding="utf-8")
        rel_source = source.relative_to(repo_root).as_posix()
        for match in WIKI_LINK_RE.finditer(text):
            target = _resolve_wiki_link(wiki_root, source, match.group(1))
            if not target.exists():
                errors.append(HealthError(FailureCode.BROKEN_WIKI_LINK.value, f"broken wiki link: {match.group(1)}", rel_source))
        for match in MD_LINK_RE.finditer(text):
            href = match.group(1)
            if href.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean_href = href.split("#", 1)[0]
            target = (repo_root / clean_href).resolve() if clean_href.startswith("wiki/") else (source.parent / clean_href).resolve()
            try:
                target.relative_to(repo_root.resolve())
            except ValueError:
                errors.append(HealthError(FailureCode.PATH_ESCAPE.value, f"markdown link escapes repo: {href}", rel_source))
                continue
            if clean_href and not target.exists():
                errors.append(HealthError(FailureCode.BROKEN_WIKI_LINK.value, f"broken markdown link: {href}", rel_source))
    return errors
