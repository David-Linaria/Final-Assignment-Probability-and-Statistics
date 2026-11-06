from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr


ALPHA = 0.05
MONTE_CARLO_SEED = 20261108
REPETITIONS = 1000
SAMPLE_SIZES = (30, 100, 500, 2000)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

BASE_SAMPLE_SETTINGS = (
    (-0.9, "neg09"),
    (0.0, "zero"),
    (0.9, "pos09"),
)

POWER_SETTINGS = (
    (0.0, "#6B6B6B", "o"),
    (0.1, "#3B6EA8", "o"),
    (0.3, "#59A14F", "s"),
    (0.5, "#F28E2B", "^"),
    (0.9, "#C44E52", "D"),
)


def main() -> None:
    single_sample_rows = []

    for rho, file_label in BASE_SAMPLE_SETTINGS:
        sample_frame = pd.read_csv(
            RESULTS_DIR / f"sample_rho_{file_label}.csv"
        )
        sample_size = len(sample_frame)
        test_result = pearsonr(sample_frame["X"], sample_frame["Y"])
        sample_correlation = test_result.statistic
        p_value = test_result.pvalue
        t_statistic = sample_correlation * np.sqrt(sample_size - 2) / np.sqrt(
            1.0 - sample_correlation**2
        )

        single_sample_rows.append(
            {
                "rho": rho,
                "n": sample_size,
                "sample_correlation": sample_correlation,
                "t_statistic": t_statistic,
                "p_value": p_value,
                "alpha": ALPHA,
                "reject_h0": bool(p_value < ALPHA),
            }
        )

    single_sample_tests = pd.DataFrame(single_sample_rows)
    single_sample_tests.to_csv(
        RESULTS_DIR / "table_05_single_sample_tests.csv",
        index=False,
        float_format="%.12e",
    )

    rng = np.random.default_rng(MONTE_CARLO_SEED)
    mean = np.array([0.0, 0.0])
    monte_carlo_rows = []

    for rho, _, _ in POWER_SETTINGS:
        covariance_matrix = np.array([[1.0, rho], [rho, 1.0]])

        for sample_size in SAMPLE_SIZES:
            simulated_samples = rng.multivariate_normal(
                mean,
                covariance_matrix,
                size=(REPETITIONS, sample_size),
            )
            test_results = pearsonr(
                simulated_samples[:, :, 0],
                simulated_samples[:, :, 1],
                axis=1,
            )
            p_values = test_results.pvalue
            rejection_count = np.count_nonzero(p_values < ALPHA)
            rejection_rate = rejection_count / REPETITIONS
            monte_carlo_se = np.sqrt(
                rejection_rate * (1.0 - rejection_rate) / REPETITIONS
            )

            monte_carlo_rows.append(
                {
                    "rho": rho,
                    "n": sample_size,
                    "repetitions": REPETITIONS,
                    "alpha": ALPHA,
                    "rejection_count": rejection_count,
                    "rejection_rate": rejection_rate,
                    "monte_carlo_se": monte_carlo_se,
                    "metric_type": "type_i_error" if rho == 0.0 else "power",
                }
            )

            if rho == 0.0 and sample_size == 100:
                null_pvalues_n100 = p_values.copy()

    monte_carlo_testing = pd.DataFrame(monte_carlo_rows)
    monte_carlo_testing.to_csv(
        RESULTS_DIR / "table_06_monte_carlo_testing.csv",
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

    null_n100_result = monte_carlo_testing[
        (monte_carlo_testing["rho"] == 0.0)
        & (monte_carlo_testing["n"] == 100)
    ].iloc[0]

    null_figure, null_axis = plt.subplots(figsize=(8.4, 5.2))
    null_axis.axvspan(
        0.0,
        ALPHA,
        color="#C44E52",
        alpha=0.14,
        label=rf"Rejection region: $p < {ALPHA}$",
    )
    null_axis.hist(
        null_pvalues_n100,
        bins=np.linspace(0.0, 1.0, 21),
        density=True,
        color="#3B6EA8",
        alpha=0.72,
        edgecolor="white",
        linewidth=0.7,
        label="Simulated p-values",
    )
    null_axis.axhline(
        1.0,
        color="#1A1A1A",
        linewidth=1.8,
        label=r"Uniform density $U(0,1)$",
    )
    null_axis.axvline(
        ALPHA,
        color="#C44E52",
        linestyle="--",
        linewidth=1.8,
        label=rf"Significance threshold $\alpha={ALPHA}$",
    )
    null_axis.text(
        0.98,
        0.93,
        (
            "Empirical Type I error = "
            f"{null_n100_result['rejection_rate']:.3f}"
        ),
        transform=null_axis.transAxes,
        ha="right",
        va="top",
    )
    null_axis.set(
        xlim=(0.0, 1.0),
        xlabel="Two-sided p-value",
        ylabel="Density",
        title=r"Null p-value Distribution ($\rho=0$, $n=100$)",
    )
    null_axis.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.75)
    null_axis.set_axisbelow(True)
    null_axis.legend(frameon=False, loc="upper left")

    null_figure.tight_layout()
    null_figure.savefig(
        RESULTS_DIR / "fig_07_null_pvalues.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(null_figure)

    performance_figure, performance_axes = plt.subplots(
        1,
        2,
        figsize=(11.8, 4.8),
    )

    type_i_results = monte_carlo_testing[
        monte_carlo_testing["metric_type"] == "type_i_error"
    ]
    performance_axes[0].plot(
        type_i_results["n"],
        type_i_results["rejection_rate"],
        color="#3B6EA8",
        marker="o",
        linewidth=1.8,
        markersize=5,
        label="Empirical Type I error",
    )
    performance_axes[0].axhline(
        ALPHA,
        color="#C44E52",
        linestyle="--",
        linewidth=1.8,
        label=rf"Nominal $\alpha={ALPHA}$",
    )
    performance_axes[0].set(
        xlabel="Sample size n",
        ylabel="Rejection rate",
        ylim=(0.0, 0.12),
        title=r"Type I Error ($\rho=0$)",
    )
    performance_axes[0].legend(frameon=False, loc="upper right")

    for rho, color, marker in POWER_SETTINGS[1:]:
        power_results = monte_carlo_testing[
            monte_carlo_testing["rho"] == rho
        ]
        performance_axes[1].plot(
            power_results["n"],
            power_results["rejection_rate"],
            color=color,
            marker=marker,
            linewidth=1.8,
            markersize=5,
            label=rf"$\rho={rho:.1f}$",
        )

    performance_axes[1].set(
        xlabel="Sample size n",
        ylabel="Empirical power",
        ylim=(0.0, 1.03),
        title="Statistical Power",
    )
    performance_axes[1].legend(frameon=False, loc="lower right")

    for axis in performance_axes:
        axis.set_xscale("log")
        axis.set_xticks(SAMPLE_SIZES)
        axis.set_xticklabels([str(size) for size in SAMPLE_SIZES])
        axis.grid(color="#D9D9D9", linewidth=0.7, alpha=0.75)
        axis.set_axisbelow(True)

    performance_figure.tight_layout(w_pad=2.0)
    performance_figure.savefig(
        RESULTS_DIR / "fig_08_testing_performance.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(performance_figure)

    print("Experiment 4 completed.")
    print(f"Monte Carlo seed: {MONTE_CARLO_SEED}")
    print(f"Parameter combinations: {len(monte_carlo_testing)}")
    print(f"Total tests: {len(monte_carlo_testing) * REPETITIONS}")


if __name__ == "__main__":
    main()
