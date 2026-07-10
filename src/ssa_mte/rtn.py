from __future__ import annotations

import numpy as np
import pandas as pd

from ssa_mte.catalog import R_EARTH_KM


def rtn_rotation_matrix_from_state(r_eci_km: np.ndarray, v_eci_km_s: np.ndarray) -> np.ndarray:
    r = np.asarray(r_eci_km, dtype=float)
    v = np.asarray(v_eci_km_s, dtype=float)
    r_norm = np.linalg.norm(r)
    if r_norm == 0.0:
        raise ValueError("Cannot build RTN frame from zero position vector.")

    h = np.cross(r, v)
    h_norm = np.linalg.norm(h)
    if h_norm == 0.0:
        raise ValueError("Cannot build RTN frame from collinear or zero position/velocity vectors.")

    r_hat = r / r_norm
    n_hat = h / h_norm
    t_hat = np.cross(n_hat, r_hat)
    return np.vstack([r_hat, t_hat, n_hat])


def relative_state_eci_to_rtn(
    operator_r_eci_km: np.ndarray,
    operator_v_eci_km_s: np.ndarray,
    target_r_eci_km: np.ndarray,
    target_v_eci_km_s: np.ndarray,
) -> dict[str, float]:
    c_rtn_from_eci = rtn_rotation_matrix_from_state(operator_r_eci_km, operator_v_eci_km_s)
    rel_r_rtn = c_rtn_from_eci @ (np.asarray(target_r_eci_km, dtype=float) - np.asarray(operator_r_eci_km, dtype=float))
    rel_v_rtn = c_rtn_from_eci @ (np.asarray(target_v_eci_km_s, dtype=float) - np.asarray(operator_v_eci_km_s, dtype=float))
    return {
        "rel_r_km": float(rel_r_rtn[0]),
        "rel_t_km": float(rel_r_rtn[1]),
        "rel_n_km": float(rel_r_rtn[2]),
        "rel_v_r_km_s": float(rel_v_rtn[0]),
        "rel_v_t_km_s": float(rel_v_rtn[1]),
        "rel_v_n_km_s": float(rel_v_rtn[2]),
    }


def add_state_geometry_columns(state_df: pd.DataFrame) -> pd.DataFrame:
    df = state_df.copy()
    pos = df[["x_km", "y_km", "z_km"]].to_numpy(dtype=float)
    vel = df[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy(dtype=float)
    df["r_norm_km"] = np.linalg.norm(pos, axis=1)
    df["v_norm_km_s"] = np.linalg.norm(vel, axis=1)
    df["altitude_km"] = df["r_norm_km"] - R_EARTH_KM
    radial_velocity = np.sum(pos * vel, axis=1) / np.maximum(df["r_norm_km"].to_numpy(dtype=float), 1e-12)
    df["radial_velocity_km_s"] = radial_velocity
    tangential_sq = np.maximum(df["v_norm_km_s"].to_numpy(dtype=float) ** 2 - radial_velocity**2, 0.0)
    df["transverse_speed_km_s"] = np.sqrt(tangential_sq)
    return df
