# Wiki Packet Template

수동 packet 작성용 템플릿입니다. 일반 팀원은 가능하면 `team-llm-wiki-packet` skill을 사용하세요.

packet은 항상 아래 경로에 둡니다.

```text
raw/users/<owner>/<category>/<date-slug>/
```

## 기본 파일

```text
manifest.yaml
packet.md
<packet-specific>.yaml
metrics.json 또는 evidence 파일
wiki_plan.yaml
```

`manifest.yaml`의 `raw_paths`가 가리키는 파일은 모두 packet 폴더 안에 있어야 합니다.

## Packet type

| Type | Wiki route |
| --- | --- |
| `reference`, `meeting` | `wiki/sources/` |
| `experiment` | `wiki/experiments/` |
| `feature` | `wiki/features/` |
| `model` | `wiki/models/` |
| `performance` | `wiki/performance/` |
| `preprocessing`, `augmentation`, `dataset` | `wiki/datasets/` |
| `benchmark` | `wiki/benchmarks/` |

## 주의

- `raw/`는 원천 증거입니다. packet 제출 후 임의 수정하지 않습니다.
- `wiki_plan.yaml`은 stable entity, affected page, open question, semantic lint를 제안하는 파일입니다.
- local OOF, notebook output, DACON public LB, private LB, official validation은 서로 다른 근거입니다.
- 제출 파일/hash, private score, 팀 재현 근거가 없으면 leaderboard claim은 보통 `tentative`입니다.
- skill이 만든 scratch 파일은 보통 `/tmp/team-llm-wiki-packet-work/<packet-id>/`에 두고 commit하지 않습니다.
