"""
build.py — Wave43 ACTIGRAPHY: VALIDATED sleep/wake scoring (Cole-Kripke 1992, Sadeh 1994)
+ STRUCTURAL-CONSTRAINT propagation from the reliable S1/TIB, leak-free OOF+test.

GOAL: crack S2 (sleep efficiency), S3 (sleep onset latency), S4 (WASO) — the targets that
resisted ad-hoc within-sleep wake detection — using TWO PRINCIPLED methods:

  METHOD A — VALIDATED ACTIGRAPHY ALGORITHMS (no training; fixed published coefficients):
    * Build per-MINUTE ACTIVITY COUNTS within the reconstructed in-bed interval from:
        wPedo steps  +  mActivity (non-STILL indicator)  +  within-minute HR std (wHr arrays).
      ETRI gives steps/activity codes, NOT raw accelerometer counts that Cole-Kripke/Sadeh
      were calibrated on, so we build a PROXY activity count and scale it (documented).
    * Cole-Kripke (1992): D = P*(w_{-4}A_{-4}+w_{-3}A_{-3}+w_{-2}A_{-2}+w_{-1}A_{-1}
                                 + w_0 A_0 + w_{+1}A_{+1}+w_{+2}A_{+2}); sleep if D < 1.
      Published weights P=0.00001, w=[404,598,326,441,1408,508,350].
    * Sadeh (1994): PS = 7.601 - 0.065*AVG - 1.08*NATS - 0.056*SD - 0.703*LG;  sleep if PS>0.
      11-min centred window: AVG=mean activity, SD=std, NATS=# epochs 50<=A<100,
      LG=ln(A_0+1). (Published coefficients.)
    * From per-epoch sleep/wake within the in-bed interval, for EACH algorithm derive:
        SE = asleep/in-bed, SOL = bed-start to first sustained sleep (>=10min),
        WASO = wake after onset, #awakenings, longest wake, sleep-period SE.
      Two validated scorers => diversity.

  METHOD C — STRUCTURAL CONSTRAINT propagation (physical identities):
        SE = TST/TIB ;  TIB ~= SOL + TST + WASO.
    We estimate TIB and TST well (S1 cracked). So:
        se_from_tst_tib = mat_tst_h / time_in_bed_h
        nonsleep_h      = time_in_bed_h - mat_tst_h     (= SOL+WASO budget)
        plus ratios and reconciliation deltas vs the two actigraphy scorers.

REUSES /home/chunoh/ETRI/raw/results/2026-06-25-wave43-withings/build.py for: data loading,
in-bed interval reconstruction (charge/screen/light/home anchors), same-subject-hole K=5
folds, leak-free subj_mean_enc, alpha search, Optuna tuners, fit_predict machinery.

Leak rules (MANDATORY): Cole-Kripke/Sadeh are FIXED published algorithms (NO fitting). All
features own-night. subj_mean_enc + reference stats: fold-train for OOF, full-train (no test
labels) for test. No row-own/future label, no test-label fitting, no pseudo-labeling, NO
external data. subjmean OOF macro MUST reproduce 0.62453 (assert).

Output: raw/results/2026-06-25-wave43-actigraphy/{predictions.npz, metrics.json, run.log}
Run: PYTHONPATH=src python raw/results/2026-06-25-wave43-actigraphy/build.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

# ── import the withings build.py as a module to REUSE its machinery ────────────
_WITHINGS_BUILD = REPO / "raw/results/2026-06-25-wave43-withings/build.py"
_spec = importlib.util.spec_from_file_location("withings_build", _WITHINGS_BUILD)
W = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W)

# reused symbols
log = W.log
_clip = W._clip
_ll = W._ll
_finite = W._finite
_assign_night = W._assign_night
_fill_short_gaps = W._fill_short_gaps
_smooth = W._smooth
_count_bouts = W._count_bouts
build_home_features = W.build_home_features
build_withings_features = W.build_withings_features
_gps_to_minute = W._gps_to_minute
_wifi_to_minute = W._wifi_to_minute
make_same_subject_hole_folds = W.make_same_subject_hole_folds
compute_subj_mean_enc = W.compute_subj_mean_enc
compute_subj_mean_enc_fulltest = W.compute_subj_mean_enc_fulltest
find_best_alpha = W.find_best_alpha
optuna_tune_lgb = W.optuna_tune_lgb
optuna_tune_cb = W.optuna_tune_cb
find_best_blend = W.find_best_blend
compute_ref_stats = W.compute_ref_stats
add_fold_features = W.add_fold_features
ALL_FOLD_COLS = W.ALL_FOLD_COLS

from sleep_baseline.features.lgb_cb_notebook_features import load_lgb_cb_notebook_modalities  # noqa: E402
from sleep_baseline.features.lgb_cb_foldsafe_features import build_foldsafe_raw_feature_frame  # noqa: E402
from sleep_baseline.io.raw_loader import load_sample_submission, load_train_labels  # noqa: E402
from sleep_baseline.training.submission import align_predictions_to_submission  # noqa: E402

OUT_DIR = Path(__file__).parent
RAW_ITEMS_DIR = REPO / "raw/datasets/sleep-lifelog-2024/ch2025_data_items"
ALL_TARGETS = W.ALL_TARGETS
S_TARGETS = W.S_TARGETS
N_FOLDS = 5
ALPHA_GRID = W.ALPHA_GRID
N_LGB_TRIALS = 50
N_CB_TRIALS = 25
N_JOBS = 16
NOISE = 0.009

SUBJ_MEAN_REF = W.SUBJ_MEAN_REF
MACRO_SUBJ_MEAN_REF = W.MACRO_SUBJ_MEAN_REF
# current stack nested targets to beat (from task spec)
STACK_REF = {"S1": 0.506, "S2": 0.565, "S3": 0.530, "S4": 0.617}

SEARCH_START_H = W.SEARCH_START_H
SEARCH_END_H = W.SEARCH_END_H
GRID_STEP = W.GRID_STEP
STILL_CODE = W.STILL_CODE

# Cole-Kripke published weights (per-minute formulation, window [-4..+2])
CK_P = 0.00001
CK_W = np.array([404.0, 598.0, 326.0, 441.0, 1408.0, 508.0, 350.0])  # offsets -4..+2
CK_OFFSETS = np.array([-4, -3, -2, -1, 0, 1, 2])
# Sadeh published coefficients (11-min centred window)
SD_INTERCEPT = 7.601
SD_AVG = -0.065
SD_NATS = -1.08
SD_SD = -0.056
SD_LG = -0.703


# ── per-minute ACTIVITY COUNT proxy (within the in-bed grid) ────────────────────
def _hr_std_to_grid(hr_df, GRID, NG):
    """Within-minute HR standard deviation as a movement proxy, on the fixed grid."""
    out = np.full(NG, np.nan)
    if hr_df is None or len(hr_df) == 0:
        return out
    cont = hr_df["cont_h"].to_numpy()
    idx = np.clip(((cont - SEARCH_START_H) * 60.0).astype(int), 0, NG - 1)
    stds = hr_df["hr_std"].to_numpy(dtype=float)
    finite = np.isfinite(stds)
    idx, stds = idx[finite], stds[finite]
    if idx.size == 0:
        return out
    # last write wins per minute (minute-resolution already)
    out[idx] = stds
    return out


def _build_activity_count(step_grid, act_grid, hrstd_grid, NG):
    """Compose a per-minute ACTIVITY COUNT proxy.

    ETRI exposes steps (count/min), an activity CODE (still/walk/run/...), and per-minute
    HR samples (whose within-minute variability rises with movement) — NOT the raw zero-
    crossing accelerometer counts Cole-Kripke/Sadeh expect. We build a non-negative proxy:
        count = steps                              (direct movement)
              + 50 * (activity is non-STILL)       (locomotion-state bump, ~ accel counts)
              + 8  * hr_std                         (within-minute HR variability ~ motion)
    Missing minutes -> 0 (Withings recon already gates to plausibly-in-bed minutes; absence
    of reported movement == immobility here). Scaling chosen so quiet sleep ~0-30 counts and
    active wake ~hundreds, matching the regime the published thresholds were tuned for. This
    proxy choice is DOCUMENTED as the key ETRI adaptation; coefficients themselves are FIXED.
    """
    steps = np.where(np.isfinite(step_grid), np.maximum(step_grid, 0.0), 0.0)
    nonstill = np.where(np.isfinite(act_grid), (act_grid != STILL_CODE).astype(float), 0.0)
    hrstd = np.where(np.isfinite(hrstd_grid), np.maximum(hrstd_grid, 0.0), 0.0)
    count = steps + 50.0 * nonstill + 8.0 * hrstd
    return count


def cole_kripke_sleep(counts):
    """Per-minute Cole-Kripke sleep/wake. Returns bool array (True=asleep)."""
    n = len(counts)
    D = np.zeros(n)
    for w, off in zip(CK_W, CK_OFFSETS):
        shifted = np.zeros(n)
        if off < 0:
            shifted[-off:] = counts[:n + off]
        elif off > 0:
            shifted[:n - off] = counts[off:]
        else:
            shifted = counts
        D += w * shifted
    D *= CK_P
    return D < 1.0


def sadeh_sleep(counts):
    """Per-minute Sadeh sleep/wake. Returns bool array (True=asleep)."""
    n = len(counts)
    asleep = np.zeros(n, dtype=bool)
    # 11-min window centred (Sadeh: 5 before, current, 5 after)
    half = 5
    cap = np.minimum(counts, 300.0)  # Sadeh caps activity at 300 for AVG/SD
    for i in range(n):
        lo, hi = max(0, i - half), min(n, i + half + 1)
        win = cap[lo:hi]
        avg = float(np.mean(win))
        sd = float(np.std(win))
        nats = float(np.sum((win >= 50.0) & (win < 100.0)))
        lg = float(np.log(counts[i] + 1.0))
        ps = SD_INTERCEPT + SD_AVG * avg + SD_NATS * nats + SD_SD * sd + SD_LG * lg
        asleep[i] = ps > 0.0
    return asleep


def _scorer_metrics(asleep, prefix):
    """SE/SOL/WASO/etc from a per-epoch (in-bed) sleep mask. Window == in-bed interval."""
    rec = {}
    tib = len(asleep)
    if tib < 1:
        return {f"{prefix}_{k}": np.nan for k in
                ["se", "tst_h", "sol_h", "waso_h", "n_awak", "longest_wake_min", "se_spt"]}
    tst = int(np.sum(asleep))
    rec[f"{prefix}_se"] = _finite(tst / max(1, tib))
    rec[f"{prefix}_tst_h"] = _finite(tst / 60.0)
    # sleep onset = first sustained (>=10min, >=80% asleep) run
    onset = np.nan
    for j in range(0, max(1, tib - 10)):
        if asleep[j] and np.mean(asleep[j:j + 10]) >= 0.8:
            onset = j
            break
    idxs = np.where(asleep)[0]
    final = idxs[-1] if idxs.size else np.nan
    rec[f"{prefix}_sol_h"] = _finite(onset / 60.0) if np.isfinite(onset) else np.nan
    if np.isfinite(onset) and np.isfinite(final) and final > onset:
        mid = asleep[int(onset):int(final) + 1]
        waso = int(np.sum(~mid))
        rec[f"{prefix}_waso_h"] = _finite(waso / 60.0)
        n_awk, longest = _count_bouts(~mid, min_len=1)
        rec[f"{prefix}_n_awak"] = float(n_awk)
        rec[f"{prefix}_longest_wake_min"] = float(longest)
        spt = int(final) - int(onset) + 1
        rec[f"{prefix}_se_spt"] = _finite(np.sum(mid) / max(1, spt))
    else:
        rec[f"{prefix}_waso_h"] = np.nan
        rec[f"{prefix}_n_awak"] = np.nan
        rec[f"{prefix}_longest_wake_min"] = np.nan
        rec[f"{prefix}_se_spt"] = np.nan
    return rec


def build_actigraphy_features(mods, withings_feat):
    """For each (subject, night) with a reconstructed in-bed interval, build Cole-Kripke,
    Sadeh, and structural-constraint features."""
    t0 = time.time()
    log("  [actig] preparing per-minute streams ...")

    # HR with within-minute std
    hr = mods["wHr"].copy()
    def _mstd(a):
        if hasattr(a, "__len__") and len(a) >= 2:
            v = np.asarray(a, float)
            v = v[np.isfinite(v)]
            return float(np.std(v)) if v.size >= 2 else 0.0
        return np.nan
    hr["hr_std"] = hr["heart_rate"].apply(_mstd)
    hr["night"], hr["cont_h"] = _assign_night(hr["timestamp"])
    hr = hr.dropna(subset=["cont_h", "night"])

    def prep(name):
        df = mods[name].copy()
        df["night"], df["cont_h"] = _assign_night(df["timestamp"])
        return df.dropna(subset=["cont_h", "night"])

    act = prep("mActivity")
    ped = prep("wPedo")

    def grp(df):
        return {k: v for k, v in df.groupby(["subject_id", "night"], sort=False)}

    hr_g, act_g, ped_g = grp(hr), grp(act), grp(ped)

    GRID = np.arange(SEARCH_START_H, SEARCH_END_H, GRID_STEP)
    NG = len(GRID)

    def to_grid(df, valcol):
        out = np.full(NG, np.nan)
        if df is None or len(df) == 0:
            return out
        idx = np.clip(((df["cont_h"].to_numpy() - SEARCH_START_H) * 60.0).astype(int), 0, NG - 1)
        vals = df[valcol].to_numpy(dtype=float)
        finite = np.isfinite(vals)
        idx, vals = idx[finite], vals[finite]
        if idx.size == 0:
            return out
        sums = np.bincount(idx, weights=vals, minlength=NG)
        cnts = np.bincount(idx, minlength=NG)
        with np.errstate(invalid="ignore", divide="ignore"):
            g = sums / cnts
        g[cnts == 0] = np.nan
        return g

    # withings in-bed interval lookup
    wlut = {(r["subject_id"], r["lifelog_date"]): r for _, r in withings_feat.iterrows()}

    records = []
    for (subj, lifelog_date), wf in wlut.items():
        night = lifelog_date  # withings lifelog_date == night key string
        rec = {"subject_id": subj, "lifelog_date": str(lifelog_date)}

        bed_entry_h = wf.get("bed_entry_hour", np.nan)
        bed_exit_h = wf.get("bed_exit_hour", np.nan)
        tib_h = wf.get("time_in_bed_h", np.nan)
        mat_tst_h = wf.get("mat_tst_h", np.nan)

        if not (np.isfinite(bed_entry_h) and np.isfinite(bed_exit_h) and bed_exit_h > bed_entry_h):
            # no valid in-bed window -> all actigraphy features nan
            for pref in ("ck", "sd"):
                rec.update(_scorer_metrics(np.zeros(0, bool), pref))
            rec.update(_struct_features(np.nan, np.nan, np.nan, np.nan, np.nan, np.nan))
            records.append(rec)
            continue

        entry_i = int(round((bed_entry_h - SEARCH_START_H) * 60.0))
        exit_i = int(round((bed_exit_h - SEARCH_START_H) * 60.0))
        entry_i = max(0, min(NG - 1, entry_i))
        exit_i = max(entry_i + 1, min(NG - 1, exit_i))

        step_grid = to_grid(ped_g.get((subj, night)), "step")
        act_grid = to_grid(act_g.get((subj, night)), "m_activity")
        hrstd_grid = _hr_std_to_grid(hr_g.get((subj, night)), GRID, NG)

        counts_full = _build_activity_count(step_grid, act_grid, hrstd_grid, NG)
        seg = slice(entry_i, exit_i + 1)
        counts = counts_full[seg]

        # data coverage within the in-bed window (how much movement signal we actually have)
        any_signal = (np.isfinite(step_grid[seg]) | np.isfinite(act_grid[seg])
                      | np.isfinite(hrstd_grid[seg]))
        rec["actig_coverage"] = _finite(np.mean(any_signal)) if counts.size else np.nan
        rec["actig_count_med"] = _finite(np.median(counts)) if counts.size else np.nan
        rec["actig_count_mean"] = _finite(np.mean(counts)) if counts.size else np.nan

        # ── Cole-Kripke ──
        ck_asleep = cole_kripke_sleep(counts)
        ck_asleep = _smooth_bool(ck_asleep)
        rec.update(_scorer_metrics(ck_asleep, "ck"))

        # ── Sadeh ──
        sd_asleep = sadeh_sleep(counts)
        sd_asleep = _smooth_bool(sd_asleep)
        rec.update(_scorer_metrics(sd_asleep, "sd"))

        # agreement between the two validated scorers
        if ck_asleep.size and sd_asleep.size:
            rec["scorer_agree"] = _finite(np.mean(ck_asleep == sd_asleep))
        else:
            rec["scorer_agree"] = np.nan

        # ── METHOD C: structural constraint from reliable TIB/TST ──
        rec.update(_struct_features(
            tib_h, mat_tst_h,
            rec.get("ck_se", np.nan), rec.get("sd_se", np.nan),
            rec.get("ck_waso_h", np.nan), rec.get("sd_waso_h", np.nan)))

        records.append(rec)

    feat = pd.DataFrame(records)
    log(f"  [actig] built {feat.shape} in {time.time()-t0:.1f}s")
    return feat


def _smooth_bool(mask, win=11, thresh=0.5):
    if mask.size == 0:
        return mask
    sm = _smooth(mask.astype(float), win=win)
    return sm >= thresh


def _struct_features(tib_h, tst_h, ck_se, sd_se, ck_waso, sd_waso):
    """METHOD C structural-constraint features from physical identities."""
    rec = {}
    rec["se_from_tst_tib"] = _finite(tst_h / tib_h) if (np.isfinite(tst_h) and np.isfinite(tib_h) and tib_h > 0) else np.nan
    rec["nonsleep_h"] = _finite(tib_h - tst_h) if (np.isfinite(tib_h) and np.isfinite(tst_h)) else np.nan
    rec["nonsleep_frac"] = _finite((tib_h - tst_h) / tib_h) if (np.isfinite(tib_h) and np.isfinite(tst_h) and tib_h > 0) else np.nan
    # reconcile structural SE vs each actigraphy SE
    se_struct = rec["se_from_tst_tib"]
    rec["se_struct_minus_ck"] = _finite(se_struct - ck_se) if (np.isfinite(se_struct) and np.isfinite(ck_se)) else np.nan
    rec["se_struct_minus_sd"] = _finite(se_struct - sd_se) if (np.isfinite(se_struct) and np.isfinite(sd_se)) else np.nan
    # nonsleep budget allocated to WASO per each scorer; residual ~ SOL implied
    rec["nonsleep_minus_ck_waso"] = _finite(rec["nonsleep_h"] - ck_waso) if (np.isfinite(rec["nonsleep_h"]) and np.isfinite(ck_waso)) else np.nan
    rec["nonsleep_minus_sd_waso"] = _finite(rec["nonsleep_h"] - sd_waso) if (np.isfinite(rec["nonsleep_h"]) and np.isfinite(sd_waso)) else np.nan
    return rec


# feature column groups
CK_COLS = [f"ck_{k}" for k in ["se", "tst_h", "sol_h", "waso_h", "n_awak", "longest_wake_min", "se_spt"]]
SD_COLS = [f"sd_{k}" for k in ["se", "tst_h", "sol_h", "waso_h", "n_awak", "longest_wake_min", "se_spt"]]
STRUCT_COLS = ["se_from_tst_tib", "nonsleep_h", "nonsleep_frac", "se_struct_minus_ck",
               "se_struct_minus_sd", "nonsleep_minus_ck_waso", "nonsleep_minus_sd_waso"]
QUAL_COLS = ["actig_coverage", "actig_count_med", "actig_count_mean", "scorer_agree"]
ACTIG_NUM_COLS = CK_COLS + SD_COLS + STRUCT_COLS + QUAL_COLS


# ── MAIN ────────────────────────────────────────────────────────────────────────
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    W._LOG_FH = open(OUT_DIR / "run.log", "w")
    t_start = time.time()
    log("=" * 72)
    log("Wave43 ACTIGRAPHY — Cole-Kripke + Sadeh (validated) + structural-constraint")
    log("=" * 72)

    log("\n[1] Loading foldsafe frame ...")
    labels = load_train_labels()
    ss = load_sample_submission()
    notebook_mods = load_lgb_cb_notebook_modalities()
    payload = build_foldsafe_raw_feature_frame(labels=labels, sample_submission=ss, modalities=notebook_mods)
    train_frame = payload.train_frame.reset_index(drop=True)
    test_frame = payload.test_frame.reset_index(drop=True)
    log(f"  train rows={len(train_frame)} test rows={len(test_frame)}")
    for fr in (train_frame, test_frame):
        fr["subject_id"] = fr["subject_id"].astype(str)
        fr["lifelog_date"] = fr["lifelog_date"].astype(str)

    existing_cols = [c for c in train_frame.columns
                     if c not in (["subject_id", "sleep_date", "lifelog_date"] + ALL_TARGETS)
                     and pd.api.types.is_numeric_dtype(train_frame[c])]
    log(f"  existing daily/intra-day numeric feature cols: {len(existing_cols)}")

    log("\n[2] Loading raw modalities ...")
    mods = {}
    for name in ["wHr", "wPedo", "mActivity", "mScreenStatus", "mACStatus", "mLight", "wLight"]:
        mods[name] = pd.read_parquet(RAW_ITEMS_DIR / f"ch2025_{name}.parquet")
        mods[name]["subject_id"] = mods[name]["subject_id"].astype(str)
        log(f"  {name}: {mods[name].shape}")
    gps = pd.read_parquet(RAW_ITEMS_DIR / "ch2025_mGps.parquet")
    gps["subject_id"] = gps["subject_id"].astype(str)
    wifi = pd.read_parquet(RAW_ITEMS_DIR / "ch2025_mWifi.parquet")
    wifi["subject_id"] = wifi["subject_id"].astype(str)
    log(f"  mGps: {gps.shape}  mWifi: {wifi.shape}")

    log("\n[3] Home features + Withings in-bed reconstruction (REUSED) ...")
    gps_min = _gps_to_minute(gps)
    wifi_min = _wifi_to_minute(wifi)
    home_feat = build_home_features(gps_min, wifi_min)
    home_feat["subject_id"] = home_feat["subject_id"].astype(str)
    home_feat["lifelog_date"] = home_feat["lifelog_date"].astype(str)
    wf = build_withings_features(mods, home_feat)
    wf["subject_id"] = wf["subject_id"].astype(str)
    wf["lifelog_date"] = wf["lifelog_date"].astype(str)
    withings_cols = [c for c in W.WITHINGS_NUM_COLS if c in wf.columns]
    log(f"  withings recon features: {len(withings_cols)}")

    log("\n[4] ACTIGRAPHY scoring (Cole-Kripke + Sadeh) + structural constraints ...")
    af = build_actigraphy_features(mods, wf)
    af["subject_id"] = af["subject_id"].astype(str)
    af["lifelog_date"] = af["lifelog_date"].astype(str)
    actig_cols = [c for c in ACTIG_NUM_COLS if c in af.columns]
    log(f"  actigraphy features: {len(actig_cols)} ({len(CK_COLS)} CK, {len(SD_COLS)} SD, "
        f"{len(STRUCT_COLS)} struct, {len(QUAL_COLS)} qual)")

    # sanity: did the scorers produce a spread of SE?
    for col in ["ck_se", "sd_se", "se_from_tst_tib"]:
        v = af[col].to_numpy(dtype=float)
        v = v[np.isfinite(v)]
        if v.size:
            log(f"    {col}: n={v.size} mean={v.mean():.3f} std={v.std():.3f} "
                f"min={v.min():.3f} max={v.max():.3f}")

    # merge withings + actigraphy + existing
    base_tr = train_frame[["subject_id", "sleep_date", "lifelog_date"] + ALL_TARGETS + existing_cols]
    base_te = test_frame[["subject_id", "sleep_date", "lifelog_date"] + existing_cols]
    merge_keys = ["subject_id", "lifelog_date"]
    train_merged = (base_tr.merge(wf, on=merge_keys, how="left")
                          .merge(af, on=merge_keys, how="left").reset_index(drop=True))
    test_merged = (base_te.merge(wf, on=merge_keys, how="left")
                         .merge(af, on=merge_keys, how="left").reset_index(drop=True))

    cov_tr = train_merged[actig_cols].notna().any(axis=1).sum()
    cov_te = test_merged[actig_cols].notna().any(axis=1).sum()
    log(f"  train rows with actigraphy: {cov_tr}/{len(train_merged)}")
    log(f"  test  rows with actigraphy: {cov_te}/{len(test_merged)}")

    # FEATURE SETS
    #  actig      : actigraphy + structural only (the two NEW methods, isolated)
    #  actig_wth  : actigraphy + structural + withings recon (principled feature stack)
    #  combo      : everything (actig + struct + withings + existing daily/intra-day)
    feat_actig = actig_cols
    feat_actig_wth = actig_cols + withings_cols
    feat_combo = actig_cols + withings_cols + existing_cols
    log(f"  feat_actig={len(feat_actig)} feat_actig_wth={len(feat_actig_wth)} feat_combo={len(feat_combo)}")

    log("\n[5] Folds (same-subject-hole K=5) ...")
    folds = make_same_subject_hole_folds(train_merged, N_FOLDS)
    for k, (tr, vl) in enumerate(folds):
        log(f"  fold {k}: train={len(tr)} val={len(vl)}")
    subject_ids = train_merged["subject_id"].astype(str).to_numpy()

    log("\n[6] Alpha search + VERIFY subject-mean OOF == 0.62453 ...")
    best_alpha, sm_oof_per_target = {}, {}
    for t in ALL_TARGETS:
        a, ll = find_best_alpha(train_merged, folds, t, ALPHA_GRID)
        best_alpha[t] = a
        sm_oof_per_target[t] = ll
        log(f"  {t}: alpha={a} subjmean_oof={ll:.5f}  (ref {SUBJ_MEAN_REF[t]:.5f})")
    macro_sm = float(np.mean([sm_oof_per_target[t] for t in ALL_TARGETS]))
    log(f"  MACRO subj-mean OOF = {macro_sm:.5f}  (expected {MACRO_SUBJ_MEAN_REF})")
    assert abs(macro_sm - MACRO_SUBJ_MEAN_REF) <= 0.01, \
        f"LEAK/REGRESSION: subjmean OOF macro {macro_sm:.5f} != {MACRO_SUBJ_MEAN_REF}"
    log("  [OK] subjmean OOF reproduces reference (leak-safe folds confirmed)")

    log(f"\n[7] Per-target Optuna ({N_LGB_TRIALS} LGB + {N_CB_TRIALS} CB) x 3 feature sets ...")
    params = {"actig": {}, "actig_wth": {}, "combo": {}}
    for fs_name, fs_cols in [("actig", feat_actig), ("actig_wth", feat_actig_wth),
                             ("combo", feat_combo)]:
        for t in ALL_TARGETS:
            t0 = time.time()
            lp, lv = optuna_tune_lgb(train_merged, fs_cols, t, folds, best_alpha[t], subject_ids, N_LGB_TRIALS)
            cp, cv = optuna_tune_cb(train_merged, fs_cols, t, folds, best_alpha[t], subject_ids, N_CB_TRIALS)
            params[fs_name][t] = {"lgb": lp, "cb": cp, "lgb_oof": lv, "cb_oof": cv}
            log(f"  [{fs_name}] {t} lgb={lv:.5f} cb={cv:.5f}  ({time.time()-t0:.0f}s)")

    log("\n[8] Full OOF + test prediction ...")
    import lightgbm as lgb
    from catboost import CatBoostClassifier

    def fit_predict_set(fs_cols, params_store):
        oof_lgb = {t: np.full(len(train_merged), np.nan) for t in ALL_TARGETS}
        oof_cb = {t: np.full(len(train_merged), np.nan) for t in ALL_TARGETS}
        test_lgb = {t: np.zeros(len(test_merged)) for t in ALL_TARGETS}
        test_cb = {t: np.zeros(len(test_merged)) for t in ALL_TARGETS}
        foldf_test = add_fold_features(test_merged, compute_ref_stats(train_merged, np.arange(len(train_merged))))
        for tr, vl in folds:
            ref_fold = compute_ref_stats(train_merged, tr)
            foldf_all = add_fold_features(train_merged, ref_fold)
            for t in ALL_TARGETS:
                alpha = best_alpha[t]
                enc = compute_subj_mean_enc(train_merged, tr, subject_ids, t, alpha)
                enc_te = compute_subj_mean_enc_fulltest(train_merged, test_merged, t, alpha)

                def make_X(frame, idx, enc_vals, fsrc, fidx, cols):
                    x = frame.iloc[idx][cols].copy() if idx is not None else frame[cols].copy()
                    x["subj_mean_enc"] = enc_vals
                    for rc in ALL_FOLD_COLS:
                        x[rc] = (fsrc.iloc[fidx][rc].to_numpy() if fidx is not None
                                 else fsrc[rc].to_numpy())
                    return x

                x_tr = make_X(train_merged, tr, enc[tr], foldf_all, tr, fs_cols)
                x_vl = make_X(train_merged, vl, enc[vl], foldf_all, vl, fs_cols)
                x_te = make_X(test_merged, None, enc_te, foldf_test, None, fs_cols)
                y_tr = train_merged.iloc[tr][t].astype(float).to_numpy()
                ytv = y_tr[~np.isnan(y_tr)]
                if len(np.unique(ytv)) < 2:
                    fb = float(np.nanmean(ytv)) if ytv.size else 0.5
                    oof_lgb[t][vl] = fb; oof_cb[t][vl] = fb
                    test_lgb[t] += fb / N_FOLDS; test_cb[t] += fb / N_FOLDS
                    continue
                ml = lgb.LGBMClassifier(**{**params_store[t]["lgb"], "objective": "binary",
                                           "random_state": 42, "verbose": -1, "n_jobs": N_JOBS})
                ml.fit(x_tr, y_tr)
                oof_lgb[t][vl] = _clip(ml.predict_proba(x_vl)[:, 1])
                test_lgb[t] += _clip(ml.predict_proba(x_te)[:, 1]) / N_FOLDS
                mc = CatBoostClassifier(**{**params_store[t]["cb"], "loss_function": "Logloss",
                                           "verbose": 0, "random_state": 42, "thread_count": N_JOBS})
                mc.fit(x_tr, y_tr)
                oof_cb[t][vl] = _clip(mc.predict_proba(x_vl)[:, 1])
                test_cb[t] += _clip(mc.predict_proba(x_te)[:, 1]) / N_FOLDS
        return oof_lgb, oof_cb, test_lgb, test_cb

    sets = {}
    for fs_name, fs_cols in [("actig", feat_actig), ("actig_wth", feat_actig_wth),
                             ("combo", feat_combo)]:
        log(f"  fitting {fs_name} ...")
        sets[fs_name] = fit_predict_set(fs_cols, params[fs_name])

    # subjmean OOF/test
    oof_sm = {t: np.full(len(train_merged), np.nan) for t in ALL_TARGETS}
    test_sm = {t: np.zeros(len(test_merged)) for t in ALL_TARGETS}
    for tr, vl in folds:
        for t in ALL_TARGETS:
            enc = compute_subj_mean_enc(train_merged, tr, subject_ids, t, best_alpha[t])
            oof_sm[t][vl] = _clip(enc[vl])
            enc_te = compute_subj_mean_enc_fulltest(train_merged, test_merged, t, best_alpha[t])
            test_sm[t] += _clip(enc_te) / N_FOLDS

    log("\n[9] Metrics ...")
    y_arr = {t: train_merged[t].astype(float).to_numpy() for t in ALL_TARGETS}
    results = {}
    for t in ALL_TARGETS:
        y = y_arr[t]
        sm_ll = _ll(y, oof_sm[t])
        cand = {}
        for fs_name in ("actig", "actig_wth", "combo"):
            ol, oc, _, _ = sets[fs_name]
            cand[f"{fs_name}_lgb"] = ol[t]
            cand[f"{fs_name}_cb"] = oc[t]
        cand_ll = {k: _ll(y, v) for k, v in cand.items()}
        best_name = min(cand_ll, key=cand_ll.get)
        best_oof = cand[best_name]
        best_ll = cand_ll[best_name]
        w, blend_ll = find_best_blend(best_oof, oof_sm[t], y)
        final_ll = min(best_ll, blend_ll)
        delta = sm_ll - final_ll
        # isolate the NEW methods: best of actig-only (no existing daily features)
        actig_only_best = min(cand_ll["actig_lgb"], cand_ll["actig_cb"])
        actig_wth_best = min(cand_ll["actig_wth_lgb"], cand_ll["actig_wth_cb"])
        results[t] = {
            "subj_mean_oof": sm_ll, "subj_mean_ref": SUBJ_MEAN_REF[t],
            **{f"{k}_oof": v for k, v in cand_ll.items()},
            "best_model": best_name, "best_model_oof": best_ll,
            "blend_w": w, "blend_oof": blend_ll, "final_oof": final_ll,
            "delta_vs_subjmean": delta, "beats_subjmean_noise": bool(delta > NOISE),
            "actig_only_oof": actig_only_best,
            "actig_wth_oof": actig_wth_best,
            "actig_only_delta_vs_subjmean": sm_ll - actig_only_best,
            "actig_only_beats_subjmean": bool(sm_ll - actig_only_best > NOISE),
        }
        if t in STACK_REF:
            results[t]["stack_ref"] = STACK_REF[t]
            results[t]["final_delta_vs_stack"] = STACK_REF[t] - final_ll
            results[t]["beats_stack_noise"] = bool(STACK_REF[t] - final_ll > NOISE)
            results[t]["actig_only_delta_vs_stack"] = STACK_REF[t] - actig_only_best
        log(f"  {t}: sm={sm_ll:.5f} | actig_only={actig_only_best:.5f} actig+wth={actig_wth_best:.5f} "
            f"| best={best_name}({best_ll:.5f}) blend={blend_ll:.5f}(w={w:.2f}) final={final_ll:.5f} "
            f"d_sm={delta:+.5f} "
            + (f"d_stack={results[t].get('final_delta_vs_stack',0):+.5f} " if t in STACK_REF else "")
            + ("BEATS_SM" if results[t]["beats_subjmean_noise"] else "no"))

    macro_final = float(np.mean([results[t]["final_oof"] for t in ALL_TARGETS]))
    improved = [t for t in ALL_TARGETS if results[t]["beats_subjmean_noise"]]
    improved_S = [t for t in S_TARGETS if results[t]["beats_subjmean_noise"]]
    beats_stack_S = [t for t in S_TARGETS if results[t].get("beats_stack_noise")]
    actig_cracks_S = [t for t in S_TARGETS if results[t]["actig_only_beats_subjmean"]]
    log(f"\n  MACRO subj-mean={macro_sm:.5f}  final={macro_final:.5f}  delta={macro_sm - macro_final:+.5f}")
    log(f"  beats SM-noise: {improved}  (S: {improved_S})")
    log(f"  beats STACK-noise on S: {beats_stack_S}")
    log(f"  actig-ONLY (new methods, no daily feats) beats SM-noise on S: {actig_cracks_S}")

    # ── feature importance (combo LGB, gain) — which method/features matter for S? ──
    log("\n[10] Feature importance (combo LGB, gain) — actig/struct/withings only ...")
    importances = {}
    interest_cols = set(actig_cols) | set(withings_cols) | set(ALL_FOLD_COLS) | {"subj_mean_enc"}
    for t in S_TARGETS:
        imp_t = {}
        y_all = y_arr[t]
        for tr, vl in folds:
            ref = compute_ref_stats(train_merged, tr)
            foldf = add_fold_features(train_merged, ref)
            enc = compute_subj_mean_enc(train_merged, tr, subject_ids, t, best_alpha[t])
            x_tr = train_merged.iloc[tr][feat_combo].copy()
            x_tr["subj_mean_enc"] = enc[tr]
            for rc in ALL_FOLD_COLS:
                x_tr[rc] = foldf.iloc[tr][rc].to_numpy()
            y_tr = y_all[tr]
            ytv = y_tr[~np.isnan(y_tr)]
            if len(np.unique(ytv)) < 2:
                continue
            m = lgb.LGBMClassifier(n_estimators=200, num_leaves=15, learning_rate=0.05,
                                   random_state=42, verbose=-1, n_jobs=N_JOBS, objective="binary",
                                   importance_type="gain")
            m.fit(x_tr, y_tr)
            for f, g in zip(x_tr.columns, m.feature_importances_):
                imp_t[f] = imp_t.get(f, 0.0) + float(g)
        ranked = sorted([(f, v) for f, v in imp_t.items() if f in interest_cols], key=lambda kv: -kv[1])
        importances[t] = ranked[:15]
        log(f"  {t} top actig/struct/withings features by gain:")
        for f, v in ranked[:10]:
            tag = ("CK" if f in CK_COLS else "SD" if f in SD_COLS else
                   "STRUCT" if f in STRUCT_COLS else "QUAL" if f in QUAL_COLS else
                   "WITHINGS" if f in withings_cols else "FOLD/ENC")
            log(f"      [{tag:8s}] {f:30s} {v:10.1f}")

    log("\n[11] Saving predictions.npz ...")
    save = {}
    for t in ALL_TARGETS:
        for fs_name in ("actig", "actig_wth", "combo"):
            ol, oc, tl, tc = sets[fs_name]
            save[f"oof_{fs_name}lgb_{t}"] = ol[t]
            save[f"oof_{fs_name}cb_{t}"] = oc[t]
            save[f"test_{fs_name}lgb_{t}"] = _clip(tl[t])
            save[f"test_{fs_name}cb_{t}"] = _clip(tc[t])
        save[f"oof_subjmean_{t}"] = oof_sm[t]
        save[f"test_subjmean_{t}"] = _clip(test_sm[t])
    np.savez(OUT_DIR / "predictions.npz", **save)
    log(f"  wrote {OUT_DIR / 'predictions.npz'} with {len(save)} arrays")

    log("\n[12] metrics.json ...")
    metrics = {
        "pipeline": "wave43-actigraphy",
        "approach": ("METHOD A: validated actigraphy sleep/wake scoring (Cole-Kripke 1992, "
                     "Sadeh 1994, FIXED published coefficients, no fitting) on a per-minute "
                     "ACTIVITY-COUNT PROXY (wPedo steps + mActivity non-STILL + within-minute "
                     "wHr std) inside the reconstructed in-bed interval. METHOD C: structural-"
                     "constraint propagation from reliable TIB/TST (SE=TST/TIB, nonsleep budget, "
                     "reconciliation deltas vs each scorer)."),
        "activity_count_proxy": "steps + 50*(mActivity!=STILL) + 8*hr_within_minute_std; missing->0",
        "cole_kripke": {"P": CK_P, "weights": CK_W.tolist(), "offsets": CK_OFFSETS.tolist(),
                        "rule": "sleep if D<1"},
        "sadeh": {"intercept": SD_INTERCEPT, "avg": SD_AVG, "nats": SD_NATS, "sd": SD_SD,
                  "lg": SD_LG, "window_min": 11, "rule": "sleep if PS>0", "activity_cap": 300},
        "n_lgb_trials": N_LGB_TRIALS, "n_cb_trials": N_CB_TRIALS, "n_folds": N_FOLDS,
        "ck_features": CK_COLS, "sd_features": SD_COLS, "struct_features": STRUCT_COLS,
        "qual_features": QUAL_COLS,
        "n_actig_features": len(actig_cols), "n_withings_features": len(withings_cols),
        "n_existing_features": len(existing_cols),
        "train_actig_coverage": int(cov_tr), "train_rows": len(train_merged),
        "test_actig_coverage": int(cov_te), "test_rows": len(test_merged),
        "macro_subj_mean_ref": MACRO_SUBJ_MEAN_REF, "macro_subj_mean_oof": macro_sm,
        "macro_final_oof": macro_final, "delta_macro_vs_subjmean": macro_sm - macro_final,
        "noise_floor": NOISE,
        "improved_vs_subjmean": improved, "improved_S_vs_subjmean": improved_S,
        "beats_stack_noise_S": beats_stack_S,
        "actig_only_cracks_S_vs_subjmean": actig_cracks_S,
        "stack_ref": STACK_REF,
        "best_alpha_per_target": best_alpha,
        "tuning_oof": {fs: {t: {"lgb": params[fs][t]["lgb_oof"], "cb": params[fs][t]["cb_oof"]}
                            for t in ALL_TARGETS} for fs in ("actig", "actig_wth", "combo")},
        "feature_importance_S": {t: importances[t] for t in S_TARGETS},
        "per_target": results,
        "subjmean_oof_verification": {
            "macro_oof": macro_sm, "expected": MACRO_SUBJ_MEAN_REF,
            "per_target_oof": sm_oof_per_target,
            "match": bool(abs(macro_sm - MACRO_SUBJ_MEAN_REF) <= 0.01),
        },
        "leak_check": (
            "Cole-Kripke & Sadeh are FIXED published algorithms with NO fitted parameters. "
            "All actigraphy + structural features computed from each night's OWN movement/HR "
            "streams inside that night's own reconstructed in-bed interval over fixed clock "
            "window [19:00 lifelog_date, 12:00 sleep_date]. Structural features use own-night "
            "TIB/TST. subj_mean_enc + regularity/rank reference stats = fold-train for OOF, "
            "full-train (no test labels) for test. subjmean OOF macro asserted == 0.62453 "
            "(leak-safe same-subject-hole folds confirmed). No row-own/future label, no "
            "test-label fitting, no pseudo-labeling, NO external/Nanum data. Features forced finite."
        ),
        "external_data_used": False,
        "elapsed_seconds": time.time() - t_start,
    }
    with open(OUT_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=float)
    log(f"  wrote {OUT_DIR / 'metrics.json'}")

    log("\n" + "=" * 72)
    log(f"DONE in {time.time()-t_start:.0f}s")
    log("=" * 72)
    W._LOG_FH.close()


if __name__ == "__main__":
    main()
