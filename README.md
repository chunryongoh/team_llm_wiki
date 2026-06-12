# Team LLM Wiki

ETRI/DACON 수면 건강 해커톤 팀의 공유 지식 저장소입니다.

팀원은 `wiki/`를 직접 고치지 않고, 자신의 실험 결과를 `raw/users/**` packet PR로 올립니다. 이후 GitHub Actions가 검증하고 GPT-5.5가 팀 wiki로 정리합니다.

## 흐름

```mermaid
flowchart LR
    A["팀원 실험/노트"] --> B["packet skill"]
    B --> C["raw/users/** PR"]
    C --> D["PR preview"]
    D --> E["wiki-main-ingest"]
    E --> F["ingest bot PR"]
    F --> G["wiki-llm-synthesis<br/>GPT-5.5"]
    G --> H["synthesis bot PR"]
    H --> I["최신 wiki"]
```

| 단계 | 역할 |
| --- | --- |
| Packet PR | 팀원이 raw evidence와 claim boundary 제출 |
| Ingest bot PR | packet을 deterministic하게 검증/정규화 |
| Synthesis bot PR | GPT-5.5가 기존 wiki와 통합 |

## Canonical Wiki Structure

Durable wiki pages live in these namespaces:

```text
wiki/preprocessing
wiki/features
wiki/models
wiki/performance
wiki/claims
wiki/targets
wiki/decisions
wiki/reports
wiki/team
```

Deprecated namespaces such as `wiki/datasets`, `wiki/benchmarks`, `wiki/questions`, `wiki/submissions`, `wiki/experiments`, and `wiki/sources` are compatibility-only. New packet PRs and bot outputs must not create substantive pages there.

## 팀원이 할 일

1. packet skill을 설치합니다.
2. skill 인터뷰로 실험/모델/feature/성능을 packet화합니다.
3. `raw/users/<owner>/<category>/<date-slug>/`만 수정하는 PR을 올립니다.
4. preview comment에서 위험도, 누락 증거, 영향을 받을 wiki page를 확인합니다.
5. merge 후 생성되는 ingest/synthesis bot PR을 리뷰합니다.

Packet skill:

```text
https://github.com/chunryongoh/team-llm-wiki-packet-skill
```

```bash
git clone https://github.com/chunryongoh/team-llm-wiki-packet-skill.git
team-llm-wiki-packet-skill/install.sh --verify
```

## AI가 먼저 읽을 파일

팀원이 Codex, Claude, Cursor 등을 사용할 때는 최신 `main`을 받은 뒤 아래 순서로 읽게 합니다.

```text
AGENTS.md
wiki/latest-context.md
wiki/index.md
관련 wiki page
필요 시 raw evidence 또는 automation/.cache/compiled/*.json
```

예시:

```bash
git clone https://github.com/chunryongoh/team_llm_wiki.git .team_context/team_llm_wiki
git -C .team_context/team_llm_wiki pull --ff-only
```

```text
.team_context/team_llm_wiki/AGENTS.md,
wiki/latest-context.md, wiki/index.md를 먼저 읽고
최신 팀 맥락을 반영해줘.
```

## 핵심 규칙

- `raw/`는 원천 증거입니다. 임의 수정하지 않습니다.
- `wiki/`는 팀이 읽는 지식층입니다. packet 복붙이 아니라 stable entity 중심으로 정리합니다.
- local OOF, notebook output, DACON public LB, private LB, official validation은 서로 다른 근거입니다.
- public LB 기록은 제출 파일/hash, private score, 팀 재현 근거가 없으면 보통 `tentative`입니다.
- 중요한 판단은 chat에만 남기지 말고 wiki로 되돌립니다.

## 주요 경로

```text
raw/users/**                  팀원이 올리는 packet
wiki/latest-context.md         최신 팀 맥락
wiki/index.md                  wiki 목차
wiki/team/                     운영 정책
automation/.cache/compiled/    packet별 정규화 JSON
raw/results/wiki-ingest/       ingest report
raw/results/llm-synthesis/     synthesis report
```

상세 문서:

- [LLM Wiki Operating Harness](wiki/team/llm-wiki-operating-harness.md)
- [Page Taxonomy](wiki/team/page-taxonomy.md)
- [Contribution Workflow](wiki/team/contribution-workflow.md)

## 검증

```bash
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
```

최근 검증 사례: DACON `Public 0.5917 LGBM+XGB anchor` packet PR `#47` -> ingest PR `#48` -> synthesis PR `#49`.
