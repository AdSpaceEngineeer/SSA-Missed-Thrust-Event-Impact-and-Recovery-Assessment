from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ssa_mte.ssa_eval import ssa_aware_pareto


def plot_search_space(search_space: pd.DataFrame, selected_candidates: pd.DataFrame, output_path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.tri as mtri

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot_df = search_space.copy()
    plot_df["final_distance_km"] = plot_df["terminal_position_error_km"]
    selected_plot = selected_candidates.copy()
    selected_plot["final_distance_km"] = selected_plot["terminal_position_error_km"]
    pareto = ssa_aware_pareto(selected_plot).sort_values("total_ballistic_min").reset_index(drop=True)

    x = plot_df["total_ballistic_min"].to_numpy(dtype=float)
    y = plot_df["final_distance_km"].to_numpy(dtype=float)
    z = plot_df["extra_dv_mps"].to_numpy(dtype=float)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(9, 6))
    unique_xy = np.unique(np.column_stack([x, y]), axis=0)
    if len(unique_xy) >= 3:
        tri = mtri.Triangulation(x, y)
        contour = ax.tricontourf(tri, z, levels=24)
        ax.tricontour(tri, z, levels=12, linewidths=0.4, alpha=0.4)
    else:
        contour = ax.scatter(x, y, c=z, s=30)

    ax.scatter(x, y, s=10, alpha=0.2)
    ax.scatter(
        pareto["total_ballistic_min"],
        pareto["final_distance_km"],
        s=120,
        facecolors="none",
        edgecolors="white",
        linewidths=1.8,
        label="SSA-aware Pareto front",
    )
    if len(pareto) >= 2:
        ax.plot(pareto["total_ballistic_min"], pareto["final_distance_km"], linewidth=1.5, color="white")

    x_span = max(float(np.max(x) - np.min(x)), 1.0)
    ax.set_xlim(float(np.min(x) - 0.04 * x_span), float(np.max(x) + 0.10 * x_span))
    ax.margins(y=0.08)

    x_high = float(np.max(x) - 0.05 * x_span)
    for _, row in pareto.iterrows():
        near_right_edge = float(row["total_ballistic_min"]) >= x_high
        ax.annotate(
            f"{int(row['outage_s'])} s",
            (row["total_ballistic_min"], row["final_distance_km"]),
            xytext=(-8 if near_right_edge else 5, 5),
            textcoords="offset points",
            fontsize=8,
            ha="right" if near_right_edge else "left",
        )

    cbar = plt.colorbar(contour, ax=ax, pad=0.02)
    cbar.set_label("Fuel proxy: extra delta-v (m/s)")
    ax.set_xlabel("Ballistic time (min)")
    ax.set_ylabel("Terminal distance from nominal trajectory (km)")
    ax.set_title("SSA-aware missed-thrust recovery search")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path
