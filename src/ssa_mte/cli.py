from __future__ import annotations

import argparse
from pathlib import Path

from ssa_mte.config import PhaseGuessConfig, RunConfig, SsaEvalConfig
from ssa_mte.pipeline import run_assessment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run an SSA-aware missed-thrust recovery assessment.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Fetch CelesTrak data, generate recovery candidates, and score SSA risk.")
    run.add_argument("--cache-dir", type=Path, default=Path("data/cache"))
    run.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    run.add_argument("--operator-catnr", type=int, default=60507)
    run.add_argument("--catalog-group", default="ACTIVE")
    run.add_argument("--step-seconds", type=int, default=120)
    run.add_argument("--catalog-size", type=int, default=40)
    run.add_argument("--eval-objects", type=int, default=25)
    run.add_argument("--force-refresh", action="store_true")
    run.add_argument("--no-plot", action="store_true")
    run.add_argument(
        "--full",
        action="store_true",
        help="Use a broader grid and larger catalog. This may take several minutes.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        run_config = RunConfig(
            operator_catnr=args.operator_catnr,
            catalog_group=args.catalog_group,
            default_step_seconds=args.step_seconds,
            local_catalog_target_size=1500 if args.full else args.catalog_size,
            screening_window_orbits=3 if args.full else 2,
            force_refresh=args.force_refresh,
            cache_dir=args.cache_dir,
            outputs_dir=args.outputs_dir,
        )
        phase_config = (
            PhaseGuessConfig(
                ballistic_delay_grid_min=(0, 5, 10, 15, 30, 45),
                recovery_horizon_grid_min=(15, 25, 35, 50, 70, 90),
                missed_thrust_durations_s=(10, 30, 60, 300, 600, 1800),
                integration_step_seconds=args.step_seconds,
                search_iterations=6,
            )
            if args.full
            else PhaseGuessConfig(integration_step_seconds=args.step_seconds)
        )
        eval_config = SsaEvalConfig(
            top_object_count=300 if args.full else args.eval_objects,
            selected_candidates_per_outage=3 if args.full else 2,
        )
        result = run_assessment(run_config, phase_config, eval_config, make_plot=not args.no_plot)
        summary = result["summary"]
        print("SSA missed-thrust recovery assessment complete")
        print(f"Operator: {summary['operator']['name']} ({summary['operator']['catnr']})")
        print(f"Screened catalog rows: {summary['screened_catalog_rows']}")
        print(f"Phase Guess candidates: {summary['phase_guess_candidate_count']}")
        print(f"Selected SSA-aware candidates: {summary['selected_candidate_count']}")
        print(f"Summary: {summary['outputs']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
