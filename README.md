# Team LLM Wiki

GitHub repo를 팀 실험 지식 저장소로 쓰기 위한 LLM wiki 자동 ingest 도구입니다.

팀원이 `raw/users/<user>/<packet-id>/` 아래에 실험, 모델, feature, 성능, 회의 자료를 packet 형태로 올리면 GitHub Actions가 이를 검증하고 `wiki/`에 요약 페이지, 인덱스, 로그, 최신 컨텍스트, brief를 생성합니다.

## 핵심 구조

```text
raw/users/<user>/<packet-id>/   # 사람이 올리는 원천 증거
wiki/                           # 자동 생성/검토되는 팀 지식
automation/.cache/compiled/     # packet별 정규화 JSON
raw/shared/templates/wiki-packet/ # packet 작성 템플릿
```

- `raw/`는 source-of-truth입니다. 원천 파일은 packet 안에 두고, 자동화는 이를 증거로만 읽습니다.
- `wiki/`는 팀이 읽는 memory layer입니다. ingest가 packet을 요약해 페이지, 인덱스, 로그, 최신 컨텍스트를 갱신합니다.
- `automation/.cache/compiled/<packet-id>.json`은 LLM/agent가 안정적으로 읽을 수 있는 정규화 결과입니다.

## 설치

```bash
python -m pip install -e .[test]
```

CLI는 둘 중 편한 방식으로 실행할 수 있습니다.

```bash
team-llm-wiki --help
PYTHONPATH=src python -m team_llm_wiki.cli --help
```

## 빠른 사용법

1. 템플릿을 복사해 packet을 만듭니다.

```bash
mkdir -p raw/users/alice/example-packet
cp raw/shared/templates/wiki-packet/manifest.yaml raw/users/alice/example-packet/manifest.yaml
```

2. `manifest.yaml`과 `raw_paths`가 가리키는 packet-local 파일을 채웁니다.

```text
raw/users/alice/example-packet/
  manifest.yaml
  performance.yaml
  result.json
  folds.csv
```

3. ingest 계획을 먼저 확인합니다.

```bash
PYTHONPATH=src python -m team_llm_wiki.cli plan-wiki-main-ingest \
  --repo-root . \
  --changed-path raw/users/alice/example-packet/manifest.yaml
```

4. 실제 wiki 생성을 실행합니다.

```bash
PYTHONPATH=src python -m team_llm_wiki.cli run-wiki-main-ingest \
  --repo-root . \
  --changed-path raw/users/alice/example-packet/manifest.yaml \
  --run-id local-run
```

5. 전체 wiki 상태를 점검합니다.

```bash
PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
```

6. review-required wiki page를 GPT-5.5로 한 번 더 합성합니다.

```bash
OPENAI_API_KEY=... PYTHONPATH=src python -m team_llm_wiki.cli run-llm-wiki-synthesis \
  --repo-root . \
  --changed-path raw/users/alice/example-packet/manifest.yaml \
  --run-id local-llm-run
```

LLM synthesis는 `AGENTS.md`, `CLAUDE.md`, `wiki/latest-context.md`, packet manifest, packet-specific YAML, `packet.md`, 기존 wiki page를 모두 prompt context에 넣고 OpenAI Responses API의 `gpt-5.5`를 호출합니다. 결과는 `wiki/` page만 수정할 수 있으며 항상 review-required bot PR 대상으로 취급합니다.

## Packet 작성 규칙

새 packet은 `packet_type`을 사용합니다. 기존 호환성을 위해 legacy `type`도 읽지만 새 문서에는 `packet_type`을 권장합니다.

필수 manifest 필드:

- `id`: ASCII kebab-case, 최대 120자
- `packet_type`: `reference`, `meeting`, `experiment`, `feature`, `model`, `performance`, `preprocessing`, `augmentation`
- `title`, `date`, `owner`, `task`, `summary`
- `status`: `submitted`, `validated`, `ingested`, `rejected`, `superseded`
- `claim_status`: `tentative`, `supported`, `disputed`, `superseded`
- `dataset`, `split`, `model`
- `claim_boundary`
- `raw_paths`
- `intended_wiki_targets`

Packet별 추가 YAML:

- `preprocessing`: split, leakage guard, normalization, imputation, feature window 정책
- `feature`: feature family, source modality, formula, `leakage_risk`
- `model`: objective, hyperparameters, training/validation 전략, `weights_policy`
- `performance`: metric 정의, overall/target metrics, OOF/submission prediction, uncertainty, claim status
- `augmentation`: 생성 방식, privacy guard, label policy, validation policy

`raw_paths`가 packet-specific YAML을 가리키면 해당 파일도 packet root 안에 실제로 있어야 합니다.

## 주요 정책

### 1. Raw 증거 우선

- `raw_paths`는 packet root 밖으로 나갈 수 없습니다.
- metric 검증은 manifest 숫자를 믿지 않고 YAML/JSON raw evidence에서 `metric_key`로 다시 읽습니다.
- `split.group_key`와 `split.fold_file`이 있으면 train/validation group overlap을 검사합니다.

### 2. 보안/개인정보 차단

다음은 hard fail입니다.

- secret-like content
- PII-like content
- `.env`, private key, credential 파일명
- model weight 파일: `.bin`, `.pt`, `.pth`, `.ckpt`, `.onnx`, `.safetensors`, `.pkl`

### 3. Review 정책

자동화 결과에는 두 개의 분리된 상태가 있습니다.

- `publish_action`: 자동화가 무엇을 할지 나타냅니다. `direct_commit`, `bot_pr`, `hard_fail`
- `risk_tier`: 의미상 위험도를 나타냅니다. `tier0-catalog`부터 `tier4-governance`

기본 동작:

- `reference`, `meeting`: guard 통과 시 direct commit 가능
- `feature`, `model`, `performance`, `experiment`, `preprocessing`, `augmentation`: review가 필요한 bot PR
- `supported`, `disputed`, `superseded` claim: governance-tier로 bot PR 필요
- guard 실패, policy conflict, link lint 실패: hard fail 및 `tier4-governance`

### 4. Bot loop 방지

Bot commit/PR은 다음 prefix를 사용합니다.

- direct commit: `[wiki-bot] ingest wiki packets`
- review PR: `[wiki-bot][review-required] ingest wiki packets`

`wiki-main-ingest`는 이 prefix를 감지해 ingest loop를 피합니다. 기본 `GITHUB_TOKEN`으로 생성한 bot commit은 GitHub 정책상 후속 workflow를 트리거하지 않을 수 있습니다. bot 출력으로도 후속 workflow가 반드시 돌아야 하면 PAT 또는 GitHub App token을 써야 합니다.

## GitHub Actions

| Workflow | Trigger | 역할 |
| --- | --- | --- |
| `tests` | `push` to `main`, PR, manual | 전체 pytest 실행 |
| `wiki-main-ingest` | `main`의 `raw/users/**`, policy/schema 변경, manual | packet ingest 후 direct commit 또는 bot PR 생성 |
| `wiki-llm-synthesis` | `raw/results/wiki-ingest/**`가 main에 merge된 뒤, manual | `gpt-5.5`로 고차원 wiki synthesis를 작성하고 review-required bot PR 생성 |
| `wiki-pr-validate` | PR의 packet/policy/schema 변경 | canonical wiki를 쓰지 않고 preview comment 작성 |
| `wiki-health-check` | schedule, manual | wiki health, daily/weekly brief, stale-claim report 생성 |

PR이 없으면 `wiki-pr-validate` run history가 비어 있는 것이 정상입니다.

`wiki-llm-synthesis`를 자동 실행하려면 repo secret `OPENAI_API_KEY`가 필요합니다. secret이 없으면 workflow는 skip summary만 남기고 성공 종료합니다. 이 workflow는 deterministic ingest 결과인 `raw/results/wiki-ingest/**/report.json`에서 packet roots를 다시 찾아 읽기 때문에, raw packet merge 직후가 아니라 ingest bot PR이 merge된 뒤 고차원 합성을 수행합니다.

## 유지보수 명령

PR preview를 로컬에서 확인:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli preview-wiki-ingest \
  --repo-root . \
  --changed-path-file changed-paths.txt
```

Daily brief 생성:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli generate-wiki-brief \
  --repo-root . \
  --date "$(date -u +%F)"
```

Weekly brief와 stale claim report 생성:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli generate-wiki-weekly-brief \
  --repo-root . \
  --date "$(date -u +%F)"
```

GPT-5.5 synthesis를 수동 실행:

```bash
PYTHONPATH=src python -m team_llm_wiki.cli run-llm-wiki-synthesis \
  --repo-root . \
  --changed-path-file changed-paths.txt \
  --model gpt-5.5 \
  --reasoning-effort high
```

Brief 출력:

- daily: `wiki/briefs/<date>-daily.md`
- weekly: `wiki/briefs/<date>-weekly.md`
- stale claims: `wiki/briefs/<date>-stale-claims.md`
- latest pointer: `wiki/briefs/latest.md`

## 권장 운영 흐름

1. 팀원은 자신의 packet을 `raw/users/<user>/<packet-id>/`에 추가합니다.
2. PR에서는 `wiki-pr-validate`가 preview comment로 위험도, 누락 증거, claim status, 영향을 받는 wiki page를 보여줍니다.
3. main merge 후 `wiki-main-ingest`가 packet을 compile하고 wiki를 갱신합니다.
4. 낮은 위험도는 direct commit, review 필요 항목은 bot PR, 실패 항목은 hard fail report로 남습니다.
5. agent나 LLM은 `wiki/latest-context.md`, `wiki/index.md`, compiled JSON을 읽어 최신 팀 맥락을 가져갑니다.

## 로컬 검증

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src pytest -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m team_llm_wiki.cli check-wiki-health --repo-root .
PYTHONDONTWRITEBYTECODE=1 python -m pip install --dry-run .[test]
```
