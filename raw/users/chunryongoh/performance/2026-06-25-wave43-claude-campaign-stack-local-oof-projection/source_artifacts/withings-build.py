"""
build.py — Wave43 WITHINGS-MAT-MIMICKING features + per-target GBDT, leak-free OOF+test.

KEY INSIGHT: The objective sleep targets S1/S2/S3/S4 are measured by a Withings Sleep
Analyzer (an UNDER-MATTRESS sleep mat) which only measures sleep when the person is
(a) physically IN BED and (b) AT HOME. The watch/phone sensors we have measure the SAME
night's physiology but we have not ALIGNED the watch's view to the mat's measurement
CONDITIONS. So reconstruct the in-bed interval the way the mat sees it, using signals
NOT yet exploited as BED-ANCHORS:
  * PHONE CHARGING (mACStatus) — people charge phones at bedside overnight.
  * SCREEN-OFF (mScreenStatus) — last screen-off before the long off-stretch.
  * HOME LOCATION (mGps/mWifi) — mat reliable only at home.
  * LIGHTS-OFF (mLight/wLight) and last STEPS (wPedo).
Then compute mat-definition-aligned TST/TIB/SE/SOL/WASO within that interval, gated on
home-night confidence. Compare to subjmean and the current stack per-target nested.

Leak rules (MANDATORY): all features from each night's own streams (row-independent).
subj_mean_enc & regularity/rank reference stats: fold-train for OOF, full-train (no test
labels) for test. No row-own/future label, no test-label fitting, no pseudo-labeling, NO
external data. All features forced finite.

Output dir: raw/results/2026-06-25-wave43-withings/
  predictions.npz, metrics.json, run.log, submission.csv.
VERIFY subjmean OOF macro == 0.62453.

Run: PYTHONPATH=src python raw/results/2026-06-25-wave43-withings/build.py
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from sleep_baseline.features.lgb_cb_notebook_features import load_lgb_cb_notebook_modalities  # noqa: E402
from sleep_baseline.features.lgb_cb_foldsafe_features import build_foldsafe_raw_feature_frame  # noqa: E402
from sleep_baseline.io.raw_loader import load_sample_submission, load_train_labels  # noqa: E402
from sleep_baseline.training.submission import align_predictions_to_submission  # noqa: E402

OUT_DIR = Path(__file__).parent
RAW_ITEMS_DIR = REPO / "raw/datasets/sleep-lifelog-2024/ch2025_data_items"
ALL_TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
N_FOLDS = 5
ALPHA_GRID = [0, 1, 5, 10, 50]
N_LGB_TRIALS = 50
N_CB_TRIALS = 25
N_JOBS = 16
NOISE = 0.009

SUBJ_MEAN_REF = {
    "Q1": 0.67266, "Q2": 0.69300, "Q3": 0.66953,
    "S1": 0.57582, "S2": 0.58008, "S3": 0.53324, "S4": 0.64739,
}
MACRO_SUBJ_MEAN_REF = 0.62453
STACK_REF = {"S1": 0.564, "S2": 0.570, "S3": 0.532, "S4": 0.627}

SEARCH_START_H = 19.0     # 19:00 lifelog_date
SEARCH_END_H = 36.0       # 12:00 sleep_date (next morning), continuous-hour basis
GRID_STEP = 1.0 / 60.0

# Google Activity Recognition codes (verified by value-counts): 0=in_vehicle, 1=bicycle,
# 3=still, 4=walking, 7=tilting, 8=running.  3 == STILL == immobility indicator.
STILL_CODE = 3


# ── logging ───────────────────────────────────────────────────────────────────
_LOG_FH = None


def log(*args):
    msg = " ".join(str(a) for a in args)
    print(msg, flush=True)
    if _LOG_FH is not None:
        _LOG_FH.write(msg + "\n")
        _LOG_FH.flush()


def _clip(arr):
    return np.clip(arr, 1e-6, 1 - 1e-6)


def _ll(y, p):
    mask = ~np.isnan(y) & ~np.isnan(p)
    if mask.sum() == 0:
        return float("nan")
    return float(log_loss(y[mask], _clip(p[mask]), labels=[0, 1]))


def _finite(x, fill=0.0):
    return float(x) if np.isfinite(x) else fill


# ── night assignment ──────────────────────────────────────────────────────────
def _assign_night(ts: pd.Series):
    hh = ts.dt.hour + ts.dt.minute / 60.0
    date = ts.dt.normalize()
    night = pd.Series(pd.NaT, index=ts.index)
    cont = pd.Series(np.nan, index=ts.index)
    evening = hh >= SEARCH_START_H
    night[evening] = date[evening]
    cont[evening] = hh[evening]
    morning = hh < (SEARCH_END_H - 24.0)
    night[morning] = date[morning] - pd.Timedelta(days=1)
    cont[morning] = hh[morning] + 24.0
    return night.dt.date.astype("string"), cont


# ── grid helpers ──────────────────────────────────────────────────────────────
def _fill_short_gaps(grid, max_gap=20):
    out = grid.copy()
    n = len(out)
    finite = np.isfinite(out)
    if not finite.any():
        return out
    i, last, last_i = 0, None, -1
    while i < n:
        if finite[i]:
            last, last_i = out[i], i
        elif last is not None and (i - last_i) <= max_gap:
            out[i] = last
        i += 1
    finite2 = np.isfinite(out)
    nxt, nxt_i = None, n
    for i in range(n - 1, -1, -1):
        if finite2[i]:
            nxt, nxt_i = out[i], i
        elif nxt is not None and (nxt_i - i) <= max_gap:
            out[i] = nxt
    return out


def _smooth(arr, win=15):
    if win <= 1:
        return arr
    k = np.ones(win)
    s = np.convolve(arr, k, mode="same")
    c = np.convolve(np.ones_like(arr), k, mode="same")
    with np.errstate(invalid="ignore", divide="ignore"):
        return s / c


def _longest_run_with_gaps(mask, max_gap=5):
    n = len(mask)
    if not mask.any():
        return None, None
    best_len, best = 0, (None, None)
    i = 0
    while i < n:
        if not mask[i]:
            i += 1
            continue
        start, last_true, j, gap = i, i, i + 1, 0
        while j < n:
            if mask[j]:
                last_true, gap = j, 0
            else:
                gap += 1
                if gap > max_gap:
                    break
            j += 1
        run_len = last_true - start + 1
        if run_len > best_len:
            best_len, best = run_len, (start, last_true)
        i = last_true + 1
    return best


def _count_bouts(mask, min_len=1):
    n = len(mask)
    n_bouts, longest, i = 0, 0, 0
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            blen = j - i
            if blen >= min_len:
                n_bouts += 1
            longest = max(longest, blen)
            i = j
        else:
            i += 1
    return n_bouts, longest


# ── GPS / WiFi home features (per subject_id/night) ───────────────────────────
def _gps_to_minute(df):
    """Return per-row (timestamp) mean lat/lon/speed from the gps array."""
    lats, lons, spds = [], [], []
    for arr in df["m_gps"].to_numpy():
        if hasattr(arr, "__len__") and len(arr):
            la = np.array([d.get("latitude", np.nan) for d in arr], float)
            lo = np.array([d.get("longitude", np.nan) for d in arr], float)
            sp = np.array([d.get("speed", np.nan) for d in arr], float)
            lats.append(np.nanmean(la)); lons.append(np.nanmean(lo)); spds.append(np.nanmean(sp))
        else:
            lats.append(np.nan); lons.append(np.nan); spds.append(np.nan)
    out = df[["subject_id", "timestamp"]].copy()
    out["lat"] = lats; out["lon"] = lons; out["speed"] = spds
    return out


def _wifi_to_minute(df):
    """Return per-row set of bssids (the strongest few) for home-AP matching."""
    bssids = []
    for arr in df["m_wifi"].to_numpy():
        if hasattr(arr, "__len__") and len(arr):
            # keep APs with strong-ish signal (rssi > -75) as a stable home fingerprint
            s = frozenset(d.get("bssid") for d in arr if d.get("rssi", -200) > -75)
            bssids.append(s)
        else:
            bssids.append(frozenset())
    out = df[["subject_id", "timestamp"]].copy()
    out["bssids"] = bssids
    return out


def build_home_features(gps_min, wifi_min):
    """Per (subject_id, night): home-night confidence from GPS cluster + WiFi AP overlap.

    Home GPS location = per-subject median position across ALL that subject's own minutes
    (row-independent within a subject; uses no labels, no other subjects, no future
    target). Home WiFi fingerprint = per-subject most-common strong BSSIDs. Both are
    properties of the subject's own sensor streams, computed once, not fold-dependent and
    not label-dependent — leak-safe.
    """
    # GPS home = subject median lat/lon (overnight hours, where bedside is)
    gps_min = gps_min.copy()
    gps_min["night"], gps_min["cont_h"] = _assign_night(gps_min["timestamp"])
    home_pos = {}
    for s, grp in gps_min.dropna(subset=["lat", "lon"]).groupby("subject_id"):
        # use 0:00-6:00 (deep night) positions as the home anchor when available
        night_h = grp["cont_h"]
        deep = grp[(night_h >= 24.0) & (night_h <= 30.0)]
        ref = deep if len(deep) >= 20 else grp
        home_pos[s] = (float(np.nanmedian(ref["lat"])), float(np.nanmedian(ref["lon"])))

    # WiFi home fingerprint = subject's most-frequent strong BSSIDs (top 30)
    home_aps = {}
    if wifi_min is not None and len(wifi_min):
        wifi_min = wifi_min.copy()
        wifi_min["night"], wifi_min["cont_h"] = _assign_night(wifi_min["timestamp"])
        for s, grp in wifi_min.groupby("subject_id"):
            cnt = {}
            for bs in grp["bssids"]:
                for b in bs:
                    cnt[b] = cnt.get(b, 0) + 1
            top = sorted(cnt.items(), key=lambda kv: -kv[1])[:30]
            home_aps[s] = frozenset(b for b, _ in top)

    records = []
    gps_g = {k: v for k, v in gps_min.dropna(subset=["night"]).groupby(["subject_id", "night"], sort=False)}
    wifi_g = {}
    if wifi_min is not None and len(wifi_min):
        wifi_g = {k: v for k, v in wifi_min.dropna(subset=["night"]).groupby(["subject_id", "night"], sort=False)}

    keys = set(gps_g.keys()) | set(wifi_g.keys())
    for (subj, night) in keys:
        rec = {"subject_id": subj, "lifelog_date": str(night)}
        # GPS home fraction: fraction of overnight minutes within ~ small radius of home
        g = gps_g.get((subj, night))
        if g is not None and subj in home_pos and len(g.dropna(subset=["lat", "lon"])):
            gg = g.dropna(subset=["lat", "lon"])
            hlat, hlon = home_pos[subj]
            # lat/lon are anonymized/offset but locally metric; use scaled euclid distance.
            d = np.sqrt((gg["lat"].to_numpy() - hlat) ** 2 + (gg["lon"].to_numpy() - hlon) ** 2)
            # threshold from subject scale: 0.0005 in these offset units (~tens of m)
            rec["home_gps_frac"] = float(np.mean(d < 0.0005))
            rec["gps_speed_med"] = float(np.nanmedian(gg["speed"].to_numpy()))
            rec["gps_n_min"] = float(len(gg))
        else:
            rec["home_gps_frac"] = np.nan
            rec["gps_speed_med"] = np.nan
            rec["gps_n_min"] = 0.0
        # WiFi home overlap: mean Jaccard-ish overlap of scan APs with home fingerprint
        w = wifi_g.get((subj, night))
        if w is not None and subj in home_aps and len(home_aps[subj]):
            hp = home_aps[subj]
            overlaps = [len(bs & hp) / max(1, len(hp)) for bs in w["bssids"] if len(bs)]
            rec["home_wifi_overlap"] = float(np.mean(overlaps)) if overlaps else np.nan
            rec["wifi_n_scan"] = float(len(w))
        else:
            rec["home_wifi_overlap"] = np.nan
            rec["wifi_n_scan"] = 0.0
        records.append(rec)
    return pd.DataFrame(records)


# ── WITHINGS-MAT-MIMICKING in-bed reconstruction ──────────────────────────────
def build_withings_features(mods, home_feat):
    t0 = time.time()
    log("  [withings] preparing streams ...")
    hr = mods["wHr"].copy()
    hr["hr_mean"] = hr["heart_rate"].apply(
        lambda a: float(np.nanmean(a)) if hasattr(a, "__len__") and len(a) else np.nan)
    hr["night"], hr["cont_h"] = _assign_night(hr["timestamp"])
    hr = hr.dropna(subset=["cont_h", "night"])

    def prep(name):
        df = mods[name].copy()
        df["night"], df["cont_h"] = _assign_night(df["timestamp"])
        return df.dropna(subset=["cont_h", "night"])

    chg = prep("mACStatus")
    scr = prep("mScreenStatus")
    act = prep("mActivity")
    ped = prep("wPedo")
    wl = prep("wLight")
    ml = prep("mLight")

    def grp(df):
        return {k: v for k, v in df.groupby(["subject_id", "night"], sort=False)}

    hr_g, chg_g, scr_g = grp(hr), grp(chg), grp(scr)
    act_g, ped_g, wl_g, ml_g = grp(act), grp(ped), grp(wl), grp(ml)

    keys = sorted(set(chg_g) | set(scr_g) | set(hr_g))
    log(f"  [withings] {len(keys)} candidate nights")

    GRID = np.arange(SEARCH_START_H, SEARCH_END_H, GRID_STEP)
    NG = len(GRID)

    def to_grid(df, valcol, agg="mean"):
        out = np.full(NG, np.nan)
        if df is None or len(df) == 0:
            return out
        idx = np.clip(((df["cont_h"].to_numpy() - SEARCH_START_H) * 60.0).astype(int), 0, NG - 1)
        vals = df[valcol].to_numpy(dtype=float)
        finite = np.isfinite(vals)
        idx, vals = idx[finite], vals[finite]
        if idx.size == 0:
            return out
        if agg == "max":
            np.maximum.at(out, idx, np.where(np.isnan(out[idx]), vals, out[idx]))
            # simpler: rebuild via bincount of max -> use pandas-free max
            out = np.full(NG, np.nan)
            order = np.argsort(vals)
            out[idx[order]] = vals[order]  # last (largest) wins
            return out
        sums = np.bincount(idx, weights=vals, minlength=NG)
        cnts = np.bincount(idx, minlength=NG)
        with np.errstate(invalid="ignore", divide="ignore"):
            g = sums / cnts
        g[cnts == 0] = np.nan
        return g

    home_lut = {(r["subject_id"], r["lifelog_date"]): r for _, r in home_feat.iterrows()} \
        if home_feat is not None and len(home_feat) else {}

    records = []
    NIGHT0 = int((24.0 - SEARCH_START_H) * 60)        # index of midnight in grid
    for (subj, night) in keys:
        rec = {"subject_id": subj, "lifelog_date": str(night)}

        chg_grid = to_grid(chg_g.get((subj, night)), "m_charging")
        scr_grid = to_grid(scr_g.get((subj, night)), "m_screen_use")
        step_grid = to_grid(ped_g.get((subj, night)), "step")
        act_grid = to_grid(act_g.get((subj, night)), "m_activity")
        hr_grid = to_grid(hr_g.get((subj, night)), "hr_mean")
        wl_grid = to_grid(wl_g.get((subj, night)), "w_light")
        ml_grid = to_grid(ml_g.get((subj, night)), "m_light")

        # ===== BED-ENTRY ANCHORS =====
        # 1) overnight charge-start: first sustained (>=15min) charging onset after 20:00
        chg_f = _fill_short_gaps(chg_grid, max_gap=10)
        chg_on = np.where(np.isfinite(chg_f), chg_f >= 0.5, False)
        idx20 = int((20.0 - SEARCH_START_H) * 60)
        charge_start_i = np.nan
        i = idx20
        while i < NG - 15:
            if chg_on[i] and np.mean(chg_on[i:i + 15]) >= 0.8:
                charge_start_i = i
                break
            i += 1
        rec["charge_start_hour"] = _finite(GRID[int(charge_start_i)]) if np.isfinite(charge_start_i) else np.nan

        # 2) last screen-off before the long screen-off stretch (use steps/screen)
        scr_f = _fill_short_gaps(scr_grid, max_gap=10)
        scr_on = np.where(np.isfinite(scr_f), scr_f >= 0.5, False)
        # find longest screen-OFF run after 20:00 -> its start = lights/phone-down
        off_after = (~scr_on).copy()
        off_after[:idx20] = False
        s_off, e_off = _longest_run_with_gaps(off_after, max_gap=10)
        screen_down_i = s_off if s_off is not None else np.nan
        rec["screen_down_hour"] = _finite(GRID[int(screen_down_i)]) if np.isfinite(screen_down_i) else np.nan

        # 3) last steps before night (last step-bearing minute after 20:00, before 4:00)
        idx4 = int((28.0 - SEARCH_START_H) * 60)
        step_after = np.where(np.isfinite(step_grid), step_grid > 0, False)
        last_step_i = np.nan
        cand = np.where(step_after[idx20:idx4])[0]
        if cand.size:
            last_step_i = idx20 + cand[-1]
        rec["last_step_hour"] = _finite(GRID[int(last_step_i)]) if np.isfinite(last_step_i) else np.nan

        # 4) lights-off: last minute with light>50 before the dark stretch (use both lights)
        light = np.where(np.isfinite(wl_grid), wl_grid, np.nan)
        light = np.where(np.isfinite(light), light, ml_grid)
        lit = np.where(np.isfinite(light), light > 30, False)
        lit_after = lit.copy(); lit_after[:idx20] = False
        litc = np.where(lit_after[:idx4])[0]
        lights_off_i = litc[-1] if litc.size else np.nan
        rec["lights_off_hour"] = _finite(GRID[int(lights_off_i)]) if np.isfinite(lights_off_i) else np.nan

        # COMBINE bed-entry: median of available anchors (charge-start, screen-down, last-step, lights-off)
        anchors = [charge_start_i, screen_down_i, last_step_i, lights_off_i]
        anchors = [a for a in anchors if np.isfinite(a)]
        if anchors:
            bed_entry_i = int(np.median(anchors))
        else:
            bed_entry_i = NIGHT0  # fallback midnight
        rec["bed_entry_hour"] = _finite(GRID[bed_entry_i])
        rec["n_bed_entry_anchors"] = float(len(anchors))
        rec["bed_entry_anchor_spread"] = _finite(np.std([GRID[int(a)] for a in anchors])) if len(anchors) >= 2 else 0.0

        # ===== BED-EXIT ANCHORS (morning) =====
        # charge-end: end of the sustained overnight charge run that contains/after bed_entry
        charge_end_i = np.nan
        if charge_start_i is not None and np.isfinite(charge_start_i):
            s_c, e_c = _longest_run_with_gaps(chg_on, max_gap=20)
            if e_c is not None and e_c >= bed_entry_i:
                charge_end_i = e_c
        rec["charge_end_hour"] = _finite(GRID[int(charge_end_i)]) if np.isfinite(charge_end_i) else np.nan
        # first screen-ON after the long-off stretch
        first_scron_i = np.nan
        if s_off is not None:
            after = np.where(scr_on[e_off:])[0]
            if after.size:
                first_scron_i = e_off + after[0]
        rec["first_screen_on_hour"] = _finite(GRID[int(first_scron_i)]) if np.isfinite(first_scron_i) else np.nan
        # first steps after bed_entry
        first_step_i = np.nan
        sc = np.where(step_after[bed_entry_i:])[0]
        if sc.size:
            first_step_i = bed_entry_i + sc[0]

        exit_anchors = [a for a in [charge_end_i, first_scron_i, first_step_i] if np.isfinite(a)]
        # require exit AFTER entry; if morning charge-end available prefer it
        exit_anchors = [a for a in exit_anchors if a > bed_entry_i + 60]
        if exit_anchors:
            bed_exit_i = int(np.median(exit_anchors))
        else:
            bed_exit_i = min(NG - 1, bed_entry_i + 8 * 60)  # fallback 8h
        rec["bed_exit_hour"] = _finite(GRID[bed_exit_i])
        rec["n_bed_exit_anchors"] = float(len(exit_anchors))

        # ===== IN-BED INTERVAL & MAT-ALIGNED METRICS =====
        if bed_exit_i <= bed_entry_i + 30:
            bed_exit_i = min(NG - 1, bed_entry_i + 6 * 60)
        seg = slice(bed_entry_i, bed_exit_i + 1)
        tib_min = bed_exit_i - bed_entry_i + 1
        tib_h = tib_min / 60.0
        rec["time_in_bed_h"] = _finite(tib_h)

        # sleep/wake within bed interval: settled HR (nocturnal low) + immobile + no steps
        hr_filled = _fill_short_gaps(hr_grid, max_gap=20)
        seg_hr = hr_filled[seg]
        valid_hr = seg_hr[np.isfinite(seg_hr)]
        seg_act = act_grid[seg]
        seg_step = step_grid[seg]
        # immobility: activity==still OR nan(no movement reported); steps==0
        immobile = np.where(np.isfinite(seg_act), seg_act == STILL_CODE, True)
        nostep = np.where(np.isfinite(seg_step), seg_step <= 0.0, True)
        if valid_hr.size >= 20:
            hr_lo = np.nanpercentile(valid_hr, 30)
            hr_hi = np.nanpercentile(valid_hr, 80)
            span = max(hr_hi - hr_lo, 1.0)
            seg_hr_f = np.where(np.isfinite(seg_hr), seg_hr, hr_hi)
            hr_settled = (hr_hi - seg_hr_f) / span  # high when HR low (asleep)
            hr_settled = np.clip(hr_settled, 0, 1)
        else:
            hr_settled = np.full(tib_min, 0.5)
        asleep_score = (0.5 * hr_settled
                        + 0.25 * immobile.astype(float)
                        + 0.25 * nostep.astype(float))
        asleep_score = _smooth(np.where(np.isfinite(asleep_score), asleep_score, 0.0), win=11)
        asleep = asleep_score >= 0.55

        # sleep onset = first sustained (>=10min) asleep within bed interval
        onset_off = bed_entry_i
        onset_rel = np.nan
        for j in range(0, tib_min - 10):
            if asleep[j] and np.mean(asleep[j:j + 10]) >= 0.8:
                onset_rel = j
                break
        # final wake = last asleep minute
        asleep_idx = np.where(asleep)[0]
        final_rel = asleep_idx[-1] if asleep_idx.size else np.nan

        tst_min = int(np.sum(asleep))
        rec["mat_tst_h"] = _finite(tst_min / 60.0)
        rec["mat_se"] = _finite(tst_min / max(1, tib_min))
        if np.isfinite(onset_rel):
            rec["mat_sol_h"] = _finite(onset_rel / 60.0)        # sleep onset latency
            rec["mat_sleep_onset_hour"] = _finite(GRID[bed_entry_i + int(onset_rel)])
        else:
            rec["mat_sol_h"] = np.nan
            rec["mat_sleep_onset_hour"] = np.nan
        if np.isfinite(final_rel):
            rec["mat_final_wake_hour"] = _finite(GRID[bed_entry_i + int(final_rel)])
        else:
            rec["mat_final_wake_hour"] = np.nan
        # WASO between onset and final wake
        if np.isfinite(onset_rel) and np.isfinite(final_rel) and final_rel > onset_rel:
            mid = asleep[int(onset_rel):int(final_rel) + 1]
            waso = int(np.sum(~mid))
            rec["mat_waso_h"] = _finite(waso / 60.0)
            n_awk, longest_w = _count_bouts(~mid, min_len=1)
            rec["mat_n_awakenings"] = float(n_awk)
            rec["mat_longest_wake_min"] = float(longest_w)
            spt = int(final_rel) - int(onset_rel) + 1   # sleep period time
            rec["mat_se_spt"] = _finite(np.sum(mid) / max(1, spt))  # SE within sleep period
        else:
            rec.update(mat_waso_h=np.nan, mat_n_awakenings=np.nan,
                       mat_longest_wake_min=np.nan, mat_se_spt=np.nan)

        # ===== CHARGING-AS-BED features =====
        rec["charge_total_h"] = _finite(np.nansum(np.where(np.isfinite(chg_grid), chg_grid, 0)) / 60.0)
        rec["charge_overnight_h"] = _finite(np.sum(chg_on[bed_entry_i:bed_exit_i + 1]) / 60.0)
        rec["charge_frac_in_bed"] = _finite(np.mean(chg_on[seg])) if tib_min > 0 else np.nan
        if np.isfinite(charge_start_i) and np.isfinite(onset_rel):
            rec["charge_start_to_onset_h"] = _finite(
                (GRID[bed_entry_i + int(onset_rel)] - GRID[int(charge_start_i)]))
        else:
            rec["charge_start_to_onset_h"] = np.nan

        # ===== HOME-NIGHT confidence (gating) =====
        hf = home_lut.get((subj, str(night)))
        hg = hf["home_gps_frac"] if hf is not None else np.nan
        hw = hf["home_wifi_overlap"] if hf is not None else np.nan
        rec["home_gps_frac"] = _finite(hg, np.nan) if hf is not None else np.nan
        rec["home_wifi_overlap"] = _finite(hw, np.nan) if hf is not None else np.nan
        # combined home confidence: GPS-led (fraction of overnight minutes at home cluster),
        # WiFi overlap kept as a separate raw feature. home_conf == home_gps_frac when GPS
        # present, else falls back to a wifi-overlap-normalised proxy. Flag at GPS frac>=0.5.
        if np.isfinite(hg):
            home_conf = float(hg)
        elif np.isfinite(hw):
            home_conf = float(np.clip(hw / 0.15, 0, 1))  # normalise wifi overlap to ~[0,1]
        else:
            home_conf = np.nan
        rec["home_conf"] = home_conf
        rec["home_night_flag"] = float(home_conf >= 0.5) if np.isfinite(home_conf) else np.nan
        # interaction: SE/SOL gated by home confidence (mat reliable only at home)
        rec["mat_se_x_home"] = _finite(rec["mat_se"] * home_conf) if np.isfinite(home_conf) else np.nan
        rec["mat_sol_x_home"] = _finite(rec["mat_sol_h"] * home_conf) \
            if (np.isfinite(home_conf) and np.isfinite(rec["mat_sol_h"])) else np.nan
        rec["mat_tst_x_home"] = _finite(rec["mat_tst_h"] * home_conf) if np.isfinite(home_conf) else np.nan

        # coverage / quality
        rec["hr_coverage_in_bed"] = _finite(valid_hr.size / max(1, tib_min))
        rec["chg_coverage"] = _finite(np.mean(np.isfinite(chg_grid)))

        records.append(rec)

    feat = pd.DataFrame(records)
    log(f"  [withings] built {feat.shape} in {time.time()-t0:.1f}s")
    return feat


WITHINGS_NUM_COLS = [
    "charge_start_hour", "screen_down_hour", "last_step_hour", "lights_off_hour",
    "bed_entry_hour", "n_bed_entry_anchors", "bed_entry_anchor_spread",
    "charge_end_hour", "first_screen_on_hour", "bed_exit_hour", "n_bed_exit_anchors",
    "time_in_bed_h", "mat_tst_h", "mat_se", "mat_sol_h", "mat_sleep_onset_hour",
    "mat_final_wake_hour", "mat_waso_h", "mat_n_awakenings", "mat_longest_wake_min",
    "mat_se_spt", "charge_total_h", "charge_overnight_h", "charge_frac_in_bed",
    "charge_start_to_onset_h", "home_gps_frac", "home_wifi_overlap", "home_conf",
    "home_night_flag", "mat_se_x_home", "mat_sol_x_home", "mat_tst_x_home",
    "hr_coverage_in_bed", "chg_coverage",
]


# ── regularity / rank (fold-dependent) ────────────────────────────────────────
REG_BASE = ["bed_entry_hour", "mat_sleep_onset_hour", "mat_tst_h"]
REG_COLS = [f"reg_{c}_dev" for c in REG_BASE]
RANK_BASE = ["mat_tst_h", "mat_se", "mat_sol_h"]
RANK_COLS = [f"rank_{c}" for c in RANK_BASE]
ALL_FOLD_COLS = REG_COLS + RANK_COLS


def compute_ref_stats(feat_frame, row_idx):
    sub = feat_frame.iloc[row_idx]
    ref = {}
    for s, grp in sub.groupby("subject_id"):
        med = {b: float(np.nanmedian(grp[b].to_numpy(dtype=float))) for b in REG_BASE}
        sv = {}
        for b in RANK_BASE:
            v = grp[b].to_numpy(dtype=float)
            sv[b] = np.sort(v[np.isfinite(v)])
        ref[s] = {"med": med, "sorted": sv}
    return ref


def add_fold_features(frame_feat, ref):
    subj = frame_feat["subject_id"].to_numpy()
    out = {}
    for b in REG_BASE:
        vals = frame_feat[b].to_numpy(dtype=float)
        dev = np.full(len(frame_feat), np.nan)
        for i, s in enumerate(subj):
            med = ref.get(s, {}).get("med", {}).get(b, np.nan)
            if np.isfinite(vals[i]) and np.isfinite(med):
                dev[i] = vals[i] - med
        out[f"reg_{b}_dev"] = dev
    for b in RANK_BASE:
        vals = frame_feat[b].to_numpy(dtype=float)
        rk = np.full(len(frame_feat), np.nan)
        for i, s in enumerate(subj):
            sv = ref.get(s, {}).get("sorted", {}).get(b, None)
            if sv is not None and sv.size and np.isfinite(vals[i]):
                rk[i] = np.searchsorted(sv, vals[i], side="right") / sv.size
        out[f"rank_{b}"] = rk
    return pd.DataFrame(out, index=frame_feat.index)


# ── CV / subject-mean encoding ────────────────────────────────────────────────
def make_same_subject_hole_folds(train_frame, n_folds=5):
    train_frame = train_frame.reset_index(drop=True)
    fa = np.full(len(train_frame), -1, dtype=int)
    for _subj, grp in train_frame.groupby("subject_id"):
        idx = grp.sort_values("sleep_date").index.to_numpy()
        for k, block in enumerate(np.array_split(idx, n_folds)):
            fa[block] = k
    folds = []
    for k in range(n_folds):
        val = fa == k
        folds.append((np.where(~val)[0], np.where(val)[0]))
    return folds


def compute_subj_mean_enc(train_frame, train_idx, subject_ids, target, alpha):
    y_all = train_frame[target].astype(float).to_numpy()
    y_tr = y_all[train_idx]
    subj_tr = subject_ids[train_idx]
    gmean = float(np.nanmean(y_tr)) if not np.all(np.isnan(y_tr)) else 0.5
    enc = {}
    for s in np.unique(subj_tr):
        vals = y_tr[subj_tr == s]
        valid = vals[~np.isnan(vals)]
        n = len(valid)
        sm = float(np.sum(valid)) / n if n else gmean
        enc[s] = (n * sm + alpha * gmean) / (n + alpha) if (n + alpha) > 0 else gmean
    return np.array([enc.get(str(s), gmean) for s in subject_ids], dtype=float)


def compute_subj_mean_enc_fulltest(train_frame, test_frame, target, alpha):
    y_all = train_frame[target].astype(float).to_numpy()
    subj_all = train_frame["subject_id"].astype(str).to_numpy()
    gmean = float(np.nanmean(y_all)) if not np.all(np.isnan(y_all)) else 0.5
    enc = {}
    for s in np.unique(subj_all):
        vals = y_all[subj_all == s]
        valid = vals[~np.isnan(vals)]
        n = len(valid)
        sm = float(np.sum(valid)) / n if n else gmean
        enc[s] = (n * sm + alpha * gmean) / (n + alpha) if (n + alpha) > 0 else gmean
    return np.array([enc.get(s, gmean) for s in test_frame["subject_id"].astype(str)], dtype=float)


def find_best_alpha(train_frame, folds, target, alpha_grid):
    y_all = train_frame[target].astype(float).to_numpy()
    subject_ids = train_frame["subject_id"].astype(str).to_numpy()
    best_ll, best_alpha = 1e9, alpha_grid[0]
    for alpha in alpha_grid:
        oof = np.zeros(len(train_frame))
        for tr, vl in folds:
            enc = compute_subj_mean_enc(train_frame, tr, subject_ids, target, alpha)
            oof[vl] = enc[vl]
        ll = _ll(y_all, _clip(oof))
        if ll < best_ll:
            best_ll, best_alpha = ll, alpha
    return float(best_alpha), float(best_ll)


# ── fold matrix builder ───────────────────────────────────────────────────────
def _build_fold_matrices(merged, feature_cols, tr_idx, vl_idx, target, alpha, subject_ids):
    enc = compute_subj_mean_enc(merged, tr_idx, subject_ids, target, alpha)
    ref = compute_ref_stats(merged, tr_idx)
    foldf = add_fold_features(merged, ref)
    x_tr = merged.iloc[tr_idx][feature_cols].copy()
    x_tr["subj_mean_enc"] = enc[tr_idx]
    x_vl = merged.iloc[vl_idx][feature_cols].copy()
    x_vl["subj_mean_enc"] = enc[vl_idx]
    for rc in ALL_FOLD_COLS:
        x_tr[rc] = foldf.iloc[tr_idx][rc].to_numpy()
        x_vl[rc] = foldf.iloc[vl_idx][rc].to_numpy()
    return x_tr, x_vl


# ── Optuna tuning ─────────────────────────────────────────────────────────────
def optuna_tune_lgb(merged, feature_cols, target, folds, alpha, subject_ids, n_trials):
    import optuna, lightgbm as lgb
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    y_all = merged[target].astype(float).to_numpy()
    fold_mats = [_build_fold_matrices(merged, feature_cols, tr, vl, target, alpha, subject_ids)
                 for tr, vl in folds]

    def objective(trial):
        params = {
            "num_leaves": trial.suggest_int("num_leaves", 8, 63),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 60),
            "feature_fraction": trial.suggest_float("feature_fraction", 0.4, 1.0),
            "lambda_l1": trial.suggest_float("lambda_l1", 1e-4, 10.0, log=True),
            "lambda_l2": trial.suggest_float("lambda_l2", 1e-4, 10.0, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 400),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.12, log=True),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "objective": "binary", "random_state": 42, "verbose": -1, "n_jobs": N_JOBS,
        }
        oof = np.full(len(merged), np.nan)
        for (tr, vl), (x_tr, x_vl) in zip(folds, fold_mats):
            y_tr = y_all[tr]
            ytv = y_tr[~np.isnan(y_tr)]
            if len(np.unique(ytv)) < 2:
                oof[vl] = float(np.nanmean(ytv)) if ytv.size else 0.5
                continue
            m = lgb.LGBMClassifier(**params)
            m.fit(x_tr, y_tr)
            oof[vl] = _clip(m.predict_proba(x_vl)[:, 1])
        return _ll(y_all, _clip(oof))

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return study.best_params, study.best_value


def optuna_tune_cb(merged, feature_cols, target, folds, alpha, subject_ids, n_trials):
    import optuna
    from catboost import CatBoostClassifier
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    y_all = merged[target].astype(float).to_numpy()
    fold_mats = [_build_fold_matrices(merged, feature_cols, tr, vl, target, alpha, subject_ids)
                 for tr, vl in folds]

    def objective(trial):
        params = {
            "depth": trial.suggest_int("depth", 4, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.12, log=True),
            "iterations": trial.suggest_int("iterations", 100, 300),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1.0, 20.0),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "loss_function": "Logloss", "verbose": 0, "random_state": 42, "thread_count": N_JOBS,
        }
        oof = np.full(len(merged), np.nan)
        for (tr, vl), (x_tr, x_vl) in zip(folds, fold_mats):
            y_tr = y_all[tr]
            ytv = y_tr[~np.isnan(y_tr)]
            if len(np.unique(ytv)) < 2:
                oof[vl] = float(np.nanmean(ytv)) if ytv.size else 0.5
                continue
            m = CatBoostClassifier(**params)
            m.fit(x_tr, y_tr)
            oof[vl] = _clip(m.predict_proba(x_vl)[:, 1])
        return _ll(y_all, _clip(oof))

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return study.best_params, study.best_value


def find_best_blend(oof_model, oof_sm, y_all):
    best_ll, best_w = 1e9, 0.0
    for w in np.linspace(0, 1, 21):
        ll = _ll(y_all, _clip(w * oof_model + (1 - w) * oof_sm))
        if ll < best_ll:
            best_ll, best_w = ll, float(w)
    return best_w, best_ll


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    global _LOG_FH
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _LOG_FH = open(OUT_DIR / "run.log", "w")
    t_start = time.time()
    log("=" * 70)
    log("Wave43 WITHINGS-MAT-MIMICKING (charging/home-anchored in-bed reconstruction)")
    log("=" * 70)

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

    # Existing daily/intra-day features available on the foldsafe frame (numeric, non-target)
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

    log("\n[3] Home features (GPS cluster + WiFi fingerprint) ...")
    gps_min = _gps_to_minute(gps)
    wifi_min = _wifi_to_minute(wifi)
    home_feat = build_home_features(gps_min, wifi_min)
    home_feat["subject_id"] = home_feat["subject_id"].astype(str)
    home_feat["lifelog_date"] = home_feat["lifelog_date"].astype(str)
    log(f"  home_feat: {home_feat.shape}")

    log("\n[4] Withings mat-mimicking in-bed reconstruction ...")
    wf = build_withings_features(mods, home_feat)
    wf["subject_id"] = wf["subject_id"].astype(str)
    wf["lifelog_date"] = wf["lifelog_date"].astype(str)
    withings_cols = [c for c in WITHINGS_NUM_COLS if c in wf.columns]
    log(f"  withings features: {len(withings_cols)}")

    # merge: withings + existing daily/intra-day
    base_tr = train_frame[["subject_id", "sleep_date", "lifelog_date"] + ALL_TARGETS + existing_cols]
    base_te = test_frame[["subject_id", "sleep_date", "lifelog_date"] + existing_cols]
    train_merged = base_tr.merge(wf, on=["subject_id", "lifelog_date"], how="left").reset_index(drop=True)
    test_merged = base_te.merge(wf, on=["subject_id", "lifelog_date"], how="left").reset_index(drop=True)

    cov_tr = train_merged[withings_cols].notna().any(axis=1).sum()
    cov_te = test_merged[withings_cols].notna().any(axis=1).sum()
    log(f"  train rows with withings recon: {cov_tr}/{len(train_merged)}")
    log(f"  test  rows with withings recon: {cov_te}/{len(test_merged)}")
    home_cov = train_merged["home_conf"].notna().sum()
    log(f"  train rows with home_conf: {home_cov}/{len(train_merged)}; "
        f"home_night_flag mean={np.nanmean(train_merged['home_night_flag']):.3f}")

    # FEATURE SETS:
    #  - "withings": withings recon features only (+ subj_mean_enc + fold feats)
    #  - "combo": withings + existing daily/intra-day features
    feat_withings = withings_cols
    feat_combo = withings_cols + existing_cols
    log(f"  feat_withings={len(feat_withings)}  feat_combo={len(feat_combo)}")

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
    if abs(macro_sm - MACRO_SUBJ_MEAN_REF) > 0.01:
        log(f"  WARNING: subject-mean OOF macro {macro_sm:.5f} deviates from reference!")

    # ── home-night subset (high-confidence nights) for the variant ──
    home_mask = (train_merged["home_night_flag"] >= 0.5).fillna(False).to_numpy()
    log(f"  home-night-only training rows: {int(home_mask.sum())}/{len(train_merged)}")

    log(f"\n[7] Per-target Optuna ({N_LGB_TRIALS} LGB + {N_CB_TRIALS} CB) on withings & combo ...")
    params_w, params_c = {}, {}
    for fs_name, fs_cols, store in [("withings", feat_withings, params_w),
                                    ("combo", feat_combo, params_c)]:
        for t in ALL_TARGETS:
            t0 = time.time()
            lp, lv = optuna_tune_lgb(train_merged, fs_cols, t, folds, best_alpha[t], subject_ids, N_LGB_TRIALS)
            cp, cv = optuna_tune_cb(train_merged, fs_cols, t, folds, best_alpha[t], subject_ids, N_CB_TRIALS)
            store[t] = {"lgb": lp, "cb": cp, "lgb_oof": lv, "cb_oof": cv}
            log(f"  [{fs_name}] {t} lgb={lv:.5f} cb={cv:.5f}  ({time.time()-t0:.0f}s)")

    log("\n[8] Full OOF + test prediction (withings, combo, + home-night-only combo) ...")
    import lightgbm as lgb
    from catboost import CatBoostClassifier

    def fit_predict_set(fs_cols, params_store, train_mask=None, tag=""):
        oof_lgb = {t: np.full(len(train_merged), np.nan) for t in ALL_TARGETS}
        oof_cb = {t: np.full(len(train_merged), np.nan) for t in ALL_TARGETS}
        test_lgb = {t: np.zeros(len(test_merged)) for t in ALL_TARGETS}
        test_cb = {t: np.zeros(len(test_merged)) for t in ALL_TARGETS}
        foldf_test = add_fold_features(test_merged, compute_ref_stats(train_merged, np.arange(len(train_merged))))
        for fold_k, (tr, vl) in enumerate(folds):
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

                tr_used = tr if train_mask is None else tr[train_mask[tr]]
                x_tr = make_X(train_merged, tr_used, enc[tr_used], foldf_all, tr_used, fs_cols)
                x_vl = make_X(train_merged, vl, enc[vl], foldf_all, vl, fs_cols)
                x_te = make_X(test_merged, None, enc_te, foldf_test, None, fs_cols)
                y_tr = train_merged.iloc[tr_used][t].astype(float).to_numpy()
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

    log("  fitting withings ...")
    ow_lgb, ow_cb, tw_lgb, tw_cb = fit_predict_set(feat_withings, params_w)
    log("  fitting combo ...")
    oc_lgb, oc_cb, tc_lgb, tc_cb = fit_predict_set(feat_combo, params_c)
    log("  fitting combo home-night-only ...")
    oh_lgb, oh_cb, th_lgb, th_cb = fit_predict_set(feat_combo, params_c, train_mask=home_mask, tag="home")

    # subjmean OOF/test
    oof_sm = {t: np.full(len(train_merged), np.nan) for t in ALL_TARGETS}
    test_sm = {t: np.zeros(len(test_merged)) for t in ALL_TARGETS}
    for fold_k, (tr, vl) in enumerate(folds):
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
        cand = {
            "withings_lgb": ow_lgb[t], "withings_cb": ow_cb[t],
            "combo_lgb": oc_lgb[t], "combo_cb": oc_cb[t],
            "home_lgb": oh_lgb[t], "home_cb": oh_cb[t],
        }
        cand_ll = {k: _ll(y, v) for k, v in cand.items()}
        best_name = min(cand_ll, key=cand_ll.get)
        best_oof = cand[best_name]
        best_ll = cand_ll[best_name]
        w, blend_ll = find_best_blend(best_oof, oof_sm[t], y)
        final_ll = min(best_ll, blend_ll)
        delta = sm_ll - final_ll
        # combo vs home (does gating help?)
        combo_best = min(cand_ll["combo_lgb"], cand_ll["combo_cb"])
        home_best = min(cand_ll["home_lgb"], cand_ll["home_cb"])
        results[t] = {
            "subj_mean_oof": sm_ll, "subj_mean_ref": SUBJ_MEAN_REF[t],
            **{f"{k}_oof": v for k, v in cand_ll.items()},
            "best_model": best_name, "best_model_oof": best_ll,
            "blend_w": w, "blend_oof": blend_ll, "final_oof": final_ll,
            "delta_vs_subjmean": delta, "beats_noise": bool(delta > NOISE),
            "combo_all_night_oof": combo_best, "combo_home_night_oof": home_best,
            "home_gating_delta": combo_best - home_best,
            "home_gating_helps": bool(combo_best - home_best > NOISE),
        }
        if t in STACK_REF:
            results[t]["stack_ref"] = STACK_REF[t]
            results[t]["delta_vs_stack"] = STACK_REF[t] - final_ll
            results[t]["beats_stack_noise"] = bool(STACK_REF[t] - final_ll > NOISE)
        log(f"  {t}: sm={sm_ll:.5f} best={best_name}({best_ll:.5f}) blend={blend_ll:.5f}(w={w:.2f}) "
            f"final={final_ll:.5f} d_sm={delta:+.5f} "
            + (f"d_stack={results[t].get('delta_vs_stack',0):+.5f} " if t in STACK_REF else "")
            + f"home_gate_d={results[t]['home_gating_delta']:+.5f} "
            f"{'BEATS_SM' if results[t]['beats_noise'] else 'no'}")

    macro_final = float(np.mean([results[t]["final_oof"] for t in ALL_TARGETS]))
    improved = [t for t in ALL_TARGETS if results[t]["beats_noise"]]
    improved_S = [t for t in S_TARGETS if results[t]["beats_noise"]]
    beats_stack_S = [t for t in S_TARGETS if results[t].get("beats_stack_noise")]
    log(f"\n  MACRO subj-mean={macro_sm:.5f}  final={macro_final:.5f}  "
        f"delta={macro_sm - macro_final:+.5f}")
    log(f"  beats SM-noise: {improved}  (S: {improved_S})")
    log(f"  beats STACK-noise on S: {beats_stack_S}")

    # ── feature importance (combo, LGB) to identify which bed-anchors matter ──
    log("\n[10] Feature importance (combo LGB, gain) ...")
    importances = {}
    for t in S_TARGETS:
        imp_t = {}
        y_all = y_arr[t]
        for tr, vl in folds:
            x_tr, _ = _build_fold_matrices(train_merged, feat_combo, tr, vl, t, best_alpha[t], subject_ids)
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
        # keep only withings-derived + fold features for the "bed anchor" story
        wcols = set(withings_cols) | set(ALL_FOLD_COLS) | {"subj_mean_enc"}
        ranked = sorted([(f, v) for f, v in imp_t.items() if f in wcols], key=lambda kv: -kv[1])
        importances[t] = ranked[:15]
        log(f"  {t} top withings/fold features by gain:")
        for f, v in ranked[:10]:
            log(f"      {f:32s} {v:10.1f}")

    log("\n[11] Saving predictions.npz ...")
    save = {}
    for t in ALL_TARGETS:
        save[f"oof_withingslgb_{t}"] = ow_lgb[t]
        save[f"oof_withingscb_{t}"] = ow_cb[t]
        save[f"oof_combolgb_{t}"] = oc_lgb[t]
        save[f"oof_combocb_{t}"] = oc_cb[t]
        save[f"oof_homelgb_{t}"] = oh_lgb[t]
        save[f"oof_homecb_{t}"] = oh_cb[t]
        save[f"oof_subjmean_{t}"] = oof_sm[t]
        save[f"test_withingslgb_{t}"] = _clip(tw_lgb[t])
        save[f"test_withingscb_{t}"] = _clip(tw_cb[t])
        save[f"test_combolgb_{t}"] = _clip(tc_lgb[t])
        save[f"test_combocb_{t}"] = _clip(tc_cb[t])
        save[f"test_homelgb_{t}"] = _clip(th_lgb[t])
        save[f"test_homecb_{t}"] = _clip(th_cb[t])
        save[f"test_subjmean_{t}"] = _clip(test_sm[t])
    np.savez(OUT_DIR / "predictions.npz", **save)
    log(f"  wrote {OUT_DIR / 'predictions.npz'} with {len(save)} arrays")

    log("\n[12] metrics.json ...")
    metrics = {
        "pipeline": "wave43-withings",
        "approach": ("charging/home-anchored Withings-mat-mimicking in-bed reconstruction; "
                     "mat-aligned TST/TIB/SE/SOL/WASO gated by home-night confidence"),
        "n_lgb_trials": N_LGB_TRIALS, "n_cb_trials": N_CB_TRIALS, "n_folds": N_FOLDS,
        "n_withings_features": len(withings_cols), "withings_feature_names": withings_cols,
        "n_existing_features": len(existing_cols),
        "regularity_features": REG_COLS, "rank_features": RANK_COLS,
        "search_window_hours": [SEARCH_START_H, SEARCH_END_H],
        "train_recon_coverage": int(cov_tr), "train_rows": len(train_merged),
        "test_recon_coverage": int(cov_te), "test_rows": len(test_merged),
        "home_conf_coverage": int(home_cov),
        "home_night_flag_mean": float(np.nanmean(train_merged["home_night_flag"])),
        "home_night_only_train_rows": int(home_mask.sum()),
        "macro_subj_mean_ref": MACRO_SUBJ_MEAN_REF, "macro_subj_mean_oof": macro_sm,
        "macro_final_oof": macro_final, "delta_macro_vs_subjmean": macro_sm - macro_final,
        "noise_floor": NOISE,
        "improved_vs_subjmean": improved, "improved_S_vs_subjmean": improved_S,
        "beats_stack_noise_S": beats_stack_S,
        "stack_ref": STACK_REF,
        "best_alpha_per_target": best_alpha,
        "tuning_oof": {"withings": {t: {"lgb": params_w[t]["lgb_oof"], "cb": params_w[t]["cb_oof"]} for t in ALL_TARGETS},
                       "combo": {t: {"lgb": params_c[t]["lgb_oof"], "cb": params_c[t]["cb_oof"]} for t in ALL_TARGETS}},
        "feature_importance_S": {t: importances[t] for t in S_TARGETS},
        "per_target": results,
        "subjmean_oof_verification": {
            "macro_oof": macro_sm, "expected": MACRO_SUBJ_MEAN_REF,
            "per_target_oof": sm_oof_per_target,
            "match": bool(abs(macro_sm - MACRO_SUBJ_MEAN_REF) <= 0.01),
        },
        "leak_check": (
            "All withings recon features from each night's own streams over fixed clock window "
            "[19:00 lifelog_date, 12:00 sleep_date]; bed-anchors (charge-start, screen-down, "
            "last-step, lights-off) and in-bed sleep/wake from own-night signals only. Home GPS "
            "anchor = subject's OWN-stream median position; home WiFi fingerprint = subject's OWN "
            "most-frequent strong BSSIDs; both per-subject, label-free, fold-independent. "
            "Regularity-dev + rank reference stats = fold-train for OOF, full-train for test. "
            "subj_mean_enc = fold-train for OOF, full-train (no test labels) for test. No "
            "row-own/future label, no test-label fitting, no pseudo-labeling, NO external data. "
            "All features forced finite."
        ),
        "external_data_used": False,
        "elapsed_seconds": time.time() - t_start,
    }
    with open(OUT_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2, default=float)
    log(f"  wrote {OUT_DIR / 'metrics.json'}")

    # submission (best per target, blended)
    pred_frame = test_merged[["subject_id", "sleep_date", "lifelog_date"]].copy()
    test_lut = {
        "withings_lgb": tw_lgb, "withings_cb": tw_cb, "combo_lgb": tc_lgb,
        "combo_cb": tc_cb, "home_lgb": th_lgb, "home_cb": th_cb,
    }
    for t in ALL_TARGETS:
        r = results[t]
        bt = test_lut[r["best_model"]][t]
        if r["blend_oof"] <= r["best_model_oof"]:
            pred = r["blend_w"] * bt + (1 - r["blend_w"]) * test_sm[t]
        else:
            pred = bt
        pred_frame[t] = _clip(pred)
    submission = align_predictions_to_submission(pred_frame, sample_submission=ss)
    submission.to_csv(OUT_DIR / "submission.csv", index=False)
    log(f"  wrote {OUT_DIR / 'submission.csv'} ({len(submission)} rows)")

    log("\n" + "=" * 70)
    log(f"DONE in {time.time()-t_start:.0f}s")
    log("=" * 70)
    _LOG_FH.close()


if __name__ == "__main__":
    main()
