from __future__ import annotations

from datetime import date as date_type
from pathlib import Path
import re


LOG_HEADING_RE = re.compile(r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\] .*$")


def _daily_log_entries(log_text: str, target_date: str) -> list[str]:
    entries: list[str] = []
    current: list[str] = []
    current_matches = False

    for line in log_text.splitlines():
        heading = LOG_HEADING_RE.match(line)
        if heading:
            if current_matches and current:
                entries.append("\n".join(current).strip())
            current = [line]
            current_matches = heading.group("date") == target_date
            continue
        if current_matches:
            current.append(line)

    if current_matches and current:
        entries.append("\n".join(current).strip())
    return [entry for entry in entries if entry]


def _brief_text(day: str, entries: list[str]) -> str:
    lines = [
        "---",
        f"date: {day}",
        "type: daily-brief",
        "---",
        "",
        f"# Daily Brief - {day}",
        "",
        "## New packets ingested",
        "",
    ]
    if entries:
        lines.append("\n\n".join(entries))
    else:
        lines.append("- No matching log entries found for this date.")
    lines.extend(
        [
            "",
            "## Session context",
            "",
            "- Continue from [[latest-context]].",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def generate_daily_brief(repo_root: Path, date: str | None = None) -> list[str]:
    day = date or date_type.today().isoformat()
    wiki = repo_root / "wiki"
    briefs = wiki / "briefs"
    briefs.mkdir(parents=True, exist_ok=True)

    log = wiki / "log.md"
    log_text = log.read_text(encoding="utf-8") if log.exists() else ""
    text = _brief_text(day, _daily_log_entries(log_text, day))

    dated_rel = f"wiki/briefs/{day}-daily.md"
    latest_rel = "wiki/briefs/latest.md"
    (repo_root / dated_rel).write_text(text, encoding="utf-8")
    (repo_root / latest_rel).write_text(text, encoding="utf-8")
    return [dated_rel, latest_rel]
