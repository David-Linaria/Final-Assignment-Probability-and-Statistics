from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm


SEED = 20261106
SAMPLE_SIZE = 500
AXIS_LIMITS = (-3.5, 3.5)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

RHO_SETTINGS = (
    (-0.9, "neg09", "#3B6EA8"),
    (0.0, "zero", "#6B6B6B"),
    (0.9, "pos09", "#C44E52"),
)


def main() -> None:
    rng = np.random.default_rng(SEED)
    mean = np.array([0.0, 0.0])
    samples = {}

    for rho, file_label, _ in RHO_SETTINGS:
        covariance = np.array([[1.0, rho], [rho, 1.0]])
        sample = rng.multivariate_normal(mean, covariance, size=SAMPLE_SIZE)
        sample_frame = pd.DataFrame(sample, columns=["X", "Y"])
        sample_frame.to_csv(
            RESULTS_DIR / f"sample_rho_{file_label}.csv",
            index=False,
        )
        samples[rho] = sample_frame

    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#333333",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "font.size": 10,
            "legend.fontsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "savefig.facecolor": "white",
        }
    )

    scatter_figure, scatter_axes = plt.subplots(
        1,
        3,
        figsize=(14.5, 4.6),
        sharex=True,
        sharey=True,
    )

    for axis, (rho, _, color) in zip(scatter_axes, RHO_SETTINGS, strict=True):
        sample_frame = samples[rho]
        axis.scatter(
            sample_frame["X"],
            sample_frame["Y"],
            s=16,
            alpha=0.58,
            color=color,
            edgecolors="none",
        )
        axis.set(
            xlim=AXIS_LIMITS,
            ylim=AXIS_LIMITS,
            xticks=np.arange(-3, 4, 1),
            yticks=np.arange(-3, 4, 1),
            xlabel="X",
            ylabel="Y",
            title=rf"Theoretical correlation $\rho = {rho:.1f}$",
        )
        axis.set_aspect("equal", adjustable="box")
        axis.grid(color="#D9D9D9", linewidth=0.7, alpha=0.75)
        axis.set_axisbelow(True)

    scatter_figure.tight_layout(w_pad=2.0)
    scatter_figure.savefig(
        RESULTS_DIR / "fig_01_joint_scatter.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(scatter_figure)

    histogram_bins = np.linspace(AXIS_LIMITS[0], AXIS_LIMITS[1], 22)
    density_x = np.linspace(AXIS_LIMITS[0], AXIS_LIMITS[1], 800)
    theoretical_density = norm.pdf(density_x, loc=0.0, scale=1.0)

    marginal_figure, marginal_axes = plt.subplots(
        2,
        3,
        figsize=(14.5, 8.0),
        sharex=True,
        sharey=True,
    )

    theoretical_line = None
    for column, (rho, _, color) in enumerate(RHO_SETTINGS):
        sample_frame = samples[rho]
        for row, variable in enumerate(("X", "Y")):
            axis = marginal_axes[row, column]
            axis.hist(
                sample_frame[variable],
                bins=histogram_bins,
                density=True,
                color=color,
                alpha=0.68,
                edgecolor="white",
                linewidth=0.6,
            )
            (theoretical_line,) = axis.plot(
                density_x,
                theoretical_density,
                color="#1A1A1A",
                linewidth=1.8,
            )
            axis.set(
                xlim=AXIS_LIMITS,
                xticks=np.arange(-3, 4, 1),
                xlabel=variable,
                ylabel="Density",
                title=rf"{variable} marginal, $\rho = {rho:.1f}$",
            )
            axis.grid(color="#E0E0E0", linewidth=0.7, alpha=0.75)
            axis.set_axisbelow(True)

    marginal_figure.legend(
        [theoretical_line],
        ["Standard normal PDF"],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        frameon=False,
    )
    marginal_figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.95), h_pad=2.0, w_pad=1.8)
    marginal_figure.savefig(
        RESULTS_DIR / "fig_02_marginal_distributions.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(marginal_figure)

    print(f"Experiment 1 completed with seed {SEED}.")
    print(f"Results saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
