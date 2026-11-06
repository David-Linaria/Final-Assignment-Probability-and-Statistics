from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm


RHO = 0.9
LOWER_X = 0.5
UPPER_X = 1.0
AXIS_LIMITS = (-3.5, 3.5)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"


def main() -> None:
    sample_path = RESULTS_DIR / "sample_rho_pos09.csv"
    sample_frame = pd.read_csv(sample_path)
    conditional_frame = sample_frame[
        (sample_frame["X"] > LOWER_X) & (sample_frame["X"] < UPPER_X)
    ]

    original_y_mean = sample_frame["Y"].mean()
    original_y_variance = sample_frame["Y"].var(ddof=1)
    conditional_y_mean = conditional_frame["Y"].mean()
    conditional_y_variance = conditional_frame["Y"].var(ddof=1)

    interval_probability = norm.cdf(UPPER_X) - norm.cdf(LOWER_X)
    truncated_x_mean = (
        norm.pdf(LOWER_X) - norm.pdf(UPPER_X)
    ) / interval_probability
    truncated_x_variance = (
        1.0
        + (
            LOWER_X * norm.pdf(LOWER_X)
            - UPPER_X * norm.pdf(UPPER_X)
        )
        / interval_probability
        - truncated_x_mean**2
    )
    theoretical_conditional_y_mean = RHO * truncated_x_mean
    theoretical_conditional_y_variance = (
        1.0 - RHO**2 + RHO**2 * truncated_x_variance
    )

    predicted_y = RHO * sample_frame["X"].to_numpy()
    prediction_errors = sample_frame["Y"].to_numpy() - predicted_y
    sample_prediction_mse = np.mean(prediction_errors**2)
    theoretical_prediction_mse = 1.0 - RHO**2

    summary_table = pd.DataFrame(
        [
            {
                "statistic": "original_sample_size",
                "theoretical_value": len(sample_frame),
                "sample_value": len(sample_frame),
            },
            {
                "statistic": "conditional_sample_size",
                "theoretical_value": None,
                "sample_value": len(conditional_frame),
            },
            {
                "statistic": "marginal_y_mean",
                "theoretical_value": 0.0,
                "sample_value": original_y_mean,
            },
            {
                "statistic": "marginal_y_variance",
                "theoretical_value": 1.0,
                "sample_value": original_y_variance,
            },
            {
                "statistic": "conditional_y_mean",
                "theoretical_value": theoretical_conditional_y_mean,
                "sample_value": conditional_y_mean,
            },
            {
                "statistic": "conditional_y_variance",
                "theoretical_value": theoretical_conditional_y_variance,
                "sample_value": conditional_y_variance,
            },
            {
                "statistic": "prediction_mse",
                "theoretical_value": theoretical_prediction_mse,
                "sample_value": sample_prediction_mse,
            },
        ]
    )
    summary_table.to_csv(
        RESULTS_DIR / "table_02_conditional_summary.csv",
        index=False,
        float_format="%.10g",
    )

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

    histogram_bins = np.linspace(AXIS_LIMITS[0], AXIS_LIMITS[1], 29)
    density_y = np.linspace(AXIS_LIMITS[0], AXIS_LIMITS[1], 800)

    distribution_figure, distribution_axes = plt.subplots(
        1,
        2,
        figsize=(12.0, 4.8),
        sharex=True,
    )

    distribution_axes[0].hist(
        sample_frame["Y"],
        bins=histogram_bins,
        density=True,
        color="#6B6B6B",
        alpha=0.68,
        edgecolor="white",
        linewidth=0.6,
    )
    distribution_axes[0].plot(
        density_y,
        norm.pdf(density_y),
        color="#1A1A1A",
        linewidth=1.8,
        label="Standard normal PDF",
    )
    distribution_axes[0].axvline(
        original_y_mean,
        color="#C44E52",
        linestyle="--",
        linewidth=1.8,
        label=f"Sample mean = {original_y_mean:.3f}",
    )
    distribution_axes[0].set(
        xlim=AXIS_LIMITS,
        xlabel="Y",
        ylabel="Density",
        title=f"Marginal Y (n = {len(sample_frame)})",
    )
    distribution_axes[0].legend(frameon=False, loc="upper left")

    distribution_axes[1].hist(
        conditional_frame["Y"],
        bins=histogram_bins,
        density=True,
        color="#C44E52",
        alpha=0.72,
        edgecolor="white",
        linewidth=0.6,
    )
    distribution_axes[1].axvline(
        conditional_y_mean,
        color="#3B6EA8",
        linestyle="--",
        linewidth=1.8,
        label=f"Sample mean = {conditional_y_mean:.3f}",
    )
    distribution_axes[1].set(
        xlim=AXIS_LIMITS,
        xlabel="Y",
        ylabel="Density",
        title=(
            f"Conditional Y: {LOWER_X} < X < {UPPER_X} "
            f"(n = {len(conditional_frame)})"
        ),
    )
    distribution_axes[1].legend(frameon=False, loc="upper right")

    for axis in distribution_axes:
        axis.grid(color="#E0E0E0", linewidth=0.7, alpha=0.75)
        axis.set_axisbelow(True)

    distribution_figure.tight_layout(w_pad=2.0)
    distribution_figure.savefig(
        RESULTS_DIR / "fig_03_conditional_distribution.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(distribution_figure)

    prediction_x = np.linspace(AXIS_LIMITS[0], AXIS_LIMITS[1], 800)
    prediction_mean = RHO * prediction_x
    prediction_margin = 1.96 * np.sqrt(theoretical_prediction_mse)

    prediction_figure, prediction_axis = plt.subplots(figsize=(8.6, 6.2))
    prediction_axis.axvspan(
        LOWER_X,
        UPPER_X,
        color="#E0B44C",
        alpha=0.20,
        label=f"Condition range: {LOWER_X} < X < {UPPER_X}",
        zorder=0,
    )
    prediction_axis.fill_between(
        prediction_x,
        prediction_mean - prediction_margin,
        prediction_mean + prediction_margin,
        color="#C44E52",
        alpha=0.16,
        label="Theoretical 95% conditional prediction interval",
        zorder=1,
    )
    prediction_axis.scatter(
        sample_frame["X"],
        sample_frame["Y"],
        s=18,
        alpha=0.52,
        color="#3B6EA8",
        edgecolors="none",
        label="Observed sample",
        zorder=2,
    )
    prediction_axis.plot(
        prediction_x,
        prediction_mean,
        color="#A52A2A",
        linewidth=2.0,
        label=rf"Theoretical conditional mean: $E(Y\mid X=x)={RHO}x$",
        zorder=3,
    )
    prediction_axis.set(
        xlim=AXIS_LIMITS,
        ylim=(-4.1, 4.1),
        xlabel="X",
        ylabel="Y",
        title=rf"Conditional Mean and Prediction Interval ($\rho = {RHO}$)",
    )
    prediction_axis.grid(color="#D9D9D9", linewidth=0.7, alpha=0.75)
    prediction_axis.set_axisbelow(True)
    prediction_axis.legend(frameon=False, loc="upper left")

    prediction_figure.tight_layout()
    prediction_figure.savefig(
        RESULTS_DIR / "fig_04_conditional_prediction.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(prediction_figure)

    print(f"Original sample size: {len(sample_frame)}")
    print(f"Conditional sample size: {len(conditional_frame)}")
    print(
        "Conditional Y mean (theoretical, sample): "
        f"{theoretical_conditional_y_mean:.6f}, {conditional_y_mean:.6f}"
    )
    print(
        "Conditional Y variance (theoretical, sample): "
        f"{theoretical_conditional_y_variance:.6f}, "
        f"{conditional_y_variance:.6f}"
    )
    print(
        "Prediction MSE (theoretical, sample): "
        f"{theoretical_prediction_mse:.6f}, {sample_prediction_mse:.6f}"
    )


if __name__ == "__main__":
    main()
