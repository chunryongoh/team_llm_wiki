# ML/AI Hackathon Entity Model

이 문서는 Team LLM Wiki가 ML/AI 해커톤 지식을 packet mirror가 아니라 entity graph로 유지하기 위한 기준이다. Raw packet은 source evidence이고, wiki page는 팀원이 다음 실험을 설계할 때 바로 참조할 수 있는 안정 기억이다.

## Core Rule

Experiment packet 하나가 들어오면 단순히 `wiki/experiments/<packet-id>.md`를 만드는 것으로 끝내지 않는다. 가능한 경우 아래 stable entity 중 최소 두 종류를 갱신해야 한다.

- `dataset`: 데이터셋, row identity, modality, label source, schema risk
- `benchmark`: target taxonomy, metric, split, claim boundary
- `target`: Q/S target family, target-specific bottleneck, label semantics
- `preprocessing`: split, fold, imputation, normalization, encoding, feature cutoff
- `feature`: feature family, formula, source modality, window, leakage guard, target hypothesis
- `model`: model family, objective, routing, calibration, blend, weights policy
- `performance`: local OOF, notebook-output, public/private leaderboard, official validation
- `submission`: DACON submission id, score, file lineage, local run mapping
- `decision`: adopted or rejected technical direction and rationale
- `question`: closeable backlog item with needed evidence and close condition
- `claim`: supported, tentative, disputed, or superseded statement with provenance

## Evidence Surfaces

다음 evidence surface는 절대 같은 claim처럼 병합하지 않는다.

- local OOF diagnostic
- notebook-output observation
- user-reported public score note
- DACON public leaderboard
- DACON private leaderboard
- organizer-official validation

각 성능 claim은 split name, group key, fold count, metric definition, baseline, raw evidence path가 있어야 한다. 이 정보가 없으면 `tentative` 또는 lower-boundary note로 유지한다.

## Required Registry Pages

- `wiki/claims/current-supported-claims.md`
- `wiki/submissions/dacon-leaderboard-history.md`
- `wiki/preprocessing/canonical-split-and-leakage-policy.md`

LLM synthesis는 packet 유형과 무관하게 위 세 페이지를 검토해야 한다. 변경이 없으면 "변경 없음"을 명시하고 boundary를 보존한다.

## Section07 Mapping

최근 section07 packet은 다음 stable entities로 분해해 관리한다.

- preprocessing: `wiki/preprocessing/canonical-split-and-leakage-policy.md`
- feature: `wiki/features/section07-feature-policy.md`
- model: `wiki/models/section07-mix-lgbm-catboost.md`
- submission: `wiki/submissions/dacon-leaderboard-history.md`
- decision: `wiki/decisions/section07-feature-policy-decision.md`
- question: `wiki/questions/section07-followup-backlog.md`

## Reviewer Checklist

- Packet이 어떤 stable entity를 갱신하는지 명시했는가?
- 실험 page 외에 feature/model/preprocessing/performance/decision/question 중 필요한 page가 갱신됐는가?
- 성능 claim이 evidence surface를 섞지 않는가?
- supported claim에 raw evidence와 baseline이 있는가?
- local OOF와 DACON leaderboard가 분리되어 있는가?
- 최신 `wiki/latest-context.md`가 Current Best, Active Risks, Next Actions를 보여주는가?
