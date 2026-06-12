# Packet Quality Standard

이 문서는 packet PR과 bot PR을 리뷰할 때 필요한 최소 품질 기준이다. Packet quality는 evidence, claim calibration, 그리고 wiki graph를 얼마나 잘 진화시키는지로 판단한다.

## Packet minimum

모든 packet은 다음을 가져야 한다.

- `manifest.yaml`
- `packet.md`
- packet-local raw evidence
- `claim_boundary`
- `claim_status`
- source path provenance
- reviewer가 닫을 수 있는 evidence gap 또는 next action

## Entity-first minimum

`experiment`, `feature`, `model`, `performance`, `preprocessing`, `augmentation` packet은 `wiki_plan.yaml`에 다음을 포함해야 한다.

- `stable_entities`
- `affected_pages`
- `semantic_lint`
- `page_role` 또는 `role` for proposed pages
- `promotion_reason` when a leaf page is proposed

권장 추가 필드:

- `claim_registry_updates`
- `supersedes_or_conflicts`
- `open_questions`
- `expected_change`

String-only entries are accepted for backward compatibility, but reviewers should treat them as weaker than structured page-role plans.

## Good packet outcome

좋은 packet은 dated packet review page만 만들지 않는다. Synthesis bot이 어떤 stable feature, model, target, preprocessing, performance/leaderboard, decision, target/open-issue, claim page를 갱신해야 하는지 알려준다.

## Weak but allowed

Weak packet도 useful raw evidence를 보존하고 claim을 `tentative`로 둔다면 merge될 수 있다. PR preview는 missing evidence, missing page role, packet-review-only plan을 드러내야 하며, reviewer는 follow-up packet이 필요한지 판단한다.

## ML/AI claim gate

`supported` claim은 다음을 충족해야 한다.

- raw metric 또는 raw audit evidence가 있다.
- split, group key, fold count가 명시되어 있다.
- baseline과 같은 evidence surface에서 비교한다.
- metric direction과 averaging policy가 명시되어 있다.
- leakage risk가 숨겨지지 않는다.

요건을 충족하지 못하면 `tentative`, `notebook_output_observation_only`, `user_reported_public_score_only`, `local_oof_diagnostic_only` 같은 좁은 boundary를 사용한다.

## Reviewer failure modes

- "best model"이라고 쓰지만 standalone, fixed blend, targetwise reblend가 구분되지 않음
- public score note를 DACON leaderboard evidence처럼 승격함
- 3-fold와 5-fold OOF를 같은 split으로 비교함
- SHAP 또는 feature importance만으로 performance claim을 만듦
- notebook-output summary를 재현된 run evidence처럼 취급함
- feature policy decision을 기록하지 않고 experiment page에만 남김
