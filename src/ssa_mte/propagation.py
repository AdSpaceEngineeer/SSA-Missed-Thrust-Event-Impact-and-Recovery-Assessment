from __future__ import annotations

import numpy as np
import pandas as pd
from sgp4.api import SGP4_ERRORS, Satrec, jday


def ensure_utc_timestamp(ts) -> pd.Timestamp:
    ts = pd.Timestamp(ts)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def datetime_to_jdfr(ts) -> tuple[float, float]:
    ts = ensure_utc_timestamp(ts)
    seconds = float(ts.second) + float(ts.microsecond) / 1e6 + float(getattr(ts, "nanosecond", 0)) / 1e9
    return jday(ts.year, ts.month, ts.day, ts.hour, ts.minute, seconds)


def build_time_grid(start_time, duration_seconds: int, step_seconds: int) -> pd.DatetimeIndex:
    if duration_seconds < 0:
        raise ValueError("duration_seconds must be >= 0")
    if step_seconds <= 0:
        raise ValueError("step_seconds must be > 0")

    start_time = ensure_utc_timestamp(start_time)
    end_time = start_time + pd.Timedelta(seconds=int(duration_seconds))
    if duration_seconds == 0:
        return pd.DatetimeIndex([start_time])

    grid = pd.date_range(start=start_time, end=end_time, freq=pd.Timedelta(seconds=int(step_seconds)))
    if len(grid) == 0 or grid[-1] != end_time:
        grid = grid.append(pd.DatetimeIndex([end_time]))
    return grid


def build_satrec(line1: str, line2: str) -> Satrec:
    return Satrec.twoline2rv(str(line1), str(line2))


def propagate_satrec_to_times(satrec: Satrec, times) -> pd.DataFrame:
    rows = []
    for ts in pd.DatetimeIndex([ensure_utc_timestamp(t) for t in times]):
        jd, fr = datetime_to_jdfr(ts)
        err_code, r_km, v_km_s = satrec.sgp4(jd, fr)
        if err_code != 0:
            err_msg = SGP4_ERRORS.get(err_code, f"Unknown SGP4 error code {err_code}")
            raise RuntimeError(f"SGP4 propagation failed at {ts} with error {err_code}: {err_msg}")

        rows.append(
            {
                "timestamp_utc": ts,
                "x_km": float(r_km[0]),
                "y_km": float(r_km[1]),
                "z_km": float(r_km[2]),
                "vx_km_s": float(v_km_s[0]),
                "vy_km_s": float(v_km_s[1]),
                "vz_km_s": float(v_km_s[2]),
            }
        )
    return pd.DataFrame(rows)


def compute_min_distance_score(
    operator_satrec: Satrec,
    target_satrec: Satrec,
    epoch,
    window_sec: int,
    step_sec: int,
) -> dict[str, object]:
    times = build_time_grid(epoch, duration_seconds=window_sec, step_seconds=step_sec)
    op_states = propagate_satrec_to_times(operator_satrec, times)
    tg_states = propagate_satrec_to_times(target_satrec, times)
    rel_pos_km = (
        tg_states[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
        - op_states[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
    )
    dist_km = np.linalg.norm(rel_pos_km, axis=1)
    min_idx = int(np.argmin(dist_km))
    tca_utc = pd.Timestamp(times[min_idx])
    return {
        "MISS_DISTANCE_KM": float(dist_km[min_idx]),
        "MISS_DISTANCE_TCA_UTC": tca_utc,
        "TCA_FROM_EPOCH_MIN": float((tca_utc - ensure_utc_timestamp(epoch)).total_seconds() / 60.0),
    }
