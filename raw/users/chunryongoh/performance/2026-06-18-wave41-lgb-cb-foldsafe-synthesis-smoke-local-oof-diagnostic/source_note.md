# Wave41 LGB/CB fold-safe synthesis smoke local OOF diagnostic

This packet records the 2026-06-18 Wave41 LGB/CB fold-safe synthesis smoke run from the ETRI local workspace.

Observed facts:

- The run completed with 13 candidates under `local_oof_diagnostic_only`.
- Final targetwise reblend grouped macro log-loss was `0.6195964535023479`.
- Same-split prior LGB/CB reproduction line was `0.6198365213240887`.
- Delta versus that prior line was approximately `-0.0002400678217408`; lower log-loss is better.
- The result remains short of the first `0.61` local goal by `+0.0095964535023479`.
- Decision matrix counts were `2` supported, `4` tentative, and `25` disputed rows.
- Supported rows were Q2/S4 nested Platt diagnostics by targetwise reblend weight `0.1`, not standalone target-score superiority.
- Most raw LGB/CB weighted reliability rows were disputed by macro Brier guard or lack of targetwise support.

Claim boundary:

- This is local OOF diagnostic evidence only.
- Do not promote this packet to DACON public leaderboard, private leaderboard, organizer-official validation, or `0.5x` evidence.
- Do not claim broad standalone LGB/CB superiority; supported signal is targetwise source/calibration diversity in Q2/S4 plus small Q1/S4 blend components.
