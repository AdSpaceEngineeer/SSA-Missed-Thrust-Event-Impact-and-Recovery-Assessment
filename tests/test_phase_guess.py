import pandas as pd

from ssa_mte.config import PhaseGuessConfig
from ssa_mte.phase_guess import build_phase_guess_search_space, hcw_state_derivative


def test_hcw_derivative_zero_state_zero_control_is_zero():
    out = hcw_state_derivative(
        state_km_kms=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        control_km_s2=[0.0, 0.0, 0.0],
        n_rad_s=0.001,
    )
    assert out.tolist() == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


def test_phase_guess_search_space_has_expected_candidate_count():
    config = PhaseGuessConfig(
        ballistic_delay_grid_min=(0, 5),
        recovery_horizon_grid_min=(10, 20),
        missed_thrust_durations_s=(30, 60),
        integration_step_seconds=300,
        search_iterations=1,
    )

    search_space = build_phase_guess_search_space(
        operator_epoch=pd.Timestamp("2026-01-01T00:00:00Z"),
        operator_period_sec=5700,
        mean_motion_rev_day=15.15,
        config=config,
    )

    assert len(search_space) == 8
    assert set(search_space["outage_s"]) == {30, 60}
    assert search_space["candidate_id"].is_unique
    assert (search_space["extra_dv_mps"] >= 0).all()
