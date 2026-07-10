from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class RunConfig:
    operator_name: str = "TANAGER-1"
    operator_catnr: int = 60507
    catalog_group: str = "ACTIVE"
    default_step_seconds: int = 120
    local_catalog_target_size: int = 40
    screening_window_orbits: int = 2
    force_refresh: bool = False
    http_timeout_seconds: int = 30
    cache_dir: Path = Path("data/cache")
    outputs_dir: Path = Path("outputs")


@dataclass(frozen=True)
class PhaseGuessConfig:
    ballistic_delay_grid_min: tuple[int, ...] = (0, 10, 30)
    recovery_horizon_grid_min: tuple[int, ...] = (15, 35, 70)
    missed_thrust_durations_s: tuple[int, ...] = (30, 300, 600)
    nominal_thrust_direction_rtn: np.ndarray = field(
        default_factory=lambda: np.array([0.0, 1.0, 0.0], dtype=float)
    )
    notional_nominal_dv_per_day_mps: float = 0.50
    control_axis_scale_rtn: np.ndarray = field(
        default_factory=lambda: np.array([0.35, 1.00, 0.25], dtype=float)
    )
    terminal_error_km_cap: float = 1.0
    terminal_velocity_error_mps_cap: float = 0.05
    integration_step_seconds: int = 120
    search_iterations: int = 5

    @property
    def nominal_accel_mps2(self) -> float:
        return self.notional_nominal_dv_per_day_mps / 86400.0

    @property
    def nominal_accel_km_s2(self) -> float:
        return self.nominal_accel_mps2 / 1000.0


@dataclass(frozen=True)
class SsaEvalConfig:
    top_object_count: int = 25
    new_close_approach_threshold_km: float = 25.0
    risk_proxy_sigma_km: float = 15.0
    selected_candidates_per_outage: int = 2
