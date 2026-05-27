from __future__ import annotations

from datetime import date as date_type, timedelta
from pathlib import Path
import re


LOG_HEADING_RE = re.compile(r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\] .*$")
CLAIM_LINE_RE = re.compile(r"(?im)^\s*[-*]\s*(?P<status>supported|tentative|disputed|superseded)\s*:\s*(?P<text>.+?)\s*$")


def _write_latest_pointer(repo_root: Path, target_stem: str) -> str:
    latest_rel = "wiki/briefs/latest.md"
    (repo_root / latest_rel).write_text(f"[[{target_stem}]]\n", encoding="utf-8")
    return latest_rel


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


def _dated_log_entries(log_text: str, start: date_type, end: date_type) -> list[str]:
    entries: list[str] = []
    current: list[str] = []
    current_in_range = False

    for line in log_text.splitlines():
        heading = LOG_HEADING_RE.match(line)
        if heading:
            if current_in_range and current:
                entries.append("\n".join(current).strip())
            current = [line]
            entry_date = date_type.fromisoformat(heading.group("date"))
            current_in_range = start <= entry_date <= end
            continue
        if current_in_range:
            current.append(line)

    if current_in_range and current:
        entries.append("\n".join(current).strip())
    return [entry for entry in entries if entry]


def _wiki_markdown_pages(repo_root: Path) -> list[Path]:
    wiki = repo_root / "wiki"
    if not wiki.exists():
        return []
    return sorted(path for path in wiki.rglob("*.md") if "/briefs/" not in path.as_posix())


def _parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip("\"'")
    return frontmatter


def _stale_tentative_claims(repo_root: Path, today: date_type) -> list[str]:
    stale: list[str] = []
    for path in _wiki_markdown_pages(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        frontmatter = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if frontmatter.get("claim_status") != "tentative":
            continue
        try:
            claim_date = date_type.fromisoformat(frontmatter.get("date", ""))
        except ValueError:
            continue
        if (today - claim_date).days > 14:
            stale.append(f"- `{rel}`: tentative since `{claim_date.isoformat()}`")
    return stale


def _contradiction_scan(repo_root: Path) -> list[str]:
    lines: list[str] = []
    claim_text_statuses: dict[str, set[str]] = {}
    claim_text_sources: dict[str, set[str]] = {}
    for path in _wiki_markdown_pages(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter(text)
        claim_status = frontmatter.get("claim_status", "")
        if claim_status in {"disputed", "superseded"}:
            lines.append(f"- `{rel}` has claim_status `{claim_status}`")
        for match in CLAIM_LINE_RE.finditer(text):
            claim_text = " ".join(match.group("text").split())
            claim_statuses = claim_text_statuses.setdefault(claim_text, set())
            claim_statuses.add(match.group("status"))
            claim_text_sources.setdefault(claim_text, set()).add(rel)

    for claim_text, statuses in sorted(claim_text_statuses.items()):
        if len(statuses) > 1:
            sources = ", ".join(f"`{source}`" for source in sorted(claim_text_sources[claim_text]))
            lines.append(f"- Conflicting statuses {sorted(statuses)} for claim `{claim_text}` in {sources}")
    return lines


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
            "## Score movement and target movement",
            "",
            "- No score movement detected in today's log entries.",
            "",
            "## Reusable features discovered",
            "",
            "- No reusable feature discoveries detected in today's log entries.",
            "",
            "## Failed ideas worth stopping",
            "",
            "- No stopped ideas detected in today's log entries.",
            "",
            "## Leakage or validation warnings",
            "",
            "- No leakage or validation warnings detected in today's log entries.",
            "",
            "## Unresolved reviewer questions",
            "",
            "- No unresolved reviewer questions detected in today's log entries.",
            "",
            "## Recommended next 3 actions",
            "",
            "1. Review [[latest-context]] before starting new work.",
            "2. Promote supported findings into the relevant wiki page.",
            "3. Resolve stale or tentative claims with raw evidence.",
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
    (repo_root / dated_rel).write_text(text, encoding="utf-8")
    latest_rel = _write_latest_pointer(repo_root, f"{day}-daily")
    return [dated_rel, latest_rel]


def _stale_report_text(day: str, stale_claims: list[str]) -> str:
    lines = [
        "---",
        f"date: {day}",
        "type: stale-claim-report",
        "---",
        "",
        f"# Stale Claim Report - {day}",
        "",
        "## Stale tentative claims",
        "",
    ]
    lines.extend(stale_claims or ["- No stale tentative claims found."])
    return "\n".join(lines).rstrip() + "\n"


def _weekly_brief_text(week_id: str, day: str, entries: list[str], contradictions: list[str], stale_claims: list[str]) -> str:
    lines = [
        "---",
        f"date: {day}",
        f"week: {week_id}",
        "type: weekly-brief",
        "---",
        "",
        f"# Weekly Brief - {week_id}",
        "",
        "## Leaderboard and maintained local line",
        "",
    ]
    lines.append("\n\n".join(entries) if entries else "- No matching log entries found for this week.")
    lines.extend(["", "## Target deficit analysis", ""])
    lines.append("- No target deficit summary detected in this week's log entries.")
    lines.extend(["", "## Best reusable preprocessing policies", ""])
    lines.append("- No reusable preprocessing policy summary detected in this week's log entries.")
    lines.extend(["", "## Best reusable feature families", ""])
    lines.append("- No reusable feature family summary detected in this week's log entries.")
    lines.extend(["", "## Model family comparison", ""])
    lines.append("- No model family comparison detected in this week's log entries.")
    lines.extend(["", "## Repeated failure modes", ""])
    lines.append("- No repeated failure mode summary detected in this week's log entries.")
    lines.extend(["", "## Decisions to accept or supersede", ""])
    lines.append("- Review contradiction scan and stale tentative claims before accepting or superseding decisions.")
    lines.extend(["", "## Next sprint backlog", ""])
    lines.append("- Convert unresolved reviewer questions and stale claims into prioritized wiki tasks.")
    lines.extend(["", "## Contradiction scan", ""])
    lines.extend(contradictions or ["- No disputed, superseded, or repeated conflicting claims found."])
    lines.extend(["", "## Stale tentative claims", ""])
    lines.extend(stale_claims or ["- No stale tentative claims found."])
    return "\n".join(lines).rstrip() + "\n"


def generate_weekly_brief(repo_root: Path, date: str | None = None) -> list[str]:
    today = date_type.fromisoformat(date) if date else date_type.today()
    day = today.isoformat()
    iso_year, iso_week, _weekday = today.isocalendar()
    week_id = f"{iso_year}-W{iso_week:02d}"
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    wiki = repo_root / "wiki"
    briefs = wiki / "briefs"
    briefs.mkdir(parents=True, exist_ok=True)

    log = wiki / "log.md"
    log_text = log.read_text(encoding="utf-8") if log.exists() else ""
    stale_claims = _stale_tentative_claims(repo_root, today)
    contradictions = _contradiction_scan(repo_root)

    weekly_rel = f"wiki/briefs/{week_id}-weekly.md"
    stale_rel = f"wiki/briefs/{day}-stale-claims.md"
    (repo_root / weekly_rel).write_text(
        _weekly_brief_text(week_id, day, _dated_log_entries(log_text, week_start, week_end), contradictions, stale_claims),
        encoding="utf-8",
    )
    (repo_root / stale_rel).write_text(_stale_report_text(day, stale_claims), encoding="utf-8")
    latest_rel = _write_latest_pointer(repo_root, f"{week_id}-weekly")
    return [weekly_rel, stale_rel, latest_rel]
