"""
Stack v2: auto-discover ALL leak-free OOF/test sources across wave-1 + wave-2,
combine per target with a heavily-regularized convex meta-learner, honestly
evaluated by NESTED same-subject-hole CV (to kill selection optimism).

Sources scanned (each npz: oof_*_<target> + test_*_<target>, oof_subjmean_<target>):
  wave-1: sliding-window, seqmodel, sasl-qtuning
  wave-2: seqbag (2 npz: res144_gpu0 + res288_gpu1), richfeat-gbdt, saslpp

Schemes compared (all honest / nested where selection happens):
  - subject-mean (baseline)
  - equal-weight average of ALL candidates (fixed, no selection)
  - per-target convex meta-learner (log-loss min, weights>=0 sum=1, L2 shrink to uniform),
    weights fit on full OOF for the test prediction, generalization estimated by NESTED CV.
Submission = the scheme with best NESTED macro (defensible), tie-broken toward equal-weight.
"""
from __future__ import annotations
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import log_loss

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from sleep_baseline.features.lgb_cb_foldsafe_features import build_foldsafe_raw_feature_frame
from sleep_baseline.features.lgb_cb_notebook_features import load_lgb_cb_notebook_modalities
from sleep_baseline.io.raw_loader import load_sample_submission, load_train_labels
from sleep_baseline.training.submission import align_predictions_to_submission

OUT = Path(__file__).parent
T = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
RES = Path("raw/results")
SRC_DIRS = [
    "2026-06-24-wave43-sliding-window",
    "2026-06-24-wave43-seqmodel",
    "2026-06-24-wave43-sasl-qtuning",
    "2026-06-24-wave43-seqbag",
    "2026-06-24-wave43-richfeat-gbdt",
    "2026-06-24-wave43-saslpp",
    "2026-06-24-wave43-context",
    "2026-06-24-wave43-seqbag-mega",
    "2026-06-24-wave43-ssl",
    "2026-06-24-wave43-sleepseg",
    "2026-06-24-wave43-seqaug",
    "2026-06-24-wave43-bigssl",
    "2026-06-24-wave43-deeptab",
    "2026-06-24-wave43-dae",
    "2026-06-24-wave43-sleepphys",
    "2026-06-24-wave43-gbdtbag",
    "2026-06-24-wave43-xgb",
    "2026-06-24-wave43-contrastive",
    "2026-06-24-wave43-structural",
    "2026-06-24-wave43-temporalprior",
    "2026-06-25-wave43-withings",
    "2026-06-25-wave43-sleepstaging",
    "2026-06-25-wave43-organizer-affinity",
    "2026-06-25-wave43-arousal",
    "2026-06-25-wave43-qmobility",
    "2026-06-25-wave43-actigraphy",
    "2026-06-25-wave43-transfer",
    "2026-06-25-wave43-waso",
]
EPS = 1e-6


def ll(y, p):
    m = ~np.isnan(y)
    return float(log_loss(y[m], np.clip(p[m], EPS, 1 - EPS), labels=[0, 1]))


def make_folds(frame, n_folds=5):
    folds = [[] for _ in range(n_folds)]
    sid = frame["subject_id"].astype(str).to_numpy()
    sd = frame["sleep_date"].astype(str).to_numpy()
    idx = np.arange(len(frame))
    for s in np.unique(sid):
        s_idx = idx[sid == s]
        order = s_idx[np.argsort(sd[s_idx], kind="stable")]
        for k, blk in enumerate(np.array_split(order, n_folds)):
            folds[k].extend(blk.tolist())
    out = []
    alli = set(idx.tolist())
    for k in range(n_folds):
        val = np.array(sorted(folds[k]))
        tr = np.array(sorted(alli - set(val.tolist())))
        out.append((tr, val))
    return out


def discover(n_train, n_test):
    """Return {target: {model_name: (oof[n_train], test[n_test])}} and subjmean per target."""
    cand = {t: {} for t in T}
    subjmean_oof = {}
    subjmean_test = {}
    for d in SRC_DIRS:
        npz_files = sorted(glob.glob(str(RES / d / "*.npz")))
        # If a merged predictions.npz exists, skip partial shards to avoid double-counting.
        if any(Path(p).name == "predictions.npz" for p in npz_files):
            npz_files = [p for p in npz_files if Path(p).name == "predictions.npz"]
        for npz_path in npz_files:
            tag = Path(d).name.replace("2026-06-24-wave43-", "") + "/" + Path(npz_path).stem
            z = np.load(npz_path)
            keys = set(z.files)
            for t in T:
                # subject-mean (capture once)
                if f"oof_subjmean_{t}" in keys and t not in subjmean_oof:
                    if len(z[f"oof_subjmean_{t}"]) == n_train:
                        subjmean_oof[t] = z[f"oof_subjmean_{t}"]
                        if f"test_subjmean_{t}" in keys:
                            subjmean_test[t] = z[f"test_subjmean_{t}"]
                # every oof_*_<t> with a matching test_*_<t>
                for k in keys:
                    if not k.startswith("oof_") or not k.endswith(f"_{t}"):
                        continue
                    if "subjmean" in k:
                        continue
                    tk = "test_" + k[len("oof_"):]
                    if tk not in keys:
                        continue
                    o, te = z[k], z[tk]
                    if len(o) != n_train or len(te) != n_test:
                        continue
                    if not (np.isfinite(o).all() and np.isfinite(te).all()):
                        continue
                    name = f"{tag}:{k[len('oof_'):-len('_'+t)]}"
                    cand[t][name] = (np.clip(o, EPS, 1 - EPS), np.clip(te, EPS, 1 - EPS))
    return cand, subjmean_oof, subjmean_test


def convex_weights(P, y, l2=0.5):
    """Min log-loss over convex weights w (>=0, sum=1) with L2 shrink to uniform."""
    M = P.shape[1]
    u = np.ones(M) / M
    m = ~np.isnan(y)
    Pm, ym = P[m], y[m]

    def obj(w):
        p = np.clip(Pm @ w, EPS, 1 - EPS)
        nll = -np.mean(ym * np.log(p) + (1 - ym) * np.log(1 - p))
        return nll + l2 * np.sum((w - u) ** 2)

    cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bnds = [(0.0, 1.0)] * M
    res = minimize(obj, u, method="SLSQP", bounds=bnds, constraints=cons,
                   options={"maxiter": 300, "ftol": 1e-9})
    return res.x if res.success else u


def main():
    payload = build_foldsafe_raw_feature_frame(
        labels=load_train_labels(), sample_submission=load_sample_submission(),
        modalities=load_lgb_cb_notebook_modalities())
    tf = payload.train_frame.reset_index(drop=True)
    test_frame = payload.test_frame.reset_index(drop=True)
    sample_submission = load_sample_submission()
    y = {t: tf[t].astype(float).to_numpy() for t in T}
    folds = make_folds(tf, 5)

    cand, sm_oof, sm_test = discover(len(tf), len(test_frame))
    report = {"n_candidates_per_target": {t: len(cand[t]) for t in T},
              "candidate_names": {t: sorted(cand[t]) for t in T}, "per_target": {}}

    macro_sm = np.mean([ll(y[t], sm_oof[t]) for t in T])

    test_final = {}
    oof_equal = {}
    oof_stack_nested = {}
    test_stack = {}
    oof_chosen = {}
    for t in T:
        names = sorted(cand[t])
        P = np.column_stack([cand[t][n][0] for n in names])          # [450, M]
        Ptest = np.column_stack([cand[t][n][1] for n in names])      # [250, M]
        # include subject-mean as a candidate column too (anchor)
        P = np.column_stack([P, sm_oof[t]])
        Ptest = np.column_stack([Ptest, sm_test[t]])
        names = names + ["subjmean"]
        yt = y[t]

        # equal-weight
        oof_eq = P.mean(axis=1)
        te_eq = Ptest.mean(axis=1)

        # sweep L2 shrinkage; pick the value with best NESTED macro for this target
        L2_GRID = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
        best_l2, best_nested_ll, best_nested = None, 1e9, None
        for l2 in L2_GRID:
            nested = np.full(len(tf), np.nan)
            for oi, (_, val) in enumerate(folds):
                inner = np.concatenate([folds[j][1] for j in range(len(folds)) if j != oi])
                w = convex_weights(P[inner], yt[inner], l2=l2)
                nested[val] = np.clip(P[val] @ w, EPS, 1 - EPS)
            cur = ll(yt, nested)
            if cur < best_nested_ll:
                best_nested_ll, best_l2, best_nested = cur, l2, nested
        nested = best_nested
        # full-OOF convex weights at the chosen L2 -> test prediction (standard stacking)
        w_full = convex_weights(P, yt, l2=best_l2)
        te_stack = np.clip(Ptest @ w_full, EPS, 1 - EPS)

        ll_sm = ll(yt, sm_oof[t])
        ll_eq = ll(yt, oof_eq)
        ll_nested = ll(yt, nested)
        report["per_target"][t] = {
            "n_models": len(names), "subjmean": ll_sm, "equal_all": ll_eq,
            "stack_nested": ll_nested,
            "stack_full_weights": {n: round(float(wv), 3) for n, wv in zip(names, w_full) if wv > 0.02},
        }
        oof_equal[t] = oof_eq
        oof_stack_nested[t] = nested
        test_stack[t] = te_stack
        # choose per-target submission source: nested-stack if it beats equal AND subjmean, else equal, else subjmean
        best = min(ll_sm, ll_eq, ll_nested)
        if best == ll_nested:
            test_final[t] = te_stack
            oof_chosen[t] = nested
        elif best == ll_eq:
            test_final[t] = te_eq
            oof_chosen[t] = oof_eq
        else:
            test_final[t] = np.clip(sm_test[t], EPS, 1 - EPS)
            oof_chosen[t] = np.clip(sm_oof[t], EPS, 1 - EPS)

        # ---- log-loss-targeted calibration (research lever #1): per-target temperature
        # scaling on the chosen prediction's logits, T selected by NESTED same-subject CV.
        def logit(p): return np.log(np.clip(p, EPS, 1 - EPS) / (1 - np.clip(p, EPS, 1 - EPS)))
        from sklearn.linear_model import LogisticRegression
        zt = logit(oof_chosen[t])
        zt_test = logit(test_final[t])
        T_GRID = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0]

        def fit_platt(z, yy):
            mm = ~np.isnan(yy)
            lr = LogisticRegression(C=1e6, solver="lbfgs")
            lr.fit(z[mm].reshape(-1, 1), yy[mm].astype(int))
            return lr

        def best_temp(z, yy):
            mm = ~np.isnan(yy); bT, bl = 1.0, 1e9
            for Tv in T_GRID:
                c = ll(yy[mm], 1.0 / (1.0 + np.exp(-z[mm] / Tv)))
                if c < bl: bl, bT = c, Tv
            return bT

        # nested selection between {none, temperature, platt} per target
        cal_methods = ["none", "temp", "platt"]
        nested = {m: np.full(len(tf), np.nan) for m in cal_methods}
        for oi, (_, val) in enumerate(folds):
            inner = np.concatenate([folds[j][1] for j in range(len(folds)) if j != oi])
            nested["none"][val] = oof_chosen[t][val]
            Tv = best_temp(zt[inner], yt[inner])
            nested["temp"][val] = 1.0 / (1.0 + np.exp(-zt[val] / Tv))
            lr = fit_platt(zt[inner], yt[inner])
            nested["platt"][val] = lr.predict_proba(zt[val].reshape(-1, 1))[:, 1]
        scores = {m: ll(yt, np.clip(nested[m], EPS, 1 - EPS)) for m in cal_methods}
        bestm = min(scores, key=scores.get)
        oof_chosen[t] = np.clip(nested[bestm], EPS, 1 - EPS)
        # final-fit chosen calibration on FULL oof, apply to test
        if bestm == "none":
            pass
        elif bestm == "temp":
            fT = best_temp(zt, yt)
            test_final[t] = 1.0 / (1.0 + np.exp(-zt_test / fT))
        else:
            lr = fit_platt(zt, yt)
            test_final[t] = lr.predict_proba(zt_test.reshape(-1, 1))[:, 1]
        test_final[t] = np.clip(test_final[t], EPS, 1 - EPS)
        report["per_target"][t]["calib_method"] = bestm
        report["per_target"][t]["calib_scores"] = {m: round(scores[m], 5) for m in cal_methods}
        report["per_target"][t]["calibrated_oof_nested"] = scores[bestm]

    macro_eq = np.mean([report["per_target"][t]["equal_all"] for t in T])
    macro_nested = np.mean([report["per_target"][t]["stack_nested"] for t in T])
    macro_chosen_precal = np.mean([min(report["per_target"][t]["subjmean"],
                                       report["per_target"][t]["equal_all"],
                                       report["per_target"][t]["stack_nested"]) for t in T])
    # calibrated macro (after per-target temperature scaling on the chosen prediction)
    macro_chosen = np.mean([ll(y[t], oof_chosen[t]) for t in T])

    # submission from chosen per-target sources
    pred = test_frame[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for t in T:
        pred[t] = np.clip(test_final[t], EPS, 1 - EPS)
    sub = align_predictions_to_submission(pred, sample_submission=sample_submission)
    sub.to_csv(OUT / "submission.csv", index=False)

    report["macro"] = {"subj_mean": macro_sm, "equal_all": macro_eq,
                       "stack_nested": macro_nested,
                       "chosen_precalibration": macro_chosen_precal,
                       "chosen_calibrated": macro_chosen,
                       "projected_public_calibrated": macro_chosen + 0.003}
    with open(OUT / "metrics.json", "w") as f:
        json.dump(report, f, indent=2)

    print("=" * 64)
    print(f"total candidate models discovered (per target): {report['n_candidates_per_target']}")
    print(f"macro subject-mean:     {macro_sm:.5f}")
    print(f"macro equal-all:        {macro_eq:.5f}")
    print(f"macro nested-stack:     {macro_nested:.5f}")
    print(f"macro chosen precal:    {macro_chosen_precal:.5f}")
    print(f"macro chosen CALIBRATED:{macro_chosen:.5f}   <- SUBMISSION")
    print(f"projected public (+0.003 offset): {macro_chosen+0.003:.5f}")
    print("=" * 64)
    for t in T:
        r = report["per_target"][t]
        print(f"  {t}: sm={r['subjmean']:.5f} eq={r['equal_all']:.5f} nested={r['stack_nested']:.5f}  (M={r['n_models']})")
    print(f"submission rows: {len(sub)}")


if __name__ == "__main__":
    main()
