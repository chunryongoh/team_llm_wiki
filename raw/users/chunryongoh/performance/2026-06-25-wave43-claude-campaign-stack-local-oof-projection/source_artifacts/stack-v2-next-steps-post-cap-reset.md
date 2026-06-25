# Wave43 — queued SDD plan (execute after org credit cap resets 6pm KST)
Confirmed: same-subject-hole nested OOF = public - 0.003 (2 submissions). Best public 0.60761.
Current ceiling: stack(94 cand)+temp/Platt calib OOF 0.60252 (~0.6055 public). Gap to 0.57 public = ~0.035 OOF (DISCRIMINATION gap, not calibration).

## Priority order (each: leak-free, same-subject-hole CV, save per-model OOF+test npz for the stack, every 0.001 OOF = 0.001 public)
1. [mixup/aug seq retrain] GPU. Retrain bigru/tcn/transformer bag WITH augmentation: jitter, scaling, magnitude/time-warp, mixup on intra-day sequences. Aug = regularization for N=450; research-backed for log-loss/calibration. Most realistic lever to break the Q2/Q3 saturation. Dir: wave43-seqaug.
2. [SSL pretrain -> linear probe] GPU, higher cost. Masked-reconstruction / contrastive pretrain on RAW unlabeled wearable streams (Pulse-PPG/Step2Heart style; HR-from-accel forecasting as pretext), freeze, mean-pool embeddings, logistic probe. Attacks the discrimination gap directly. LEAK CARE: pretrain may use all rows (no labels) since transductive is allowed, but probe/scaler stats train-fold only. Dir: wave43-ssl.
3. [focal loss seq] cheap GPU. Retrain seq with focal loss (gamma 1-3) — research: better calibration/log-loss. Dir: wave43-focal.
4. [explicit sleep-segment windows] cheap CPU. Detect longest low-HR+low-activity+dark stretch = sleep proxy; compute HRV/stats ONLY in that segment + its timing/duration; add to GBDT/seq. Dir: wave43-sleepseg.
5. Re-stack ALL (existing 94 + new) via stack-v2/build.py (add new dirs to SRC_DIRS), keep nested-CV convex + temp/Platt calib.

## Honest expectation
0.57 public needs OOF ~0.567 (~0.035 below current). Subjective Q (Q1-Q3) has irreducible self-rating noise; 0.57 may exceed this data's ceiling. Levers 1-2 are the only real shots; treat 0.57 as aspirational, "best achievable public" as the real objective.
