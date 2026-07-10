from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from ssa_mte.config import PhaseGuessConfig
from ssa_mte.propagation import build_time_grid, ensure_utc_timestamp

RTN_AXES = np.array(["R", "T", "N"])


def sign_no_zero(x):
    arr = np.asarray(x, dtype=float)
    return np.where(arr >= 0.0, 1.0, -1.0)


def hcw_state_derivative(state_km_kms: np.ndarray, control_km_s2: np.ndarray, n_rad_s: float) -> np.ndarray:
    d_r, d_t, d_n, d_vr, d_vt, d_vn = state_km_kms
    u_r, u_t, u_n = control_km_s2
    dd_r = 3.0 * (n_rad_s**2) * d_r + 2.0 * n_rad_s * d_vt + u_r
    dd_t = -2.0 * n_rad_s * d_vr + u_t
    dd_n = -(n_rad_s**2) * d_n + u_n
    return np.array([d_vr, d_vt, d_vn, dd_r, dd_t, dd_n], dtype=float)


def rk4_step_hcw(
    state_km_kms: np.ndarray,
    t_s: float,
    dt_s: float,
    control_fn: Callable[[float, np.ndarray], np.ndarray],
    n_rad_s: float,
) -> np.ndarray:
    def f(local_t, local_state):
        return hcw_state_derivative(local_state, np.asarray(control_fn(local_t, local_state), dtype=float), n_rad_s)

    k1 = f(t_s, state_km_kms)
    k2 = f(t_s + 0.5 * dt_s, state_km_kms + 0.5 * dt_s * k1)
    k3 = f(t_s + 0.5 * dt_s, state_km_kms + 0.5 * dt_s * k2)
    k4 = f(t_s + dt_s, state_km_kms + dt_s * k3)
    return state_km_kms + (dt_s / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate_hcw_segment(
    initial_state_km_kms: np.ndarray,
    start_time_utc,
    duration_seconds: int,
    control_fn: Callable[[float, np.ndarray], np.ndarray],
    n_rad_s: float,
    step_seconds: int,
    segment_label: str,
) -> pd.DataFrame:
    times = build_time_grid(start_time_utc, int(duration_seconds), int(step_seconds))
    t_seconds = (times - times[0]).total_seconds().astype(float)
    state = np.asarray(initial_state_km_kms, dtype=float).copy()
    rows = []

    for idx, t_s in enumerate(t_seconds):
        control_km_s2 = np.asarray(control_fn(float(t_s), state), dtype=float)
        rows.append(
            {
                "timestamp_utc": ensure_utc_timestamp(times[idx]),
                "t_s": float(t_s),
                "segment": segment_label,
                "dR_km": float(state[0]),
                "dT_km": float(state[1]),
                "dN_km": float(state[2]),
                "dVR_km_s": float(state[3]),
                "dVT_km_s": float(state[4]),
                "dVN_km_s": float(state[5]),
                "uR_km_s2": float(control_km_s2[0]),
                "uT_km_s2": float(control_km_s2[1]),
                "uN_km_s2": float(control_km_s2[2]),
            }
        )
        if idx == len(t_seconds) - 1:
            break
        state = rk4_step_hcw(state, float(t_s), float(t_seconds[idx + 1] - t_s), control_fn, n_rad_s)

    out = pd.DataFrame(rows)
    out["relative_position_error_km"] = np.linalg.norm(out[["dR_km", "dT_km", "dN_km"]].to_numpy(float), axis=1)
    out["relative_velocity_error_mps"] = 1000.0 * np.linalg.norm(
        out[["dVR_km_s", "dVT_km_s", "dVN_km_s"]].to_numpy(float),
        axis=1,
    )
    out["control_norm_mps2"] = 1000.0 * np.linalg.norm(
        out[["uR_km_s2", "uT_km_s2", "uN_km_s2"]].to_numpy(float),
        axis=1,
    )
    return out


def make_constant_control_fn(control_vector_km_s2: np.ndarray):
    control_vector_km_s2 = np.asarray(control_vector_km_s2, dtype=float).copy()

    def _fn(t_s, state_km_kms):
        return control_vector_km_s2

    return _fn


def make_phase_guess_control_fn(phase_vector_rad: np.ndarray, axis_control_km_s2: np.ndarray, n_rad_s: float):
    phase_vector_rad = np.asarray(phase_vector_rad, dtype=float).copy()
    axis_control_km_s2 = np.asarray(axis_control_km_s2, dtype=float).copy()

    def _fn(t_s, state_km_kms):
        bang = -sign_no_zero(np.cos(n_rad_s * float(t_s) + phase_vector_rad))
        return axis_control_km_s2 * bang

    return _fn


def phase_guess_initial_phases(state_start_km_kms: np.ndarray, recovery_horizon_s: float) -> tuple[np.ndarray, str, np.ndarray]:
    tau = max(float(recovery_horizon_s), 1.0)
    r0 = np.asarray(state_start_km_kms[:3], dtype=float)
    v0 = np.asarray(state_start_km_kms[3:], dtype=float)
    q_like = -(2.0 * r0 + tau * v0) / (tau**2)
    phase0 = np.where(q_like >= 0.0, np.pi / 2.0, -np.pi / 2.0)
    phase0 = np.where(np.isclose(q_like, 0.0), 0.0, phase0)
    priority_axis = str(RTN_AXES[int(np.argmax(np.abs(q_like)))])
    return phase0.astype(float), priority_axis, q_like


def integrate_outage_then_ballistic(
    outage_s: int,
    ballistic_delay_s: int,
    nominal_control_km_s2: np.ndarray,
    n_rad_s: float,
    step_seconds: int,
    epoch,
):
    x0 = np.zeros(6, dtype=float)
    outage_hist = integrate_hcw_segment(
        x0,
        epoch,
        int(outage_s),
        make_constant_control_fn(-nominal_control_km_s2),
        n_rad_s,
        step_seconds,
        "missed_thrust_outage",
    )
    x_after_outage = outage_hist[["dR_km", "dT_km", "dN_km", "dVR_km_s", "dVT_km_s", "dVN_km_s"]].iloc[-1].to_numpy(float)
    if int(ballistic_delay_s) > 0:
        coast_hist = integrate_hcw_segment(
            x_after_outage,
            outage_hist["timestamp_utc"].iloc[-1],
            int(ballistic_delay_s),
            make_constant_control_fn(np.zeros(3, dtype=float)),
            n_rad_s,
            step_seconds,
            "ballistic_delay",
        )
        x_recovery_start = coast_hist[["dR_km", "dT_km", "dN_km", "dVR_km_s", "dVT_km_s", "dVN_km_s"]].iloc[-1].to_numpy(float)
    else:
        coast_hist = pd.DataFrame(columns=outage_hist.columns)
        x_recovery_start = x_after_outage.copy()
    return x_after_outage, x_recovery_start, outage_hist, coast_hist


def _terminal_position_for_phases(
    phases_rad: np.ndarray,
    state_start_km_kms: np.ndarray,
    recovery_horizon_s: int,
    axis_control_km_s2: np.ndarray,
    n_rad_s: float,
    step_seconds: int,
    epoch,
) -> np.ndarray:
    hist = integrate_hcw_segment(
        state_start_km_kms,
        epoch,
        int(recovery_horizon_s),
        make_phase_guess_control_fn(phases_rad, axis_control_km_s2, n_rad_s),
        n_rad_s,
        step_seconds,
        "phase_guess_recovery",
    )
    return hist[["dR_km", "dT_km", "dN_km"]].iloc[-1].to_numpy(float)


def refine_phase_guess(
    phase0_rad: np.ndarray,
    state_start_km_kms: np.ndarray,
    recovery_horizon_s: int,
    axis_control_km_s2: np.ndarray,
    n_rad_s: float,
    step_seconds: int,
    epoch,
    iterations: int,
) -> tuple[np.ndarray, float, int]:
    phases = np.asarray(phase0_rad, dtype=float).copy()
    best = float(np.linalg.norm(_terminal_position_for_phases(phases, state_start_km_kms, recovery_horizon_s, axis_control_km_s2, n_rad_s, step_seconds, epoch)))
    evals = 1
    step = np.pi / 2.0
    for _ in range(int(iterations)):
        improved = False
        for axis in range(3):
            for direction in (-1.0, 1.0):
                trial = phases.copy()
                trial[axis] = float(np.clip(trial[axis] + direction * step, -np.pi, np.pi))
                score = float(np.linalg.norm(_terminal_position_for_phases(trial, state_start_km_kms, recovery_horizon_s, axis_control_km_s2, n_rad_s, step_seconds, epoch)))
                evals += 1
                if score < best:
                    phases, best, improved = trial, score, True
        if not improved:
            step *= 0.5
    return phases, best, evals


def solve_phase_guess_candidate(
    state_start_km_kms: np.ndarray,
    recovery_horizon_s: int,
    axis_control_km_s2: np.ndarray,
    n_rad_s: float,
    step_seconds: int,
    epoch,
    iterations: int,
) -> dict[str, object]:
    phase0_rad, priority_axis, q_like = phase_guess_initial_phases(state_start_km_kms, recovery_horizon_s)
    best_phases_rad, _, n_eval = refine_phase_guess(
        phase0_rad,
        state_start_km_kms,
        recovery_horizon_s,
        axis_control_km_s2,
        n_rad_s,
        step_seconds,
        epoch,
        iterations,
    )
    recovery_hist = integrate_hcw_segment(
        state_start_km_kms,
        epoch,
        int(recovery_horizon_s),
        make_phase_guess_control_fn(best_phases_rad, axis_control_km_s2, n_rad_s),
        n_rad_s,
        step_seconds,
        "phase_guess_recovery",
    )
    final_state = recovery_hist[["dR_km", "dT_km", "dN_km", "dVR_km_s", "dVT_km_s", "dVN_km_s"]].iloc[-1].to_numpy(float)
    control_norm_km_s2 = np.linalg.norm(recovery_hist[["uR_km_s2", "uT_km_s2", "uN_km_s2"]].to_numpy(float), axis=1)
    extra_dv_mps = float(1000.0 * np.trapezoid(control_norm_km_s2, recovery_hist["t_s"].to_numpy(float)))
    return {
        "phase_r_deg": float(np.degrees(best_phases_rad[0])),
        "phase_t_deg": float(np.degrees(best_phases_rad[1])),
        "phase_n_deg": float(np.degrees(best_phases_rad[2])),
        "phase_r_rad": float(best_phases_rad[0]),
        "phase_t_rad": float(best_phases_rad[1]),
        "phase_n_rad": float(best_phases_rad[2]),
        "priority_axis": priority_axis,
        "q_like_r_km_s2": float(q_like[0]),
        "q_like_t_km_s2": float(q_like[1]),
        "q_like_n_km_s2": float(q_like[2]),
        "terminal_position_error_km": float(np.linalg.norm(final_state[:3])),
        "terminal_velocity_error_mps": float(1000.0 * np.linalg.norm(final_state[3:])),
        "extra_dv_mps": extra_dv_mps,
        "solver_nfev": int(n_eval),
        "solver_success": True,
    }


def build_phase_guess_search_space(
    operator_epoch,
    operator_period_sec: int,
    mean_motion_rev_day: float,
    config: PhaseGuessConfig,
) -> pd.DataFrame:
    n_mean_rad_s = float(mean_motion_rev_day) * (2.0 * np.pi / 86400.0)
    nominal_control_km_s2 = config.nominal_accel_km_s2 * config.nominal_thrust_direction_rtn
    axis_control_km_s2 = config.nominal_accel_km_s2 * config.control_axis_scale_rtn
    rows = []

    for outage_s in config.missed_thrust_durations_s:
        for ballistic_delay_min in config.ballistic_delay_grid_min:
            ballistic_delay_s = int(60 * ballistic_delay_min)
            x_after_outage, x_recovery_start, _, _ = integrate_outage_then_ballistic(
                int(outage_s),
                ballistic_delay_s,
                nominal_control_km_s2,
                n_mean_rad_s,
                config.integration_step_seconds,
                operator_epoch,
            )
            for recovery_horizon_min in config.recovery_horizon_grid_min:
                recovery_horizon_s = int(60 * recovery_horizon_min)
                candidate = solve_phase_guess_candidate(
                    x_recovery_start,
                    recovery_horizon_s,
                    axis_control_km_s2,
                    n_mean_rad_s,
                    config.integration_step_seconds,
                    operator_epoch,
                    config.search_iterations,
                )
                total_ballistic_s = int(outage_s) + int(ballistic_delay_s)
                rows.append(
                    {
                        "candidate_id": f"out{int(outage_s)}_delay{int(ballistic_delay_s)}_rec{int(recovery_horizon_s)}",
                        "outage_s": int(outage_s),
                        "ballistic_delay_s": ballistic_delay_s,
                        "ballistic_delay_min": float(ballistic_delay_s / 60.0),
                        "total_ballistic_s": total_ballistic_s,
                        "total_ballistic_min": float(total_ballistic_s / 60.0),
                        "recovery_horizon_s": recovery_horizon_s,
                        "recovery_horizon_min": float(recovery_horizon_s / 60.0),
                        "recovery_orbits": float(recovery_horizon_s / operator_period_sec),
                        "state_start_dR_km": float(x_recovery_start[0]),
                        "state_start_dT_km": float(x_recovery_start[1]),
                        "state_start_dN_km": float(x_recovery_start[2]),
                        "state_start_dVR_mps": float(1000.0 * x_recovery_start[3]),
                        "state_start_dVT_mps": float(1000.0 * x_recovery_start[4]),
                        "state_start_dVN_mps": float(1000.0 * x_recovery_start[5]),
                        "outage_terminal_error_km": float(np.linalg.norm(x_after_outage[:3])),
                        "recovery_start_error_km": float(np.linalg.norm(x_recovery_start[:3])),
                        **candidate,
                    }
                )

    out = pd.DataFrame(rows)
    out["recoverable_flag"] = (
        (out["terminal_position_error_km"] <= config.terminal_error_km_cap)
        & (out["terminal_velocity_error_mps"] <= config.terminal_velocity_error_mps_cap)
    )
    out["tradeoff_score"] = (
        out["terminal_position_error_km"] / max(out["terminal_position_error_km"].quantile(0.90), 1e-6)
        + out["extra_dv_mps"] / max(out["extra_dv_mps"].quantile(0.90), 1e-6)
        + 0.25 * out["total_ballistic_min"] / max(out["total_ballistic_min"].quantile(0.90), 1e-6)
    )
    return out.sort_values(["outage_s", "tradeoff_score", "terminal_position_error_km", "extra_dv_mps"]).reset_index(drop=True)
