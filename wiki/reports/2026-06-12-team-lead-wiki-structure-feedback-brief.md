---
id: team-lead-wiki-structure-feedback-brief-20260612
type: report
page_role: report
status: draft
title: Team Lead Wiki Structure Feedback Brief
date: "2026-06-12"
source: team-lead-wiki-structure-review_shs260612.md
---

# Team Lead Wiki Structure Feedback Brief

## 핵심 결론

팀장 피드백의 방향은 명확하다.

현재 구조는 LLM wiki 관점에서는 체계적이지만, 실제 팀원이 쓰기에는 복잡하다. 초기 운영은 핵심 디렉토리 중심으로 단순화하고, 세부 실험 로그와 반복적으로 변하는 정보는 stable page에 계속 누적하지 말고 report, log, versioned summary로 흡수한다.

Wiki는 모든 실험 기록을 복붙하는 공간이 아니라 팀이 현재 믿고 있는 결론, target별 병목, feature/model/performance 방향, 중요한 결정의 근거를 관리하는 지식층이어야 한다.

## 유지할 핵심 구조

- `latest-context.md`: 유지하되 version header 또는 최신본 기록을 쉽게 추적할 수 있게 수정.
- `index.md`: 유지. 길어지지 않게 관리하고, 필요하면 hash/code 기반 route를 고려.
- `overview.md`: 수정. 한 줄 요약과 최신본 링크 중심으로 아주 짧게 유지.
- `preprocessing/`: 수정. raw 검수, filtering, cleaning, NaN removal, warping, label별 feature 개발 계획까지 feature 생성 전 과정을 간략히 기록.
- `features/`: 수정. feature family, 전체 feature 수, raw feature source, feature selection 유무만 핵심으로 기록. 전체 feature list는 별도 저장 후 링크.
- `models/`: 수정. 모델 종류, architecture, 큰 flow, 구성상 특이점 중심. 반복되는 hyperparameter/weight 변화는 제외.
- `performance/`: 수정. local validation 근거와 external leaderboard 근거를 구분해 기록. SHAP 분석이 있으면 의미 있는 feature 중심으로 요약 가능.
- `claims/`: 유지. supported claim은 raw evidence, validation metric, feature/model hash, 실험 조건이 모두 확인된 경우에만 허용.
- `targets/`: 유지. Q1-S4 각 target별 병목, feature family, model strategy, performance issue를 stable leaf로 관리.
- `decisions/`: 유지. 팀 방향을 바꾸는 결정은 ADR에 가깝게 기록하고, 승인자와 날짜를 남김.
- `reports/`: 수정. feature, preprocessing, model, performance, claim/decision 요약을 보여주는 versioned summary 역할.
- `team/`: 수정. 팀원용 onboarding 문서와 agent/자동화용 정책 문서를 분리.

## 삭제 또는 병합 방향

- `datasets/`: 별도 운영 삭제. 데이터는 고정이므로 초기 설정만 남기고 필요한 내용은 preprocessing 또는 model/performance 쪽에서 참조.
- `benchmarks/`: 별도 운영 삭제. 큰 의미가 낮다고 판단.
- `submissions/`: `performance/`와 병합.
- `questions/`: 초기에는 삭제. 질문은 target 또는 report 내부 open issue로 관리하고, 쌓이면 나중에 본격 운영.
- `experiments/`: reports 또는 versioned summary와 통합.
- `sources/`: 별도 운영 삭제. 외부 자료는 필요한 경우 feature/model/performance에 흡수.
- `briefs/`: 삭제. report로 갈음.

## 운영 정책 변화

1. 팀원이 stable wiki page를 직접 수정하는 방식은 기본값이 아니다.
2. 팀원은 `raw/users/**` packet으로 원천 자료를 제출한다.
3. stable wiki 반영은 팀장 또는 담당자 검토 후 진행한다.
4. supported claim 승격과 중요한 decision은 human review가 필수다.
5. single split, fast screening, 재현되지 않은 결과는 `tentative`로 둔다.
6. 오래된 `tentative` claim은 일정 기간 후 `stale` 또는 `superseded`로 정리한다.

## 구현 영향

현재 자동화와 skill은 다음 방향으로 수정되어야 한다.

- packet skill 질문은 유지하되, wiki output target은 더 단순한 디렉토리 체계로 유도한다.
- synthesis prompt는 많은 leaf/page를 만드는 것보다 핵심 stable page와 versioned report를 우선해야 한다.
- `datasets`, `benchmarks`, `submissions`, `questions`, `experiments`, `sources`, `briefs`는 신규 생성 기본 route에서 제외하거나 archive/compatibility route로 낮춘다.
- `latest-context`, `overview`, `index`는 더 짧은 entrypoint로 유지되도록 lint 기준을 강화한다.
- `performance`는 submission과 external leaderboard 기록까지 품되, local, external, official evidence surface를 반드시 분리한다.

## 다음 액션

1. 팀장 피드백을 반영한 `wiki/team/page-taxonomy.md` 간소화안 작성.
2. `wiki/team/llm-wiki-operating-harness.md`에 사람용 단순 구조와 agent용 내부 role을 분리.
3. `wiki/team/contribution-workflow.md`에 "팀원은 raw packet 제출, stable page 반영은 reviewer 승인" 원칙 명시.
4. 자동 ingest/synthesis route에서 삭제/병합 대상 디렉토리의 신규 생성 정책 조정.
5. packet skill README/SKILL/references에 단순화된 target wiki 구조 반영.
