from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


MONTE_CARLO_SEED = 20261107
REPETITIONS = 1000
SAMPLE_SIZES = (30, 100, 500, 2000)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

RHO_SETTINGS = (
    (-0.9, "neg09", "#3B6EA8"),
    (0.0, "zero", "#6B6B6B"),
    (0.9, "pos09", "#C44E52"),
)


def main() -> None:
    sample_estimate_rows = []

    for rho, file_label, _ in RHO_SETTINGS:
        sample_frame = pd.read_csv(
            RESULTS_DIR / f"sample_rho_{file_label}.csv"
        )
        x_values = sample_frame["X"].to_numpy()
        y_values = sample_frame["Y"].to_numpy()
        sample_covariance = np.cov(x_values, y_values, ddof=1)[0, 1]
        sample_correlation = np.corrcoef(x_values, y_values)[0, 1]

        sample_estimate_rows.append(
            {
                "rho": rho,
                "sample_size": len(sample_frame),
                "mean_x": np.mean(x_values),
                "mean_y": np.mean(y_values),
                "std_x": np.std(x_values, ddof=1),
                "std_y": np.std(y_values, ddof=1),
                "theoretical_covariance": rho,
                "sample_covariance": sample_covariance,
                "covariance_error": sample_covariance - rho,
                "theoretical_correlation": rho,
                "sample_correlation": sample_correlation,
                "correlation_error": sample_correlation - rho,
            }
        )

    sample_estimates = pd.DataFrame(sample_estimate_rows)
    sample_estimates.to_csv(
        RESULTS_DIR / "table_03_sample_estimates.csv",
        index=False,
        float_format="%.10g",
    )

    rng = np.random.default_rng(MONTE_CARLO_SEED)
    mean = np.array([0.0, 0.0])
    monte_carlo_rows = []

    for rho, _, _ in RHO_SETTINGS:
        covariance_matrix = np.array([[1.0, rho], [rho, 1.0]])

        for sample_size in SAMPLE_SIZES:
            simulated_samples = rng.multivariate_normal(
                mean,
                covariance_matrix,
                size=(REPETITIONS, sample_size),
            )
            x_simulated = simulated_samples[:, :, 0]
            y_simulated = simulated_samples[:, :, 1]
            x_centered = x_simulated - np.mean(
                x_simulated,
                axis=1,
                keepdims=True,
            )
            y_centered = y_simulated - np.mean(
                y_simulated,
                axis=1,
                keepdims=True,
            )

            covariance_estimates = np.sum(
                x_centered * y_centered,
                axis=1,
            ) / (sample_size - 1)
            x_standard_deviations = np.sqrt(
                np.sum(x_centered**2, axis=1) / (sample_size - 1)
            )
            y_standard_deviations = np.sqrt(
                np.sum(y_centered**2, axis=1) / (sample_size - 1)
            )
            correlation_estimates = covariance_estimates / (
                x_standard_deviations * y_standard_deviations
            )

            covariance_mean = np.mean(covariance_estimates)
            correlation_mean = np.mean(correlation_estimates)

            monte_carlo_rows.append(
                {
                    "rho": rho,
                    "sample_size": sample_size,
                    "repetitions": REPETITIONS,
                    "covariance_mean": covariance_mean,
                    "covariance_bias": covariance_mean - rho,
                    "covariance_empirical_std": np.std(
                        covariance_estimates,
                        ddof=1,
                    ),
                    "covariance_rmse": np.sqrt(
                        np.mean((covariance_estimates - rho) ** 2)
                    ),
                    "correlation_mean": correlation_mean,
                    "correlation_bias": correlation_mean - rho,
                    "correlation_empirical_std": np.std(
                        correlation_estimates,
                        ddof=1,
                    ),
                    "correlation_rmse": np.sqrt(
                        np.mean((correlation_estimates - rho) ** 2)
                    ),
                }
            )

    monte_carlo_summary = pd.DataFrame(monte_carlo_rows)
    monte_carlo_summary.to_csv(
        RESULTS_DIR / "table_04_monte_carlo_estimation.csv",
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

    category_positions = np.arange(len(RHO_SETTINGS))
    category_labels = [rf"$\rho = {rho:.1f}$" for rho, _, _ in RHO_SETTINGS]
    bar_width = 0.34

    estimate_figure, estimate_axes = plt.subplots(
        1,
        2,
        figsize=(11.5, 4.8),
        sharey=True,
    )

    comparisons = (
        (
            "sample_covariance",
            "Sample Covariance vs. Population Covariance",
            "Covariance",
        ),
        (
            "sample_correlation",
            "Pearson Correlation vs. Population Correlation",
            "Correlation",
        ),
    )

    for axis, (sample_column, title, y_label) in zip(
        estimate_axes,
        comparisons,
        strict=True,
    ):
        axis.bar(
            category_positions - bar_width / 2,
            sample_estimates["rho"],
            width=bar_width,
            color="#B8B8B8",
            edgecolor="#555555",
            linewidth=0.8,
            label="Population value",
        )
        axis.bar(
            category_positions + bar_width / 2,
            sample_estimates[sample_column],
            width=bar_width,
            color="#3B6EA8",
            alpha=0.82,
            label="Sample estimate",
        )
        axis.axhline(0.0, color="#333333", linewidth=0.8)
        axis.set(
            xticks=category_positions,
            xticklabels=category_labels,
            ylim=(-1.05, 1.05),
            ylabel=y_label,
            title=title,
        )
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
        axis.set_axisbelow(True)
        axis.legend(frameon=False, loc="upper left")

    estimate_figure.tight_layout(w_pad=2.0)
    estimate_figure.savefig(
        RESULTS_DIR / "fig_05_sample_estimates.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(estimate_figure)

    accuracy_figure, accuracy_axes = plt.subplots(
        1,
        2,
        figsize=(11.5, 4.8),
    )

    for rho, _, color in RHO_SETTINGS:
        rho_results = monte_carlo_summary[
            monte_carlo_summary["rho"] == rho
        ]
        accuracy_axes[0].plot(
            rho_results["sample_size"],
            rho_results["correlation_rmse"],
            color=color,
            marker="o",
            linewidth=1.8,
            markersize=5,
            label=rf"$\rho = {rho:.1f}$",
        )
        accuracy_axes[1].plot(
            rho_results["sample_size"],
            rho_results["covariance_rmse"],
            color=color,
            marker="o",
            linewidth=1.8,
            markersize=5,
            label=rf"$\rho = {rho:.1f}$",
        )

    accuracy_axes[0].set(
        xlabel="Sample size n",
        ylabel="RMSE",
        title="Pearson Correlation Estimation",
    )
    accuracy_axes[1].set(
        xlabel="Sample size n",
        ylabel="RMSE",
        title="Sample Covariance Estimation",
    )

    for axis in accuracy_axes:
        axis.set_xscale("log")
        axis.set_xticks(SAMPLE_SIZES)
        axis.set_xticklabels([str(size) for size in SAMPLE_SIZES])
        axis.set_ylim(bottom=0.0)
        axis.grid(color="#D9D9D9", linewidth=0.7, alpha=0.75)
        axis.set_axisbelow(True)
        axis.legend(frameon=False)

    accuracy_figure.tight_layout(w_pad=2.0)
    accuracy_figure.savefig(
        RESULTS_DIR / "fig_06_estimation_accuracy.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(accuracy_figure)

    print("Experiment 3 completed.")
    print(f"Monte Carlo seed: {MONTE_CARLO_SEED}")
    print(f"Parameter combinations: {len(monte_carlo_summary)}")
    print(f"Repetitions per combination: {REPETITIONS}")


if __name__ == "__main__":
    main()
