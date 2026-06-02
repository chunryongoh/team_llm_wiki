# Packet Quality Standard

이 문서는 packet PR과 bot PR을 리뷰할 때 필요한 최소 품질 기준이다.

## Packet Minimum

모든 packet은 다음을 가져야 한다.

- `manifest.yaml`
- `packet.md`
- packet-local raw evidence
- `claim_boundary`
- `claim_status`
- source path provenance
- reviewer가 닫을 수 있는 evidence gap 또는 next action

## Entity-First Minimum

`experiment`, `feature`, `model`, `performance`, `preprocessing`, `augmentation` packet은 `wiki_plan.yaml`에 다음을 포함해야 한다.

- `stable_entities`
- `affected_pages`
- `semantic_lint`

가능하면 다음도 포함한다.

- `claim_registry_updates`
- `supersedes_or_conflicts`
- `open_questions`

`wiki-pr-validate`의 `entity_coverage` warning은 merge blocker가 아니지만, reviewer는 packet이 실험 mirror로만 남지 않는지 확인해야 한다.

## ML/AI Claim Gate

`supported` claim은 다음을 충족해야 한다.

- raw metric 또는 raw audit evidence가 있다.
- split, group key, fold count가 명시되어 있다.
- baseline과 같은 evidence surface에서 비교한다.
- metric direction과 averaging policy가 명시되어 있다.
- leakage risk가 숨겨지지 않는다.

요건을 충족하지 못하면 `tentative`, `notebook_output_observation_only`, `user_reported_public_score_only`, `local_oof_diagnostic_only` 같은 좁은 boundary를 사용한다.

## Reviewer Failure Modes

- "best model"이라고 쓰지만 standalone, fixed blend, targetwise reblend가 구분되지 않음
- public score note를 DACON leaderboard evidence처럼 승격함
- 3-fold와 5-fold OOF를 같은 split으로 비교함
- SHAP 또는 feature importance만으로 performance claim을 만듦
- notebook-output summary를 재현된 run evidence처럼 취급함
- feature policy decision을 기록하지 않고 experiment page에만 남김
