# Team LLM Wiki Packet Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the standalone `team-llm-wiki-packet` skill in `chunryongoh/team-llm-wiki-packet-skill`, install it locally, and verify through a subagent-run smoke test that it can create a real raw packet PR against `team_llm_wiki`.

**Architecture:** The skill lives outside `team_llm_wiki` and treats that repo as a target. The skill uses markdown-first packet creation with helper-generated `manifest.yaml`, optional structured evidence for performance/experiment claims, deterministic Python helper scripts, JSON failure contracts, markdown safety scanning, fixture-based self-tests, and PR-first upload. Final verification is done by a fresh subagent that installs the skill and runs it against a disposable clone of `team_llm_wiki`, including an actual GitHub PR smoke test that is closed after validation.

**Tech Stack:** Codex Skills (`SKILL.md`, `agents/openai.yaml`, `references/`), Python 3.11+ standard library helper scripts, `unittest`, `git`, `gh`, existing `team_llm_wiki` CLI for target repo validation.

---

## Source Documents

- Spec: `/home/chunoh/ETRI/team_llm_wiki/docs/superpowers/specs/2026-05-28-team-llm-wiki-packet-skill-design.md`
- CEO plan: `/home/chunoh/.gstack/projects/team_llm_wiki/ceo-plans/2026-05-28-team-llm-wiki-packet-skill.md`
- Target repo: `/home/chunoh/ETRI/team_llm_wiki`
- Skill source repo path: `/home/chunoh/ETRI/team-llm-wiki-packet-skill`
- Skill source remote: `https://github.com/chunryongoh/team-llm-wiki-packet-skill`
- Local install path: `/home/chunoh/.codex/skills/team-llm-wiki-packet`

## Scope Check

This plan deliberately creates a separate skill repository. It must not add implementation files under `/home/chunoh/ETRI/team_llm_wiki`. The only permitted modifications in `team_llm_wiki` during this plan are plan/spec/report/log updates made before implementation. The skill itself, helper scripts, fixtures, and tests live in `/home/chunoh/ETRI/team-llm-wiki-packet-skill`.

The implementation has four linked units:

1. Standalone skill package and references.
2. Deterministic helper scripts and failure contracts.
3. Fixture-based self-tests.
4. Subagent-run installation and real packet PR smoke verification.

These units are tightly coupled for v1 because the user explicitly requires the plan to verify installation and real packet creation, not just produce a skill folder.

## File Structure

Create this repository:

```text
/home/chunoh/ETRI/team-llm-wiki-packet-skill/
  .gitignore
  pyproject.toml
  SKILL.md
  agents/
    openai.yaml
  references/
    packet-types.md
    interview-prompts.md
    claim-calibration.md
    github-upload.md
  scripts/
    __init__.py
    packet_skill_common.py
    make_packet_draft.py
    render_packet.py
    preview_packet.py
    upload_packet_pr.py
    install_local.py
  fixtures/
    minimal-target-repo/
      AGENTS.md
      CLAUDE.md
      wiki/
        index.md
        latest-context.md
        team/
          wiki-ingest-policy.md
          contribution-workflow.md
      raw/
        shared/
          templates/
            wiki-packet/
              README.md
              manifest.yaml
    examples/
      markdown-meeting-packet/
        answers.json
      markdown-feature-hypothesis/
        answers.json
      structured-performance-packet/
        answers.json
        metrics.json
      unsafe-secret-packet/
        answers.json
      unsupported-performance-claim/
        answers.json
  tests/
    test_common.py
    test_make_packet_draft.py
    test_render_packet.py
    test_preview_packet.py
    test_upload_packet_pr.py
    test_end_to_end_fixtures.py
```

Responsibility split:

- `SKILL.md`: short procedural workflow loaded by AI assistants.
- `references/*.md`: detailed interview prompts, packet type rules, claim calibration, upload policy.
- `packet_skill_common.py`: shared JSON output, slug/path validation, YAML rendering, frontmatter parsing, safety scanning, subprocess helpers.
- `make_packet_draft.py`: converts interview answers into a normalized draft contract. It never writes packet files.
- `render_packet.py`: renders approved drafts into `packet.md`, `manifest.yaml`, and optional structured files under the target repo.
- `preview_packet.py`: bounded deterministic preview with blocks, warnings, files, validation commands.
- `upload_packet_pr.py`: stages only approved packet files, commits, pushes a branch, and opens a PR.
- `install_local.py`: installs the standalone skill into `/home/chunoh/.codex/skills/team-llm-wiki-packet`.
- `fixtures/`: self-test target repo and example inputs.
- `tests/`: unittest coverage for all helper scripts and fixture flows.

## Implementation Tasks

### Task 1: Create Standalone Repo Skeleton

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/.gitignore`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/pyproject.toml`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/SKILL.md`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/agents/openai.yaml`

- [ ] **Step 1: Create the repo directory and initialize git**

Run:

```bash
mkdir -p /home/chunoh/ETRI/team-llm-wiki-packet-skill
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git init
```

Expected: `Initialized empty Git repository` or `Reinitialized existing Git repository`.

- [ ] **Step 2: Write `.gitignore`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/.gitignore`:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
.DS_Store
.venv/
dist/
build/
*.egg-info/
.skill-smoke/
```

- [ ] **Step 3: Write `pyproject.toml`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/pyproject.toml`:

```toml
[project]
name = "team-llm-wiki-packet-skill"
version = "0.1.0"
description = "Standalone Codex skill for creating Team LLM Wiki raw packets"
requires-python = ">=3.11"
dependencies = []

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

- [ ] **Step 4: Write `SKILL.md`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/SKILL.md`:

```markdown
---
name: team-llm-wiki-packet
description: Use when a teammate wants to turn ML/DL work, experiment results, features, preprocessing notes, model configuration, performance metrics, meeting notes, or references into a validated Team LLM Wiki raw packet and open a GitHub pull request. Interviews the user as an ML/DL research expert, creates a markdown-first packet with explicit approval, validates locally, commits only approved raw packet files, and opens a PR.
---

# Team LLM Wiki Packet

Use this skill to create raw packets for a Team LLM Wiki target repository. This skill is standalone. Do not implement skill files inside the target repository.

## Start

1. Confirm the target repo root. If not specified, use the current working directory only when it contains `AGENTS.md`, `wiki/`, and `raw/shared/templates/wiki-packet/manifest.yaml`.
2. Read target repo context:
   - `AGENTS.md`
   - `CLAUDE.md` when present
   - `wiki/latest-context.md` when present
   - `wiki/index.md`
   - `wiki/team/wiki-ingest-policy.md`
   - `wiki/team/contribution-workflow.md`
   - `raw/shared/templates/wiki-packet/README.md`
   - `raw/shared/templates/wiki-packet/manifest.yaml`
3. Read only the reference file needed for the packet type:
   - `references/packet-types.md`
   - `references/interview-prompts.md`
   - `references/claim-calibration.md`
   - `references/github-upload.md`

## Interview Rules

- Act as an ML/DL research interviewer, not a form filler.
- Ask one high-signal question at a time.
- Prefer multiple-choice questions when the choices are known.
- Default to markdown-first packets.
- Require structured mode for performance, experiment, supported/disputed/superseded claims, metric comparisons, or split-sensitive claims.
- Use `tentative` when evidence is incomplete.
- Do not write files until preview is shown and the user explicitly approves.

## Packet Modes

Markdown-first mode creates:

```text
packet.md
manifest.yaml
```

Structured mode creates:

```text
packet.md
manifest.yaml
<type-specific>.yaml
<raw evidence files>
```

## Helper Flow

Use helper scripts from this skill directory:

1. `scripts/make_packet_draft.py` to normalize interview answers into a draft contract.
2. `scripts/render_packet.py` to render approved draft files under `raw/users/...`.
3. `scripts/preview_packet.py` to show bounded preview, safety warnings, and validation commands.
4. `scripts/upload_packet_pr.py` to stage only approved packet files, commit, push, and open a PR.

Every helper returns JSON with `ok: true` or `ok: false`. On failure, show the `code`, `message`, and `recovery` to the user. Do not parse free-form stderr for control flow.

## Approval Gate

Before writing or uploading, show:

- target packet path
- packet mode
- file list
- claim status
- claim boundary
- markdown safety blocks and warnings
- validation commands
- git branch and PR title

Ask:

```text
이 preview대로 packet을 생성하고 GitHub PR을 열까요?

A. 승인 - 생성, 검증, commit/push/PR 진행
B. 수정 - 특정 항목 수정 후 다시 preview
C. 중단 - 파일을 만들지 않음
```

## Upload Rules

- PR-first is the default.
- Direct push to `main` requires explicit user confirmation.
- Do not commit generated `wiki/` files.
- Do not commit unrelated dirty files.
- Do not store model weights, secrets, private keys, credential files, or PII-like artifacts.
```

- [ ] **Step 5: Write `agents/openai.yaml`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/agents/openai.yaml`:

```yaml
display_name: Team LLM Wiki Packet
short_description: Interview-driven raw packet creation for Team LLM Wiki repos.
default_prompt: Create a validated Team LLM Wiki packet from my latest research notes and open a PR.
```

- [ ] **Step 6: Commit the scaffold**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add .gitignore pyproject.toml SKILL.md agents/openai.yaml
git commit -m "chore: scaffold packet skill"
```

Expected: commit succeeds with four tracked files.

### Task 2: Add References for Interview and Policy

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/packet-types.md`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/interview-prompts.md`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/claim-calibration.md`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/github-upload.md`

- [ ] **Step 1: Write `packet-types.md`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/packet-types.md`:

```markdown
# Packet Types

Valid packet types:

- `meeting`: meeting notes, decisions, open questions
- `reference`: papers, blog posts, external source notes
- `feature`: feature hypotheses or feature family evidence
- `model`: model configuration, objective, validation strategy
- `preprocessing`: split, normalization, imputation, leakage guard notes
- `augmentation`: synthetic data, SMOTE, LLM data generation notes
- `experiment`: one run with dataset, split, model, features, logs, metrics
- `performance`: metric comparison, leaderboard, OOF, confusion matrix, baseline comparison

Default mode:

- `meeting`, `reference`, early `feature`, and early `model` notes use `markdown_first`.
- `performance`, `experiment`, supported/disputed/superseded claims, metric comparisons, and split-sensitive claims use `structured`.

Routes used by the target repo:

- `reference`, `meeting` -> `wiki/sources/<id>.md`
- `experiment` -> `wiki/experiments/<id>.md`
- `feature` -> `wiki/features/<id>.md`
- `model` -> `wiki/models/<id>.md`
- `performance` -> `wiki/performance/<id>.md`
- `preprocessing`, `augmentation` -> `wiki/datasets/<id>.md`
```

- [ ] **Step 2: Write `interview-prompts.md`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/interview-prompts.md`:

```markdown
# Interview Prompts

Ask one question at a time.

## First Question

```text
어떤 종류의 packet으로 만들까요?

A. performance - metric, leaderboard, OOF, confusion matrix, baseline comparison
B. experiment - one run with dataset, split, model, feature set, logs, interpretation
C. feature - feature family, formula, leakage risk, hypothesis, evidence
D. model - architecture, objective, validation strategy, hyperparameters, inference contract
E. preprocessing - split, normalization, imputation, leakage guard, row identity
F. augmentation - synthetic data, SMOTE, LLM generation, validation policy
G. meeting/reference - meeting note, paper, blog, external source, decision evidence
```

## Performance Questions

- 어떤 split에서 나온 metric인가요?
- baseline은 무엇이고 같은 split인가요?
- metric은 raw YAML/JSON에서 재검증 가능한가요?
- target별로 악화된 항목이 있나요?
- public LB, OOF, local validation 중 어느 결과인가요?
- claim status는 `tentative`, `supported`, `disputed`, `superseded` 중 무엇인가요?

## Experiment Questions

- run id는 무엇인가요?
- dataset version과 split은 무엇인가요?
- model family와 feature set은 무엇인가요?
- training command, notebook, log가 있나요?
- baseline과 새 결과는 무엇인가요?
- 이 run에서 실제로 배운 점은 무엇인가요?
- 다음 action은 무엇인가요?

## Feature Questions

- feature family 이름은 무엇인가요?
- target과 연결되는 가설은 무엇인가요?
- formula, anchor, window는 무엇인가요?
- leakage risk는 low, medium, high 중 무엇인가요?
- SHAP, ablation, target-wise gain 중 근거가 있나요?

## Meeting or Reference Questions

- 출처나 회의 provenance는 무엇인가요?
- 결정, 가설, 검증된 사실을 분리할 수 있나요?
- follow-up owner가 있나요?
- 관련 packet이나 실험이 있나요?
```

- [ ] **Step 3: Write `claim-calibration.md`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/claim-calibration.md`:

```markdown
# Claim Calibration

Use explicit claim status:

- `tentative`: plausible, early, incomplete, or not fully verified
- `supported`: backed by raw evidence and valid split/metric context
- `disputed`: conflicting evidence exists
- `superseded`: replaced by newer evidence

Default to `tentative` when evidence is incomplete.

Useful claim boundaries:

- `local_oof_diagnostic_only`
- `same_split_baseline_comparison`
- `public_lb_observation_only`
- `meeting_decision_not_experimentally_verified`
- `feature_hypothesis_pending_ablation`
- `reference_summary_not_project_verified`

Never write "best model" as a supported claim unless the user provides metric evidence, split, baseline, and validation context.
```

- [ ] **Step 4: Write `github-upload.md`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/references/github-upload.md`:

```markdown
# GitHub Upload

Default upload flow:

1. Create a packet branch.
2. Stage only approved packet files.
3. Commit with `data: add <packet-id> wiki packet`.
4. Push the branch.
5. Open a GitHub PR.

Do not commit generated `wiki/` files.
Do not commit unrelated dirty files.
Direct push to `main` requires explicit user confirmation.

Smoke-test PRs use:

- branch prefix: `skill-smoke/`
- PR title prefix: `[skill-smoke]`
- close after validation unless the user asks to keep it open
```

- [ ] **Step 5: Commit references**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add references
git commit -m "docs: add packet skill references"
```

Expected: commit succeeds with four reference files.

### Task 3: Implement Shared Helper Library

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/__init__.py`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/packet_skill_common.py`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_common.py`

- [ ] **Step 1: Write failing common helper tests**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_common.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from scripts.packet_skill_common import (
    Failure,
    extract_frontmatter,
    packet_route,
    render_yaml,
    scan_markdown_safety,
    slugify,
    success,
)


class CommonTests(unittest.TestCase):
    def test_slugify_returns_ascii_kebab_case(self):
        self.assertEqual(slugify("LGB + CB Seed Ensemble!!"), "lgb-cb-seed-ensemble")

    def test_packet_route_matches_target_repo_routes(self):
        self.assertEqual(packet_route("meeting", "demo"), "wiki/sources/demo.md")
        self.assertEqual(packet_route("performance", "demo"), "wiki/performance/demo.md")

    def test_render_yaml_supports_nested_manifest(self):
        rendered = render_yaml({"id": "demo", "dataset": {"name": "none", "version": "none"}, "raw_paths": {"notes": "packet.md"}})
        self.assertIn("id: demo\n", rendered)
        self.assertIn("dataset:\n  name: none\n  version: none\n", rendered)
        self.assertIn("raw_paths:\n  notes: packet.md\n", rendered)

    def test_extract_frontmatter_reads_yaml_like_header(self):
        frontmatter, body = extract_frontmatter("---\npacket_type: meeting\nowner: alice\n---\n# Body\n")
        self.assertEqual(frontmatter["packet_type"], "meeting")
        self.assertEqual(frontmatter["owner"], "alice")
        self.assertEqual(body.strip(), "# Body")

    def test_scan_markdown_safety_blocks_absolute_local_path(self):
        result = scan_markdown_safety("Evidence at /home/alice/private/result.csv\n")
        self.assertFalse(result["ok"])
        self.assertEqual(result["blocks"][0]["code"], "unsafe_local_path")

    def test_scan_markdown_safety_warns_unsupported_best_claim(self):
        result = scan_markdown_safety("This is the best model so far.\n")
        self.assertTrue(result["ok"])
        self.assertEqual(result["warnings"][0]["code"], "unsupported_performance_claim")

    def test_json_success_contract(self):
        payload = success({"path": "packet.md"})
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["outputs"]["path"], "packet.md")

    def test_failure_contract_shape(self):
        failure = Failure("invalid_draft", "Draft invalid", "Ask again", {"field": "owner"})
        payload = failure.to_json()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["code"], "invalid_draft")
        self.assertEqual(payload["details"]["field"], "owner")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_common -v
```

Expected: FAIL with `ModuleNotFoundError` or missing functions.

- [ ] **Step 3: Create helper module**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/__init__.py` as an empty file.

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/packet_skill_common.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
import subprocess
from typing import Any


PACKET_TYPES = {
    "reference",
    "meeting",
    "experiment",
    "feature",
    "model",
    "performance",
    "preprocessing",
    "augmentation",
}

CLAIM_STATUSES = {"tentative", "supported", "disputed", "superseded"}

ROUTES = {
    "reference": "wiki/sources",
    "meeting": "wiki/sources",
    "experiment": "wiki/experiments",
    "feature": "wiki/features",
    "model": "wiki/models",
    "performance": "wiki/performance",
    "preprocessing": "wiki/datasets",
    "augmentation": "wiki/datasets",
}


@dataclass
class Failure:
    code: str
    message: str
    recovery: str
    details: dict[str, Any] | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "ok": False,
            "code": self.code,
            "message": self.message,
            "recovery": self.recovery,
            "details": self.details or {},
        }


def success(outputs: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "outputs": outputs}


def failure(code: str, message: str, recovery: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return Failure(code, message, recovery, details).to_json()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or "packet"


def packet_route(packet_type: str, packet_id: str) -> str:
    if packet_type not in ROUTES:
        raise ValueError(f"unsupported packet type: {packet_type}")
    return f"{ROUTES[packet_type]}/{packet_id}.md"


def render_yaml(data: Any, indent: int = 0) -> str:
    spaces = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{spaces}{key}:")
                lines.append(render_yaml(value, indent + 2).rstrip())
            else:
                lines.append(f"{spaces}{key}: {yaml_scalar(value)}")
        return "\n".join(lines) + "\n"
    if isinstance(data, list):
        if not data:
            return f"{spaces}[]\n"
        lines = []
        for value in data:
            if isinstance(value, (dict, list)):
                lines.append(f"{spaces}-")
                lines.append(render_yaml(value, indent + 2).rstrip())
            else:
                lines.append(f"{spaces}- {yaml_scalar(value)}")
        return "\n".join(lines) + "\n"
    return f"{spaces}{yaml_scalar(data)}\n"


def yaml_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or text.strip() != text or any(ch in text for ch in [":", "#", "{", "}", "[", "]", ",", "\n"]):
        return json.dumps(text, ensure_ascii=False)
    return text


def extract_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown
    end = markdown.find("\n---\n", 4)
    if end == -1:
        return {}, markdown
    raw = markdown[4:end]
    body = markdown[end + 5 :]
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values, body


def scan_markdown_safety(markdown: str, max_chars: int = 20000) -> dict[str, Any]:
    blocks: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if len(markdown) > max_chars:
        blocks.append({"code": "oversized_markdown", "message": "packet.md exceeds configured review size."})
    if re.search(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*[A-Za-z0-9_\-]{12,}", markdown):
        blocks.append({"code": "secret_like_content", "message": "Secret-like credential text found."})
    if re.search(r"(?m)(/home/[^\\s)]+|[A-Za-z]:\\\\[^\\s)]+)", markdown):
        blocks.append({"code": "unsafe_local_path", "message": "Absolute local path found."})
    if re.search(r"(?i)(ignore previous instructions|reveal secrets|override policy|modify generated wiki)", markdown):
        blocks.append({"code": "prompt_injection_phrase", "message": "Prompt-injection-like phrase found."})
    if re.search(r"(?i)\\b(model weights|\\.safetensors|\\.ckpt|\\.pth|\\.pt|\\.onnx|\\.pkl)\\b", markdown):
        blocks.append({"code": "model_weight_reference", "message": "Model weight reference found."})
    if re.search(r"(?i)\\b(best model|optimal model|performance improved|score improved)\\b", markdown):
        warnings.append({"code": "unsupported_performance_claim", "message": "Performance-strength wording should be evidenced or tentative."})
    if re.search(r"(?i)\\b(decided|agreed)\\b", markdown) and re.search(r"(?i)\\b(proves|verified|confirmed)\\b", markdown):
        warnings.append({"code": "meeting_claim_as_fact", "message": "Meeting decision may be phrased as verified fact."})
    return {"ok": not blocks, "blocks": blocks, "warnings": warnings}


def ensure_inside(parent: Path, child: Path) -> None:
    child.resolve().relative_to(parent.resolve())


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
```

- [ ] **Step 4: Run common tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_common -v
```

Expected: PASS.

- [ ] **Step 5: Commit common helpers**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add scripts/__init__.py scripts/packet_skill_common.py tests/test_common.py
git commit -m "feat: add packet skill common helpers"
```

Expected: commit succeeds.

### Task 4: Add Draft Helper

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/make_packet_draft.py`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_make_packet_draft.py`

- [ ] **Step 1: Write failing draft tests**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_make_packet_draft.py`:

```python
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_packet_draft.py"


class MakePacketDraftTests(unittest.TestCase):
    def test_markdown_meeting_draft(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "target"
            (repo / "raw/shared/templates/wiki-packet").mkdir(parents=True)
            (repo / "wiki/team").mkdir(parents=True)
            (repo / "AGENTS.md").write_text("rules", encoding="utf-8")
            (repo / "wiki/index.md").write_text("# index\n", encoding="utf-8")
            (repo / "wiki/team/wiki-ingest-policy.md").write_text("policy", encoding="utf-8")
            (repo / "raw/shared/templates/wiki-packet/manifest.yaml").write_text("id: example\n", encoding="utf-8")
            answers = Path(temp) / "answers.json"
            answers.write_text(json.dumps({
                "owner": "alice",
                "packet_type": "meeting",
                "title": "Packet skill kickoff",
                "date": "2026-05-28",
                "summary": "Discussed packet skill operation.",
                "body": "Decision: create a standalone packet skill.",
                "claim_status": "tentative",
                "claim_boundary": "meeting_decision_not_experimentally_verified"
            }), encoding="utf-8")

            result = subprocess.run(
                ["python", str(SCRIPT), "--target-repo", str(repo), "--answers", str(answers)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            draft = payload["outputs"]["draft"]
            self.assertEqual(draft["mode"], "markdown_first")
            self.assertEqual(draft["id"], "2026-05-28-packet-skill-kickoff")
            self.assertEqual(draft["packet_root"], "raw/users/alice/meetings/2026-05-28-packet-skill-kickoff")

    def test_supported_meeting_claim_requires_structured_or_downgrade(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "target"
            (repo / "raw/shared/templates/wiki-packet").mkdir(parents=True)
            (repo / "wiki/team").mkdir(parents=True)
            (repo / "AGENTS.md").write_text("rules", encoding="utf-8")
            (repo / "wiki/index.md").write_text("# index\n", encoding="utf-8")
            (repo / "wiki/team/wiki-ingest-policy.md").write_text("policy", encoding="utf-8")
            (repo / "raw/shared/templates/wiki-packet/manifest.yaml").write_text("id: example\n", encoding="utf-8")
            answers = Path(temp) / "answers.json"
            answers.write_text(json.dumps({
                "owner": "alice",
                "packet_type": "meeting",
                "title": "Best model",
                "date": "2026-05-28",
                "summary": "Best model found.",
                "body": "This proves the best model.",
                "claim_status": "supported",
                "claim_boundary": "meeting_decision_not_experimentally_verified"
            }), encoding="utf-8")

            result = subprocess.run(
                ["python", str(SCRIPT), "--target-repo", str(repo), "--answers", str(answers)],
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["code"], "structured_required")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_make_packet_draft -v
```

Expected: FAIL because `make_packet_draft.py` does not exist.

- [ ] **Step 3: Implement `make_packet_draft.py`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/make_packet_draft.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from packet_skill_common import CLAIM_STATUSES, PACKET_TYPES, failure, packet_route, slugify, success


CATEGORY_DIRS = {
    "meeting": "meetings",
    "reference": "references",
    "experiment": "experiments",
    "feature": "features",
    "model": "models",
    "performance": "performance",
    "preprocessing": "preprocessing",
    "augmentation": "augmentation",
}


STRUCTURED_TYPES = {"performance", "experiment"}
STRONG_STATUSES = {"supported", "disputed", "superseded"}


def repo_context_missing(repo: Path) -> list[str]:
    required = [
        "AGENTS.md",
        "wiki/index.md",
        "wiki/team/wiki-ingest-policy.md",
        "raw/shared/templates/wiki-packet/manifest.yaml",
    ]
    return [path for path in required if not (repo / path).exists()]


def build_draft(target_repo: Path, answers: dict) -> dict:
    missing = repo_context_missing(target_repo)
    if missing:
        return failure("missing_repo_context", "Target repo is missing required wiki context.", "Point the skill at a Team LLM Wiki repo.", {"missing": missing})
    packet_type = answers.get("packet_type")
    if packet_type not in PACKET_TYPES:
        return failure("invalid_packet_type", "Packet type is absent or unsupported.", "Re-ask packet triage with valid packet types.", {"packet_type": packet_type})
    owner = str(answers.get("owner", "")).strip()
    if not owner or slugify(owner) != owner:
        return failure("invalid_owner", "Owner must be a non-empty ASCII kebab-case slug.", "Ask for the GitHub handle or owner slug.", {"owner": owner})
    claim_status = answers.get("claim_status", "tentative")
    if claim_status not in CLAIM_STATUSES:
        return failure("unsupported_claim_status", "Claim status is unsupported.", "Re-ask claim calibration.", {"claim_status": claim_status})
    if packet_type not in STRUCTURED_TYPES and claim_status in STRONG_STATUSES:
        return failure("structured_required", "Strong claims require structured mode.", "Ask for evidence or downgrade claim status to tentative.", {"packet_type": packet_type, "claim_status": claim_status})
    title = str(answers.get("title", "")).strip()
    date = str(answers.get("date", "")).strip()
    if not title or not date:
        return failure("invalid_draft", "Title and date are required.", "Ask for title and date.", {})
    packet_id = f"{date}-{slugify(title)}"
    category = CATEGORY_DIRS[packet_type]
    mode = "structured" if packet_type in STRUCTURED_TYPES else "markdown_first"
    draft = {
        "id": packet_id,
        "mode": mode,
        "owner": owner,
        "packet_type": packet_type,
        "title": title,
        "date": date,
        "summary": str(answers.get("summary", "")).strip() or title,
        "body": str(answers.get("body", "")).strip() or str(answers.get("summary", "")).strip() or title,
        "claim_status": claim_status,
        "claim_boundary": str(answers.get("claim_boundary", "reference_summary_not_project_verified")).strip(),
        "task": str(answers.get("task", "team-llm-wiki-packet")).strip(),
        "dataset": answers.get("dataset", {"name": "not-applicable", "version": "not-applicable"}),
        "split": answers.get("split", {"name": "none"}),
        "model": answers.get("model", {"family": "not-applicable", "weights_in_repo": False}),
        "packet_root": f"raw/users/{owner}/{category}/{packet_id}",
        "intended_wiki_targets": [packet_route(packet_type, packet_id)],
        "structured": answers.get("structured", {}),
    }
    return success({"draft": draft})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repo", required=True)
    parser.add_argument("--answers", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    target_repo = Path(args.target_repo)
    answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    payload = build_draft(target_repo, answers)
    if args.output and payload.get("ok"):
        Path(args.output).write_text(json.dumps(payload["outputs"]["draft"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run draft tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_make_packet_draft -v
```

Expected: PASS.

- [ ] **Step 5: Commit draft helper**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add scripts/make_packet_draft.py tests/test_make_packet_draft.py
git commit -m "feat: add packet draft helper"
```

Expected: commit succeeds.

### Task 5: Implement Render Helper

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/render_packet.py`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_render_packet.py`

- [ ] **Step 1: Write failing render tests**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_render_packet.py`:

```python
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_packet.py"


class RenderPacketTests(unittest.TestCase):
    def test_markdown_first_packet_renders_packet_and_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "target"
            repo.mkdir()
            draft = Path(temp) / "draft.json"
            draft.write_text(json.dumps({
                "id": "2026-05-28-packet-skill-kickoff",
                "mode": "markdown_first",
                "owner": "alice",
                "packet_type": "meeting",
                "title": "Packet skill kickoff",
                "date": "2026-05-28",
                "summary": "Discussed packet skill operation.",
                "body": "Decision: create a standalone packet skill.",
                "claim_status": "tentative",
                "claim_boundary": "meeting_decision_not_experimentally_verified",
                "task": "team-llm-wiki-packet",
                "dataset": {"name": "not-applicable", "version": "not-applicable"},
                "split": {"name": "none"},
                "model": {"family": "not-applicable", "weights_in_repo": False},
                "packet_root": "raw/users/alice/meetings/2026-05-28-packet-skill-kickoff",
                "intended_wiki_targets": ["wiki/sources/2026-05-28-packet-skill-kickoff.md"],
                "structured": {}
            }), encoding="utf-8")

            result = subprocess.run(
                ["python", str(SCRIPT), "--target-repo", str(repo), "--draft", str(draft)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            packet_root = repo / "raw/users/alice/meetings/2026-05-28-packet-skill-kickoff"
            self.assertTrue((packet_root / "packet.md").is_file())
            self.assertTrue((packet_root / "manifest.yaml").is_file())
            manifest = (packet_root / "manifest.yaml").read_text(encoding="utf-8")
            self.assertIn("packet_type: meeting\n", manifest)
            self.assertIn("notes: packet.md\n", manifest)

    def test_render_rejects_unsafe_markdown(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "target"
            repo.mkdir()
            draft = Path(temp) / "draft.json"
            draft.write_text(json.dumps({
                "id": "2026-05-28-secret",
                "mode": "markdown_first",
                "owner": "alice",
                "packet_type": "meeting",
                "title": "Secret",
                "date": "2026-05-28",
                "summary": "Secret",
                "body": "api_key = abcdefghijklmnop",
                "claim_status": "tentative",
                "claim_boundary": "meeting_decision_not_experimentally_verified",
                "task": "team-llm-wiki-packet",
                "dataset": {"name": "not-applicable", "version": "not-applicable"},
                "split": {"name": "none"},
                "model": {"family": "not-applicable", "weights_in_repo": False},
                "packet_root": "raw/users/alice/meetings/2026-05-28-secret",
                "intended_wiki_targets": ["wiki/sources/2026-05-28-secret.md"],
                "structured": {}
            }), encoding="utf-8")
            result = subprocess.run(
                ["python", str(SCRIPT), "--target-repo", str(repo), "--draft", str(draft)],
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["code"], "markdown_safety_block")

    def test_structured_performance_packet_renders_metric_files(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "target"
            repo.mkdir()
            draft = Path(temp) / "draft.json"
            draft.write_text(json.dumps({
                "id": "2026-05-28-lgb-cb-smoke-metric",
                "mode": "structured",
                "owner": "alice",
                "packet_type": "performance",
                "title": "LGB CB Smoke Metric",
                "date": "2026-05-28",
                "summary": "Structured performance smoke packet.",
                "body": "OOF metric smoke result with raw metric evidence.",
                "claim_status": "tentative",
                "claim_boundary": "local_oof_diagnostic_only",
                "task": "team-llm-wiki-packet",
                "dataset": {"name": "not-applicable", "version": "not-applicable"},
                "split": {"name": "oof"},
                "model": {"family": "lightgbm-catboost", "weights_in_repo": False},
                "packet_root": "raw/users/alice/performance/2026-05-28-lgb-cb-smoke-metric",
                "intended_wiki_targets": ["wiki/performance/2026-05-28-lgb-cb-smoke-metric.md"],
                "structured": {
                    "primary_metric": "macro_log_loss",
                    "overall_metrics": {"macro_log_loss": 0.42}
                }
            }), encoding="utf-8")

            result = subprocess.run(
                ["python", str(SCRIPT), "--target-repo", str(repo), "--draft", str(draft)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            packet_root = repo / "raw/users/alice/performance/2026-05-28-lgb-cb-smoke-metric"
            self.assertTrue((packet_root / "packet.md").is_file())
            self.assertTrue((packet_root / "manifest.yaml").is_file())
            self.assertTrue((packet_root / "performance.yaml").is_file())
            self.assertTrue((packet_root / "metrics.json").is_file())
            manifest = (packet_root / "manifest.yaml").read_text(encoding="utf-8")
            self.assertIn("performance: performance.yaml\n", manifest)
            self.assertIn("metrics: metrics.json\n", manifest)
            self.assertIn("metric_key: overall_metrics.macro_log_loss\n", manifest)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run render tests to verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_render_packet -v
```

Expected: FAIL because `render_packet.py` does not exist.

- [ ] **Step 3: Implement `render_packet.py`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/render_packet.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from packet_skill_common import ensure_inside, failure, read_json, render_yaml, scan_markdown_safety, success


def packet_markdown(draft: dict) -> str:
    frontmatter = {
        "packet_type": draft["packet_type"],
        "owner": draft["owner"],
        "date": draft["date"],
        "claim_status": draft["claim_status"],
        "summary": draft["summary"],
    }
    body = [
        "---",
        *[f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in frontmatter.items()],
        "---",
        "",
        f"# {draft['title']}",
        "",
        "## Summary",
        "",
        draft["summary"],
        "",
        "## Notes",
        "",
        draft["body"],
        "",
        "## Claim Boundary",
        "",
        draft["claim_boundary"],
        "",
    ]
    return "\n".join(body)


def performance_payload(draft: dict) -> dict:
    structured = draft.get("structured", {})
    return {
        "primary_metric": structured.get("primary_metric"),
        "overall_metrics": structured.get("overall_metrics", {}),
        "target_metrics": structured.get("target_metrics", {}),
        "baseline": structured.get("baseline", {}),
        "notes": structured.get("notes", ""),
    }


def metrics_payload(draft: dict) -> dict:
    structured = draft.get("structured", {})
    return {
        "overall_metrics": structured.get("overall_metrics", {}),
        "target_metrics": structured.get("target_metrics", {}),
    }


def manifest_payload(draft: dict) -> dict:
    raw_paths = {"notes": "packet.md"}
    metrics_to_verify = list(draft.get("metrics_to_verify", []))
    if draft.get("mode") == "structured" and draft.get("packet_type") == "performance":
        raw_paths["performance"] = "performance.yaml"
        raw_paths["metrics"] = "metrics.json"
        primary_metric = draft.get("structured", {}).get("primary_metric")
        overall_metrics = draft.get("structured", {}).get("overall_metrics", {})
        if primary_metric and primary_metric in overall_metrics:
            metrics_to_verify.append({
                "raw_path": "metrics.json",
                "metric_key": f"overall_metrics.{primary_metric}",
                "reported_value": overall_metrics[primary_metric],
                "tolerance": 0.0,
            })
    elif draft.get("mode") == "structured":
        raw_paths["evidence"] = "evidence.yaml"
    return {
        "id": draft["id"],
        "packet_type": draft["packet_type"],
        "title": draft["title"],
        "date": draft["date"],
        "owner": draft["owner"],
        "status": "submitted",
        "task": draft["task"],
        "dataset": draft["dataset"],
        "split": draft["split"],
        "model": draft["model"],
        "claim_boundary": draft["claim_boundary"],
        "claim_status": draft["claim_status"],
        "summary": draft["summary"],
        "raw_paths": raw_paths,
        "intended_wiki_targets": draft["intended_wiki_targets"],
        "metrics_to_verify": metrics_to_verify,
        "claims": [{"status": draft["claim_status"], "text": draft["summary"]}],
    }


def render_packet(target_repo: Path, draft: dict) -> dict:
    packet_root = target_repo / draft["packet_root"]
    try:
        ensure_inside(target_repo / "raw" / "users", packet_root)
    except ValueError:
        return failure("unsafe_packet_path", "Packet path escapes raw/users.", "Regenerate owner/type/slug.", {"packet_root": draft.get("packet_root")})
    if packet_root.exists():
        return failure("packet_already_exists", "Packet root already exists.", "Choose a new packet title or slug.", {"packet_root": draft["packet_root"]})
    markdown = packet_markdown(draft)
    safety = scan_markdown_safety(markdown)
    if safety["blocks"]:
        return failure("markdown_safety_block", "Markdown safety hard block found.", "Edit packet text before preview/upload.", safety)
    packet_root.mkdir(parents=True)
    (packet_root / "packet.md").write_text(markdown, encoding="utf-8")
    created_names = ["packet.md"]
    if draft.get("mode") == "structured" and draft.get("packet_type") == "performance":
        (packet_root / "performance.yaml").write_text(render_yaml(performance_payload(draft)), encoding="utf-8")
        (packet_root / "metrics.json").write_text(json.dumps(metrics_payload(draft), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        created_names.extend(["performance.yaml", "metrics.json"])
    elif draft.get("mode") == "structured":
        (packet_root / "evidence.yaml").write_text(render_yaml(draft.get("structured", {})), encoding="utf-8")
        created_names.append("evidence.yaml")
    (packet_root / "manifest.yaml").write_text(render_yaml(manifest_payload(draft)), encoding="utf-8")
    created_names.append("manifest.yaml")
    created = [str((packet_root / name).relative_to(target_repo)) for name in created_names]
    return success({"packet_root": draft["packet_root"], "created_files": created, "warnings": safety["warnings"], "changed_paths": [f"{draft['packet_root']}/manifest.yaml"]})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repo", required=True)
    parser.add_argument("--draft", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    payload = render_packet(Path(args.target_repo), read_json(Path(args.draft)))
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run render tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_render_packet -v
```

Expected: PASS.

- [ ] **Step 5: Commit render helper**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add scripts/render_packet.py tests/test_render_packet.py
git commit -m "feat: render wiki packet files"
```

Expected: commit succeeds.

### Task 6: Add Preview Helper

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/preview_packet.py`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_preview_packet.py`

- [ ] **Step 1: Write failing preview tests**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_preview_packet.py`:

```python
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "preview_packet.py"


class PreviewPacketTests(unittest.TestCase):
    def test_preview_contains_required_sections(self):
        with tempfile.TemporaryDirectory() as temp:
            draft = Path(temp) / "draft.json"
            render = Path(temp) / "render.json"
            draft.write_text(json.dumps({
                "id": "demo",
                "mode": "markdown_first",
                "packet_type": "meeting",
                "claim_status": "tentative",
                "claim_boundary": "meeting_decision_not_experimentally_verified",
                "packet_root": "raw/users/alice/meetings/demo"
            }), encoding="utf-8")
            render.write_text(json.dumps({
                "ok": True,
                "outputs": {
                    "created_files": ["raw/users/alice/meetings/demo/packet.md", "raw/users/alice/meetings/demo/manifest.yaml"],
                    "warnings": [],
                    "changed_paths": ["raw/users/alice/meetings/demo/manifest.yaml"]
                }
            }), encoding="utf-8")
            result = subprocess.run(["python", str(SCRIPT), "--draft", str(draft), "--render-result", str(render)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            preview = payload["outputs"]["preview"]
            self.assertIn("Packet preview", preview)
            self.assertIn("raw/users/alice/meetings/demo", preview)
            self.assertIn("claim_status: tentative", preview)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run preview tests to verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_preview_packet -v
```

Expected: FAIL because `preview_packet.py` does not exist.

- [ ] **Step 3: Implement `preview_packet.py`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/preview_packet.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from packet_skill_common import failure, read_json, success


def build_preview(draft: dict, render_result: dict) -> dict:
    if not render_result.get("ok"):
        return failure("preview_missing_required_section", "Render result is not successful.", "Fix render failure before preview.", {})
    outputs = render_result.get("outputs", {})
    required = ["created_files", "changed_paths"]
    missing = [key for key in required if key not in outputs]
    if missing:
        return failure("preview_missing_required_section", "Preview lacks required render sections.", "Regenerate render output.", {"missing": missing})
    warnings = outputs.get("warnings", [])
    lines = [
        "Packet preview",
        "",
        f"Mode: {draft.get('mode')}",
        f"Target path: {draft.get('packet_root')}",
        "",
        "Files:",
        *[f"- {path}" for path in outputs["created_files"]],
        "",
        f"claim_status: {draft.get('claim_status')}",
        f"claim_boundary: {draft.get('claim_boundary')}",
        "",
        "Markdown safety warnings:",
        *([f"- {item.get('code')}: {item.get('message')}" for item in warnings] or ["- none"]),
        "",
        "Validation commands:",
        f"- PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m team_llm_wiki.cli plan-wiki-main-ingest --repo-root . --changed-path {outputs['changed_paths'][0]}",
        "- PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .",
    ]
    return success({"preview": "\n".join(lines) + "\n", "warnings": warnings})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", required=True)
    parser.add_argument("--render-result", required=True)
    args = parser.parse_args(argv)
    payload = build_preview(read_json(Path(args.draft)), read_json(Path(args.render_result)))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run preview tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_preview_packet -v
```

Expected: PASS.

- [ ] **Step 5: Commit preview helper**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add scripts/preview_packet.py tests/test_preview_packet.py
git commit -m "feat: add packet preview helper"
```

Expected: commit succeeds.

### Task 7: Add PR Upload Helper

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/upload_packet_pr.py`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_upload_packet_pr.py`

- [ ] **Step 1: Write failing upload safety tests**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_upload_packet_pr.py`:

```python
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "upload_packet_pr.py"


class UploadPacketPrTests(unittest.TestCase):
    def test_no_packet_files_fails_before_git_actions(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            result = subprocess.run(
                ["python", str(SCRIPT), "--target-repo", str(repo), "--packet-root", "raw/users/alice/meetings/demo", "--branch", "skill-smoke/demo", "--commit-message", "data: add demo wiki packet", "--dry-run"],
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["code"], "no_packet_files")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run upload tests to verify they fail**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_upload_packet_pr -v
```

Expected: FAIL because `upload_packet_pr.py` does not exist.

- [ ] **Step 3: Implement `upload_packet_pr.py`**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/upload_packet_pr.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from packet_skill_common import failure, run_command, success


def upload_packet_pr(target_repo: Path, packet_root: str, branch: str, commit_message: str, pr_title: str, pr_body: str, dry_run: bool) -> dict:
    root = target_repo / packet_root
    if not root.exists() or not any(root.iterdir()):
        return failure("no_packet_files", "No approved packet files are present to commit.", "Run render_packet.py before upload.", {"packet_root": packet_root})
    files = sorted(path.relative_to(target_repo).as_posix() for path in root.rglob("*") if path.is_file())
    if not files:
        return failure("no_packet_files", "No approved packet files are present to commit.", "Run render_packet.py before upload.", {"packet_root": packet_root})
    status = run_command(["git", "status", "--porcelain"], target_repo)
    unrelated = [line for line in status.stdout.splitlines() if line and not line[3:].startswith(packet_root + "/")]
    if unrelated:
        return failure("dirty_worktree_conflict", "Unrelated dirty files are present.", "Commit or stash unrelated files before packet upload.", {"unrelated": unrelated})
    if dry_run:
        return success({"packet_files": files, "branch": branch, "dry_run": True})
    checkout = run_command(["git", "checkout", "-b", branch], target_repo)
    if checkout.returncode != 0:
        return failure("branch_exists", "Packet branch already exists or cannot be created.", "Reuse branch or generate a new branch suffix.", {"stderr": checkout.stderr})
    add = run_command(["git", "add", *files], target_repo)
    if add.returncode != 0:
        return failure("unexpected_staged_files", "Failed to stage approved packet files.", "Inspect git status and retry.", {"stderr": add.stderr})
    commit = run_command(["git", "commit", "-m", commit_message], target_repo)
    if commit.returncode != 0:
        return failure("commit_failed", "Git commit failed.", "Leave files in place and report the git error.", {"stderr": commit.stderr})
    push = run_command(["git", "push", "-u", "origin", branch], target_repo)
    if push.returncode != 0:
        return failure("push_failed", "Branch push failed.", "Retry push after fixing remote/auth.", {"stderr": push.stderr})
    gh = run_command(["gh", "pr", "create", "--title", pr_title, "--body", pr_body], target_repo)
    if gh.returncode != 0:
        return failure("pr_create_failed", "GitHub PR creation failed.", "Run gh pr create manually from the pushed branch.", {"stderr": gh.stderr, "branch": branch})
    return success({"packet_files": files, "branch": branch, "pr_url": gh.stdout.strip()})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-repo", required=True)
    parser.add_argument("--packet-root", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--commit-message", required=True)
    parser.add_argument("--pr-title", default="[packet] add wiki packet")
    parser.add_argument("--pr-body", default="Created by team-llm-wiki-packet skill.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = upload_packet_pr(Path(args.target_repo), args.packet_root, args.branch, args.commit_message, args.pr_title, args.pr_body, args.dry_run)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run upload tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_upload_packet_pr -v
```

Expected: PASS.

- [ ] **Step 5: Commit upload helper**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add scripts/upload_packet_pr.py tests/test_upload_packet_pr.py
git commit -m "feat: add PR-first upload helper"
```

Expected: commit succeeds.

### Task 8: Add Fixtures and End-to-End Self-Tests

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/fixtures/minimal-target-repo/...`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/fixtures/examples/...`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_end_to_end_fixtures.py`

- [ ] **Step 1: Create minimal target repo fixture**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
mkdir -p fixtures/minimal-target-repo/wiki/team
mkdir -p fixtures/minimal-target-repo/raw/shared/templates/wiki-packet
printf '%s\n' '# Fixture Agent Rules' '- Treat raw as evidence.' > fixtures/minimal-target-repo/AGENTS.md
printf '%s\n' '@AGENTS.md' > fixtures/minimal-target-repo/CLAUDE.md
printf '%s\n' '# Fixture Wiki Index' > fixtures/minimal-target-repo/wiki/index.md
printf '%s\n' '# Latest Context' > fixtures/minimal-target-repo/wiki/latest-context.md
printf '%s\n' '# Policy' 'Packets require manifest.yaml.' > fixtures/minimal-target-repo/wiki/team/wiki-ingest-policy.md
printf '%s\n' '# Workflow' 'Add packets under raw/users.' > fixtures/minimal-target-repo/wiki/team/contribution-workflow.md
printf '%s\n' '# Template' > fixtures/minimal-target-repo/raw/shared/templates/wiki-packet/README.md
printf '%s\n' 'id: example' 'packet_type: meeting' > fixtures/minimal-target-repo/raw/shared/templates/wiki-packet/manifest.yaml
```

Expected: fixture files exist.

- [ ] **Step 2: Create example answer payloads**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
mkdir -p fixtures/examples/markdown-meeting-packet fixtures/examples/unsafe-secret-packet fixtures/examples/unsupported-performance-claim fixtures/examples/structured-performance-packet
cat > fixtures/examples/markdown-meeting-packet/answers.json <<'JSON'
{
  "owner": "codex-smoke",
  "packet_type": "meeting",
  "title": "Skill Smoke Meeting",
  "date": "2026-05-28",
  "summary": "Smoke test for markdown-first packet creation.",
  "body": "Decision: verify standalone skill packet creation.",
  "claim_status": "tentative",
  "claim_boundary": "meeting_decision_not_experimentally_verified"
}
JSON
cat > fixtures/examples/unsafe-secret-packet/answers.json <<'JSON'
{
  "owner": "codex-smoke",
  "packet_type": "meeting",
  "title": "Unsafe Secret",
  "date": "2026-05-28",
  "summary": "Unsafe packet.",
  "body": "api_key = abcdefghijklmnop",
  "claim_status": "tentative",
  "claim_boundary": "meeting_decision_not_experimentally_verified"
}
JSON
cat > fixtures/examples/unsupported-performance-claim/answers.json <<'JSON'
{
  "owner": "codex-smoke",
  "packet_type": "meeting",
  "title": "Best Model Note",
  "date": "2026-05-28",
  "summary": "This is the best model so far.",
  "body": "This is the best model so far, pending evidence.",
  "claim_status": "tentative",
  "claim_boundary": "meeting_decision_not_experimentally_verified"
}
JSON
cat > fixtures/examples/structured-performance-packet/answers.json <<'JSON'
{
  "owner": "codex-smoke",
  "packet_type": "performance",
  "title": "LGB CB Smoke Metric",
  "date": "2026-05-28",
  "summary": "Structured performance smoke packet.",
  "body": "OOF metric smoke result with raw metric evidence.",
  "claim_status": "tentative",
  "claim_boundary": "local_oof_diagnostic_only",
  "structured": {
    "primary_metric": "macro_log_loss",
    "overall_metrics": {"macro_log_loss": 0.42}
  }
}
JSON
cat > fixtures/examples/structured-performance-packet/metrics.json <<'JSON'
{
  "overall_metrics": {"macro_log_loss": 0.42}
}
JSON
```

Expected: four `answers.json` files and one structured `metrics.json` fixture exist.

- [ ] **Step 3: Write end-to-end tests**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_end_to_end_fixtures.py`:

```python
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "scripts" / "make_packet_draft.py"
RENDER = ROOT / "scripts" / "render_packet.py"
PREVIEW = ROOT / "scripts" / "preview_packet.py"


class EndToEndFixtureTests(unittest.TestCase):
    def test_markdown_fixture_draft_render_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target"
            shutil.copytree(ROOT / "fixtures/minimal-target-repo", target)
            answers = ROOT / "fixtures/examples/markdown-meeting-packet/answers.json"
            draft_path = Path(temp) / "draft.json"
            render_path = Path(temp) / "render.json"

            draft = subprocess.run(["python", str(DRAFT), "--target-repo", str(target), "--answers", str(answers), "--output", str(draft_path)], text=True, capture_output=True, check=False)
            self.assertEqual(draft.returncode, 0, draft.stderr)

            render = subprocess.run(["python", str(RENDER), "--target-repo", str(target), "--draft", str(draft_path), "--output", str(render_path)], text=True, capture_output=True, check=False)
            self.assertEqual(render.returncode, 0, render.stderr)

            preview = subprocess.run(["python", str(PREVIEW), "--draft", str(draft_path), "--render-result", str(render_path)], text=True, capture_output=True, check=False)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            payload = json.loads(preview.stdout)
            self.assertIn("Packet preview", payload["outputs"]["preview"])

    def test_structured_performance_fixture_renders_metrics_files(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target"
            shutil.copytree(ROOT / "fixtures/minimal-target-repo", target)
            answers = ROOT / "fixtures/examples/structured-performance-packet/answers.json"
            draft_path = Path(temp) / "draft.json"
            render_path = Path(temp) / "render.json"

            draft = subprocess.run(["python", str(DRAFT), "--target-repo", str(target), "--answers", str(answers), "--output", str(draft_path)], text=True, capture_output=True, check=False)
            self.assertEqual(draft.returncode, 0, draft.stderr)

            render = subprocess.run(["python", str(RENDER), "--target-repo", str(target), "--draft", str(draft_path), "--output", str(render_path)], text=True, capture_output=True, check=False)
            self.assertEqual(render.returncode, 0, render.stderr)
            packet_root = target / "raw/users/codex-smoke/performance/2026-05-28-lgb-cb-smoke-metric"
            self.assertTrue((packet_root / "performance.yaml").is_file())
            self.assertTrue((packet_root / "metrics.json").is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run all tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit fixtures and self-tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add fixtures tests/test_end_to_end_fixtures.py
git commit -m "test: add packet skill fixtures"
```

Expected: commit succeeds.

### Task 9: Add Local Install Script

**Files:**
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/install_local.py`
- Create: `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_install_local.py`

- [ ] **Step 1: Write failing install test**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/tests/test_install_local.py`:

```python
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install_local.py"


class InstallLocalTests(unittest.TestCase):
    def test_install_copies_skill_files(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "skill"
            result = subprocess.run(["python", str(SCRIPT), "--source", str(Path(__file__).resolve().parents[1]), "--dest", str(dest)], text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertTrue((dest / "scripts/render_packet.py").is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Implement install script**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/install_local.py`:

```python
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


INCLUDE = ["SKILL.md", "agents", "references", "scripts"]


def install(source: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in INCLUDE:
        src = source / name
        target = dest / name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        if src.is_dir():
            ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
            shutil.copytree(src, target, ignore=ignore)
        else:
            shutil.copy2(src, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--dest", default=str(Path.home() / ".codex" / "skills" / "team-llm-wiki-packet"))
    args = parser.parse_args(argv)
    install(Path(args.source), Path(args.dest))
    print(f"installed team-llm-wiki-packet to {args.dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run install tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest tests.test_install_local -v
```

Expected: PASS.

- [ ] **Step 4: Install locally from source**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python scripts/install_local.py --source /home/chunoh/ETRI/team-llm-wiki-packet-skill --dest /home/chunoh/.codex/skills/team-llm-wiki-packet
test -f /home/chunoh/.codex/skills/team-llm-wiki-packet/SKILL.md
```

Expected: `installed team-llm-wiki-packet to /home/chunoh/.codex/skills/team-llm-wiki-packet` and `test` exits 0.

- [ ] **Step 5: Commit install script**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add scripts/install_local.py tests/test_install_local.py
git commit -m "feat: add local skill installer"
```

Expected: commit succeeds.

### Task 10: Create GitHub Source Repository and Push

**Files:**
- Remote repo: `chunryongoh/team-llm-wiki-packet-skill`

- [ ] **Step 1: Confirm GitHub auth**

Run:

```bash
gh auth status
```

Expected: authenticated to `github.com` as an account with permission to create repos under `chunryongoh`.

- [ ] **Step 2: Create or attach remote**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
if gh repo view chunryongoh/team-llm-wiki-packet-skill >/dev/null 2>&1; then
  git remote remove origin 2>/dev/null || true
  git remote add origin https://github.com/chunryongoh/team-llm-wiki-packet-skill.git
else
  gh repo create chunryongoh/team-llm-wiki-packet-skill --private --source . --remote origin
fi
```

Expected: remote `origin` points to `https://github.com/chunryongoh/team-llm-wiki-packet-skill.git`.

- [ ] **Step 3: Push main**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git branch -M main
git push -u origin main
```

Expected: push succeeds and GitHub repo contains the skill.

- [ ] **Step 4: Verify cloneability**

Run:

```bash
rm -rf /tmp/team-llm-wiki-packet-skill-clone
git clone https://github.com/chunryongoh/team-llm-wiki-packet-skill.git /tmp/team-llm-wiki-packet-skill-clone
test -f /tmp/team-llm-wiki-packet-skill-clone/SKILL.md
```

Expected: clone succeeds and `SKILL.md` exists.

### Task 11: Subagent Verification With Local Install and Real Packet Creation

**Files:**
- Uses installed skill at `/home/chunoh/.codex/skills/team-llm-wiki-packet`
- Uses target repo clone under `/tmp/team-llm-wiki-skill-smoke`
- Creates transient branch and PR in `chunryongoh/team_llm_wiki`

This task is mandatory. It verifies what the user requested: a fresh subagent installs the skill, runs it, and confirms an actual packet can be made.

- [ ] **Step 1: Dispatch a worker subagent for smoke verification**

Spawn a worker subagent with this exact prompt:

```text
You are a verification worker. You are not alone in the codebase. Do not edit /home/chunoh/ETRI/team_llm_wiki or /home/chunoh/ETRI/team-llm-wiki-packet-skill source files.

Task:
1. Clone https://github.com/chunryongoh/team_llm_wiki.git into /tmp/team-llm-wiki-skill-smoke, replacing any existing directory.
2. Clone or use /home/chunoh/ETRI/team-llm-wiki-packet-skill as the skill source.
3. Install the skill to /home/chunoh/.codex/skills/team-llm-wiki-packet by running:
   python /home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/install_local.py --source /home/chunoh/ETRI/team-llm-wiki-packet-skill --dest /home/chunoh/.codex/skills/team-llm-wiki-packet
4. In /tmp/team-llm-wiki-skill-smoke, create a markdown-first meeting packet using the installed helper scripts:
   - owner: codex-smoke
   - packet_type: meeting
   - title: Skill Smoke Meeting
   - date: 2026-05-28
   - claim_status: tentative
   - claim_boundary: meeting_decision_not_experimentally_verified
5. Run the installed helper scripts explicitly:
   - /home/chunoh/.codex/skills/team-llm-wiki-packet/scripts/make_packet_draft.py
   - /home/chunoh/.codex/skills/team-llm-wiki-packet/scripts/render_packet.py
   - /home/chunoh/.codex/skills/team-llm-wiki-packet/scripts/preview_packet.py
6. Install the target repo dependencies with:
   python -m pip install -e .[test]
7. Run:
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m team_llm_wiki.cli plan-wiki-main-ingest --repo-root . --changed-path raw/users/codex-smoke/meetings/2026-05-28-skill-smoke-meeting/manifest.yaml
8. Run:
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
9. Use upload_packet_pr.py to create a real smoke branch and PR:
   branch: skill-smoke/2026-05-28-packet-skill
   title: [skill-smoke] verify packet skill
   body: Smoke PR created by team-llm-wiki-packet verification. Do not merge.
10. Wait for GitHub PR validation if a workflow starts. Record the PR URL and workflow status.
11. Close the smoke PR and delete the remote branch:
   gh pr close <PR_URL> --repo chunryongoh/team_llm_wiki --delete-branch
12. Final report must include:
   - installed skill path
   - generated packet root
   - created files
   - local validation outputs
   - PR URL
   - whether PR was closed and branch deleted
   - any failure code encountered

Do not merge the smoke PR.
```

Expected: worker returns a report proving the skill installed and generated a valid packet in the target repo clone, plus a transient PR URL that was closed.

- [ ] **Step 2: Review subagent output**

Check the worker report for all required fields:

```text
installed skill path: /home/chunoh/.codex/skills/team-llm-wiki-packet
generated packet root: raw/users/codex-smoke/meetings/2026-05-28-skill-smoke-meeting
created files:
- packet.md
- manifest.yaml
local validation: plan-wiki-main-ingest ok, check-wiki-health ok
PR URL: https://github.com/chunryongoh/team_llm_wiki/pull/<number>
PR cleanup: closed, branch deleted
failure code: none
```

If any field is missing, send the worker one follow-up asking for the missing evidence. Do not mark this task complete until the smoke verification is evidenced.

- [ ] **Step 3: Fix any smoke failure in the skill source repo**

If the worker reports a helper failure, fix the skill source repo using the failure code:

```text
invalid_draft -> update make_packet_draft.py or tests
markdown_safety_block -> update fixture text or safety scanner
frontmatter_manifest_mismatch -> update render_packet.py
dirty_worktree_conflict -> update upload_packet_pr.py staging logic
pr_create_failed -> update upload_packet_pr.py recovery output
```

Run the focused failing test and then full tests:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest discover -s tests -v
```

Expected: PASS before rerunning the subagent smoke test.

- [ ] **Step 4: Commit smoke-related fixes**

Run only if Step 3 changed files:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git status --short
git add scripts tests fixtures
git commit -m "fix: pass packet skill smoke verification"
git push origin main
```

Expected: commit and push succeed.

### Task 12: Final Verification and Handoff

**Files:**
- Verify: `/home/chunoh/ETRI/team-llm-wiki-packet-skill`
- Verify: `/home/chunoh/.codex/skills/team-llm-wiki-packet`
- Verify: GitHub repo `chunryongoh/team-llm-wiki-packet-skill`

- [ ] **Step 1: Run full skill tests**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Reinstall local skill from source**

Run:

```bash
python /home/chunoh/ETRI/team-llm-wiki-packet-skill/scripts/install_local.py \
  --source /home/chunoh/ETRI/team-llm-wiki-packet-skill \
  --dest /home/chunoh/.codex/skills/team-llm-wiki-packet
test -f /home/chunoh/.codex/skills/team-llm-wiki-packet/SKILL.md
test -f /home/chunoh/.codex/skills/team-llm-wiki-packet/scripts/render_packet.py
```

Expected: install succeeds and both `test` commands exit 0.

- [ ] **Step 3: Confirm GitHub source is current**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git status --short --branch
git log --oneline -5
git push origin main
```

Expected: branch is not behind remote; push reports `Everything up-to-date` or pushes the latest commit.

- [ ] **Step 4: Record final smoke evidence**

Create `/home/chunoh/ETRI/team-llm-wiki-packet-skill/SMOKE_RESULT.md` with this shape, using the actual subagent evidence:

```markdown
# Smoke Result

Date: 2026-05-28

## Local Install

- Installed path: `/home/chunoh/.codex/skills/team-llm-wiki-packet`
- Source repo: `https://github.com/chunryongoh/team-llm-wiki-packet-skill`

## Target Repo Verification

- Target clone: `/tmp/team-llm-wiki-skill-smoke`
- Packet root: `raw/users/codex-smoke/meetings/2026-05-28-skill-smoke-meeting`
- Created files:
  - `packet.md`
  - `manifest.yaml`

## Validation

- `plan-wiki-main-ingest`: passed
- `check-wiki-health`: passed

## GitHub PR Smoke

- PR URL: `<actual closed smoke PR URL>`
- PR status: closed without merge
- Remote branch: deleted

## Notes

- Failure code encountered: none
```

The `<actual closed smoke PR URL>` token must be replaced with a real URL before committing.

- [ ] **Step 5: Commit final smoke evidence**

Run:

```bash
cd /home/chunoh/ETRI/team-llm-wiki-packet-skill
git add SMOKE_RESULT.md
git commit -m "test: record packet skill smoke verification"
git push origin main
```

Expected: commit and push succeed.

## Self-Review Checklist

Spec coverage:

- Standalone packaging: Task 1, Task 10, Task 12.
- Separate repo source: Task 10.
- Local install path: Task 9, Task 12.
- Markdown-first packet: Task 4, Task 5, Task 8, Task 11.
- Minimal manifest compatibility: Task 5, Task 8, Task 11.
- Structured path: Task 5 renders `performance.yaml` and `metrics.json`; Task 8 verifies structured performance fixtures.
- Helper failure contracts: Task 3 through Task 7.
- Markdown safety gate: Task 3 and Task 5.
- PR-first upload: Task 7 and Task 11.
- Fixture self-tests: Task 8.
- Subagent install and actual packet verification: Task 11.

No placeholder patterns:

- The plan uses concrete file paths.
- The plan includes exact commands.
- The plan includes exact test bodies for each helper.
- The plan names failure codes and recovery paths.

Type consistency:

- Packet mode uses `markdown_first` and `structured`.
- Packet type values match target repo enum values.
- Claim status values match target repo values.
- Upload helper uses `packet_root`, `branch`, `commit_message`, `pr_title`, and `pr_body`.

## Execution Handoff

Use **Subagent-Driven** execution.

Implementation rule:

- Dispatch one worker per task for Tasks 1-10 where practical.
- Task 11 must be a fresh verification worker with no implementation ownership.
- The verification worker must install the skill and create an actual smoke packet PR against `chunryongoh/team_llm_wiki`, then close it without merging.
- Review after each worker returns before dispatching the next worker.

Do not use inline execution for Task 11. The whole point is to test that a fresh agent can install and operate the skill.
