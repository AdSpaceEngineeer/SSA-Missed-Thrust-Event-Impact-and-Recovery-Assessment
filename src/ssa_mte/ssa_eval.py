from __future__ import annotations

import numpy as np
import pandas as pd

from ssa_mte.catalog import R_EARTH_KM
from ssa_mte.config import PhaseGuessConfig, SsaEvalConfig
from ssa_mte.phase_guess import (
    integrate_hcw_segment,
    integrate_outage_then_ballistic,
    make_phase_guess_control_fn,
)
from ssa_mte.propagation import propagate_satrec_to_times
from ssa_mte.rtn import rtn_rotation_matrix_from_state


def pareto_front(df: pd.DataFrame, objective_cols: list[str], minimize: list[bool]) -> pd.DataFrame:
    work = df.copy().reset_index(drop=True)
    obj = np.column_stack(
        [work[col].to_numpy(dtype=float) if is_min else -work[col].to_numpy(dtype=float) for col, is_min in zip(objective_cols, minimize)]
    )
    keep = np.ones(len(work), dtype=bool)
    for i in range(len(work)):
        if not keep[i]:
            continue
        dominated = np.all(obj <= obj[i], axis=1) & np.any(obj < obj[i], axis=1)
        dominated[i] = False
        if np.any(dominated):
            keep[i] = False
    return work.loc[keep].copy().reset_index(drop=True)


def select_phase_guess_candidates(search_space_df: pd.DataFrame, config: SsaEvalConfig) -> pd.DataFrame:
    selected_rows = []
    for _, group in search_space_df.groupby("outage_s"):
        pareto = pareto_front(
            group,
            ["total_ballistic_min", "extra_dv_mps", "recovery_horizon_min"],
            [False, True, True],
        )
        selected_rows.append(
            pareto.sort_values(
                [
                    "recoverable_flag",
                    "total_ballistic_min",
                    "extra_dv_mps",
                    "recovery_horizon_min",
                    "terminal_position_error_km",
                ],
                ascending=[False, False, True, True, True],
            ).head(config.selected_candidates_per_outage)
        )
    return pd.concat(selected_rows, ignore_index=True).reset_index(drop=True)


def simulate_phase_guess_candidate_history(
    candidate_row: pd.Series,
    operator_epoch,
    mean_motion_rev_day: float,
    phase_config: PhaseGuessConfig,
) -> pd.DataFrame:
    n_mean_rad_s = float(mean_motion_rev_day) * (2.0 * np.pi / 86400.0)
    nominal_control_km_s2 = phase_config.nominal_accel_km_s2 * phase_config.nominal_thrust_direction_rtn
    axis_control_km_s2 = phase_config.nominal_accel_km_s2 * phase_config.control_axis_scale_rtn
    _, x_recovery_start, outage_hist, coast_hist = integrate_outage_then_ballistic(
        outage_s=int(candidate_row["outage_s"]),
        ballistic_delay_s=int(candidate_row["ballistic_delay_s"]),
        nominal_control_km_s2=nominal_control_km_s2,
        n_rad_s=n_mean_rad_s,
        step_seconds=phase_config.integration_step_seconds,
        epoch=operator_epoch,
    )
    phases_rad = np.array(
        [float(candidate_row["phase_r_rad"]), float(candidate_row["phase_t_rad"]), float(candidate_row["phase_n_rad"])],
        dtype=float,
    )
    recovery_start_time = pd.Timestamp(operator_epoch) + pd.Timedelta(
        seconds=int(candidate_row["outage_s"] + candidate_row["ballistic_delay_s"])
    )
    recovery_hist = integrate_hcw_segment(
        x_recovery_start,
        recovery_start_time,
        int(candidate_row["recovery_horizon_s"]),
        make_phase_guess_control_fn(phases_rad, axis_control_km_s2, n_mean_rad_s),
        n_mean_rad_s,
        phase_config.integration_step_seconds,
        "phase_guess_recovery",
    )

    pieces = [outage_hist]
    if len(coast_hist) > 0:
        pieces.append(coast_hist.iloc[1:].copy())
    if len(recovery_hist) > 0:
        pieces.append(recovery_hist.iloc[1:].copy())
    full_hist = pd.concat(pieces, ignore_index=True)
    full_hist["candidate_id"] = candidate_row["candidate_id"]
    full_hist["elapsed_s"] = (full_hist["timestamp_utc"] - full_hist["timestamp_utc"].iloc[0]).dt.total_seconds()
    return full_hist


def relative_history_to_candidate_eci(candidate_rel_hist: pd.DataFrame, operator_satrec) -> pd.DataFrame:
    times = candidate_rel_hist["timestamp_utc"].tolist()
    operator_nominal = propagate_satrec_to_times(operator_satrec, times)
    rows = []
    for idx in range(len(candidate_rel_hist)):
        op_row = operator_nominal.iloc[idx]
        rel_row = candidate_rel_hist.iloc[idx]
        op_r = op_row[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
        op_v = op_row[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy(dtype=float)
        c_rtn_from_eci = rtn_rotation_matrix_from_state(op_r, op_v)
        rel_r_eci = c_rtn_from_eci.T @ rel_row[["dR_km", "dT_km", "dN_km"]].to_numpy(dtype=float)
        rel_v_eci = c_rtn_from_eci.T @ rel_row[["dVR_km_s", "dVT_km_s", "dVN_km_s"]].to_numpy(dtype=float)
        cand_r = op_r + rel_r_eci
        cand_v = op_v + rel_v_eci
        rows.append(
            {
                "timestamp_utc": rel_row["timestamp_utc"],
                "candidate_id": rel_row["candidate_id"],
                "segment": rel_row["segment"],
                "x_km": float(cand_r[0]),
                "y_km": float(cand_r[1]),
                "z_km": float(cand_r[2]),
                "vx_km_s": float(cand_v[0]),
                "vy_km_s": float(cand_v[1]),
                "vz_km_s": float(cand_v[2]),
            }
        )
    out = pd.DataFrame(rows)
    out["r_norm_km"] = np.linalg.norm(out[["x_km", "y_km", "z_km"]].to_numpy(dtype=float), axis=1)
    out["altitude_km"] = out["r_norm_km"] - R_EARTH_KM
    return out


def score_candidate_ssa(
    candidate_row: pd.Series,
    eval_catalog_df: pd.DataFrame,
    satrec_cache: dict[int, object],
    operator_satrec,
    operator_epoch,
    mean_motion_rev_day: float,
    phase_config: PhaseGuessConfig,
    eval_config: SsaEvalConfig,
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    candidate_rel_hist = simulate_phase_guess_candidate_history(candidate_row, operator_epoch, mean_motion_rev_day, phase_config)
    candidate_eci_hist = relative_history_to_candidate_eci(candidate_rel_hist, operator_satrec)
    times = candidate_eci_hist["timestamp_utc"].tolist()
    operator_nominal = propagate_satrec_to_times(operator_satrec, times)

    all_candidate_distances: list[float] = []
    all_baseline_distances: list[float] = []
    new_close_count = 0
    nearest = {"name": None, "catnr": None, "candidate": np.inf, "baseline": np.inf}

    for _, obj_row in eval_catalog_df.iterrows():
        catnr = int(obj_row["NORAD_CAT_ID"])
        obj_states = propagate_satrec_to_times(satrec_cache[catnr], times)
        obj_pos = obj_states[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
        baseline_pos = operator_nominal[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
        candidate_pos = candidate_eci_hist[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
        baseline_dist_km = np.linalg.norm(obj_pos - baseline_pos, axis=1)
        candidate_dist_km = np.linalg.norm(obj_pos - candidate_pos, axis=1)
        min_base = float(np.min(baseline_dist_km))
        min_cand = float(np.min(candidate_dist_km))
        if min_base >= eval_config.new_close_approach_threshold_km and min_cand < eval_config.new_close_approach_threshold_km:
            new_close_count += 1
        if min_cand < nearest["candidate"]:
            nearest = {
                "name": str(obj_row["OBJECT_NAME"]),
                "catnr": int(obj_row["NORAD_CAT_ID"]),
                "candidate": min_cand,
                "baseline": min_base,
            }
        all_candidate_distances.extend(candidate_dist_km.tolist())
        all_baseline_distances.extend(baseline_dist_km.tolist())

    all_candidate_distances_np = np.asarray(all_candidate_distances, dtype=float)
    all_baseline_distances_np = np.asarray(all_baseline_distances, dtype=float)
    risk_proxy = np.exp(-0.5 * (all_candidate_distances_np / eval_config.risk_proxy_sigma_km) ** 2)
    metrics = {
        "ssa_eval_object_count": int(len(eval_catalog_df)),
        "new_close_approach_count": int(new_close_count),
        "baseline_min_catalog_miss_distance_km": float(np.min(all_baseline_distances_np)),
        "candidate_min_catalog_miss_distance_km": float(np.min(all_candidate_distances_np)),
        "delta_min_miss_distance_km": float(np.min(all_candidate_distances_np) - np.min(all_baseline_distances_np)),
        "candidate_p10_catalog_miss_distance_km": float(np.percentile(all_candidate_distances_np, 10)),
        "risk_proxy_peak": float(np.max(risk_proxy)),
        "risk_proxy_p95": float(np.percentile(risk_proxy, 95)),
        "nearest_object_name": nearest["name"],
        "nearest_object_catnr": nearest["catnr"],
        "nearest_object_baseline_miss_km": float(nearest["baseline"]),
        "nearest_object_candidate_miss_km": float(nearest["candidate"]),
    }
    return metrics, candidate_rel_hist, candidate_eci_hist


def evaluate_selected_candidates(
    search_space_df: pd.DataFrame,
    local_catalog_with_tle: pd.DataFrame,
    satrec_cache: dict[int, object],
    operator_catnr: int,
    operator_epoch,
    mean_motion_rev_day: float,
    phase_config: PhaseGuessConfig,
    eval_config: SsaEvalConfig,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    eval_catalog = (
        local_catalog_with_tle.sort_values(["MISS_DISTANCE_KM", "TCA_FROM_EPOCH_MIN"], ascending=[True, True])
        .head(eval_config.top_object_count)
        .reset_index(drop=True)
    )
    selected = select_phase_guess_candidates(search_space_df, eval_config)
    selected_metrics_rows = []
    rel_histories: dict[str, pd.DataFrame] = {}
    eci_histories: dict[str, pd.DataFrame] = {}
    for _, candidate_row in selected.iterrows():
        metrics, rel_hist, eci_hist = score_candidate_ssa(
            candidate_row,
            eval_catalog,
            satrec_cache,
            satrec_cache[int(operator_catnr)],
            operator_epoch,
            mean_motion_rev_day,
            phase_config,
            eval_config,
        )
        row_out = candidate_row.to_dict()
        row_out.update(metrics)
        selected_metrics_rows.append(row_out)
        rel_histories[str(candidate_row["candidate_id"])] = rel_hist
        eci_histories[str(candidate_row["candidate_id"])] = eci_hist

    selected_with_metrics = pd.DataFrame(selected_metrics_rows).sort_values(
        ["outage_s", "recoverable_flag", "total_ballistic_min", "extra_dv_mps", "candidate_min_catalog_miss_distance_km"],
        ascending=[True, False, False, True, True],
    )
    return selected_with_metrics.reset_index(drop=True), rel_histories, eci_histories


def ssa_aware_pareto(df: pd.DataFrame) -> pd.DataFrame:
    return pareto_front(df, ["total_ballistic_min", "extra_dv_mps", "risk_proxy_peak"], [False, True, True])
