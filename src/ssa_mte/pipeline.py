from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ssa_mte.catalog import build_local_catalog, normalize_catalog
from ssa_mte.celestrak import CelesTrakClient
from ssa_mte.config import PhaseGuessConfig, RunConfig, SsaEvalConfig
from ssa_mte.phase_guess import build_phase_guess_search_space
from ssa_mte.plotting import plot_search_space
from ssa_mte.propagation import build_satrec, compute_min_distance_score, ensure_utc_timestamp, propagate_satrec_to_times
from ssa_mte.rtn import add_state_geometry_columns, rtn_rotation_matrix_from_state
from ssa_mte.ssa_eval import evaluate_selected_candidates


def _json_default(value):
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def build_operator_summary(operator_row: pd.Series) -> dict[str, object]:
    return {
        "name": str(operator_row["OBJECT_NAME"]),
        "catnr": int(operator_row["NORAD_CAT_ID"]),
        "epoch": ensure_utc_timestamp(operator_row["EPOCH"]),
        "inclination_deg": float(operator_row["INCLINATION"]),
        "mean_motion_rev_day": float(operator_row["MEAN_MOTION"]),
        "period_min": float(operator_row["PERIOD_MIN"]),
        "perigee_alt_km": float(operator_row["PERIGEE_ALT_KM"]),
        "apogee_alt_km": float(operator_row["APOGEE_ALT_KM"]),
    }


def attach_tles_and_rank(
    client: CelesTrakClient,
    local_catalog: pd.DataFrame,
    operator_tle: dict[str, str],
    operator_summary: dict[str, object],
    config: RunConfig,
) -> tuple[pd.DataFrame, dict[int, object]]:
    prefetch = (
        local_catalog.sort_values(["DELTA_RAAN_DEG", "DELTA_MEAN_MOTION", "DELTA_INC_DEG"])
        .head(config.local_catalog_target_size)
        .reset_index(drop=True)
    )
    tle_records = []
    for catnr in prefetch["NORAD_CAT_ID"].astype(int).tolist():
        rec = client.fetch_tle_for_catnr(catnr, force_refresh=config.force_refresh)
        if rec is not None:
            tle_records.append(rec)

    tle_pool = pd.DataFrame(tle_records)
    if tle_pool.empty:
        raise RuntimeError("No local-catalog TLE records could be fetched.")

    local_with_tle = prefetch.merge(tle_pool, on="NORAD_CAT_ID", how="inner").reset_index(drop=True)
    satrec_cache: dict[int, object] = {
        int(config.operator_catnr): build_satrec(operator_tle["line1"], operator_tle["line2"])
    }
    for _, row in local_with_tle.iterrows():
        satrec_cache[int(row["NORAD_CAT_ID"])] = build_satrec(str(row["TLE_LINE1"]), str(row["TLE_LINE2"]))

    operator_epoch = ensure_utc_timestamp(operator_summary["epoch"])
    operator_period_sec = int(round(float(operator_summary["period_min"]) * 60.0))
    score_window_sec = int(config.screening_window_orbits * operator_period_sec)

    miss_records = []
    for _, row in local_with_tle.iterrows():
        catnr = int(row["NORAD_CAT_ID"])
        try:
            rec = compute_min_distance_score(
                satrec_cache[int(config.operator_catnr)],
                satrec_cache[catnr],
                operator_epoch,
                score_window_sec,
                config.default_step_seconds,
            )
        except Exception:
            rec = {"MISS_DISTANCE_KM": np.nan, "MISS_DISTANCE_TCA_UTC": pd.NaT, "TCA_FROM_EPOCH_MIN": np.nan}
        miss_records.append(rec)

    ranked = pd.concat([local_with_tle.reset_index(drop=True), pd.DataFrame(miss_records)], axis=1)
    ranked = (
        ranked.dropna(subset=["MISS_DISTANCE_KM"])
        .sort_values(["MISS_DISTANCE_KM", "DELTA_RAAN_DEG", "DELTA_MEAN_MOTION"])
        .head(config.local_catalog_target_size)
        .reset_index(drop=True)
    )
    if ranked.empty:
        raise RuntimeError("All SGP4 miss-distance scores failed.")
    return ranked, satrec_cache


def build_operator_reference(
    satrec_cache: dict[int, object],
    operator_catnr: int,
    operator_summary: dict[str, object],
    screening_window_orbits: int,
    step_seconds: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    operator_epoch = ensure_utc_timestamp(operator_summary["epoch"])
    operator_period_sec = int(round(float(operator_summary["period_min"]) * 60.0))
    screening_window_sec = int(screening_window_orbits * operator_period_sec)
    times = pd.date_range(
        start=operator_epoch,
        periods=max(2, int(screening_window_sec / step_seconds) + 1),
        freq=pd.Timedelta(seconds=int(step_seconds)),
    )
    trajectory = add_state_geometry_columns(propagate_satrec_to_times(satrec_cache[int(operator_catnr)], times))
    state_at_epoch = trajectory.iloc[0]
    rtn_matrix = rtn_rotation_matrix_from_state(
        state_at_epoch[["x_km", "y_km", "z_km"]].to_numpy(dtype=float),
        state_at_epoch[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy(dtype=float),
    )
    reference = {
        "epoch": operator_epoch,
        "period_sec": operator_period_sec,
        "screening_window_sec": screening_window_sec,
        "rtn_matrix_at_epoch": rtn_matrix.tolist(),
    }
    return trajectory, reference


def run_assessment(
    config: RunConfig | None = None,
    phase_config: PhaseGuessConfig | None = None,
    eval_config: SsaEvalConfig | None = None,
    make_plot: bool = True,
) -> dict[str, object]:
    config = config or RunConfig()
    phase_config = phase_config or PhaseGuessConfig(integration_step_seconds=config.default_step_seconds)
    eval_config = eval_config or SsaEvalConfig()

    config.cache_dir.mkdir(parents=True, exist_ok=True)
    config.outputs_dir.mkdir(parents=True, exist_ok=True)

    client = CelesTrakClient(config.cache_dir, timeout_seconds=config.http_timeout_seconds)
    operator_tle = client.fetch_operator_tle(config.operator_catnr, force_refresh=config.force_refresh)
    catalog_raw = client.fetch_catalog_csv(config.catalog_group, force_refresh=config.force_refresh)
    catalog = normalize_catalog(catalog_raw)
    operator_row, local_catalog = build_local_catalog(catalog, config.operator_catnr)
    operator_summary = build_operator_summary(operator_row)

    local_catalog_with_tle, satrec_cache = attach_tles_and_rank(
        client,
        local_catalog,
        operator_tle,
        operator_summary,
        config,
    )
    operator_trajectory, operator_reference = build_operator_reference(
        satrec_cache,
        config.operator_catnr,
        operator_summary,
        config.screening_window_orbits,
        config.default_step_seconds,
    )

    search_space = build_phase_guess_search_space(
        operator_summary["epoch"],
        int(operator_reference["period_sec"]),
        float(operator_summary["mean_motion_rev_day"]),
        phase_config,
    )
    selected, rel_histories, eci_histories = evaluate_selected_candidates(
        search_space,
        local_catalog_with_tle,
        satrec_cache,
        config.operator_catnr,
        operator_summary["epoch"],
        float(operator_summary["mean_motion_rev_day"]),
        phase_config,
        eval_config,
    )

    paths = {
        "local_catalog": config.outputs_dir / "local_catalog_screened.csv",
        "operator_trajectory": config.outputs_dir / "operator_trajectory.csv",
        "search_space": config.outputs_dir / "phase_guess_search_space.csv",
        "selected_candidates": config.outputs_dir / "ssa_selected_candidates.csv",
        "summary": config.outputs_dir / "run_summary.json",
    }
    local_catalog_with_tle.to_csv(paths["local_catalog"], index=False)
    operator_trajectory.to_csv(paths["operator_trajectory"], index=False)
    search_space.to_csv(paths["search_space"], index=False)
    selected.to_csv(paths["selected_candidates"], index=False)

    for candidate_id, rel_hist in rel_histories.items():
        rel_hist.to_csv(config.outputs_dir / f"{candidate_id}_relative_history.csv", index=False)
    for candidate_id, eci_hist in eci_histories.items():
        eci_hist.to_csv(config.outputs_dir / f"{candidate_id}_eci_history.csv", index=False)

    if make_plot:
        paths["plot"] = plot_search_space(search_space, selected, config.outputs_dir / "ssa_aware_pareto.png")

    summary = {
        "operator": operator_summary,
        "operator_tle_name": operator_tle["name"],
        "raw_catalog_rows": int(len(catalog_raw)),
        "prefilter_catalog_rows": int(len(local_catalog)),
        "screened_catalog_rows": int(len(local_catalog_with_tle)),
        "phase_guess_candidate_count": int(len(search_space)),
        "recoverable_candidate_count": int(search_space["recoverable_flag"].sum()),
        "selected_candidate_count": int(len(selected)),
        "best_candidate": selected.iloc[0].to_dict() if len(selected) else {},
        "outputs": {key: str(path) for key, path in paths.items()},
    }
    paths["summary"].write_text(json.dumps(summary, indent=2, default=_json_default), encoding="utf-8")
    return {
        "summary": summary,
        "paths": paths,
        "catalog": local_catalog_with_tle,
        "search_space": search_space,
        "selected": selected,
    }
