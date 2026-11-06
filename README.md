# Correlation Structure and Statistical Inference of the Bivariate Normal Distribution

This project supports an undergraduate probability and statistics study of the correlation structure, conditional distributions, parameter estimation, and statistical inference of the bivariate normal distribution. Monte Carlo experiments will compare theoretical results with reproducible numerical evidence generated in Python.

## Main Tools

- Python 3.14.7
- NumPy
- SciPy
- Matplotlib
- pandas
- Git and Visual Studio Code

## Project Structure

```text
Final-Assignment-Probability-and-Statistics/
|-- .venv/                 # Project-local Python environment (not tracked by Git)
|-- .vscode/
|   `-- settings.json      # VS Code interpreter configuration
|-- src/                   # Python experiment programs
|   |-- .gitkeep
|   `-- experiment_01.py   # Joint and marginal distribution simulation
|-- results/               # Figures, tables, and experiment records
|   |-- .gitkeep
|   |-- sample_rho_neg09.csv
|   |-- sample_rho_zero.csv
|   |-- sample_rho_pos09.csv
|   |-- fig_01_joint_scatter.png
|   `-- fig_02_marginal_distributions.png
|-- .gitignore
|-- README.md
`-- requirements.txt
```

## Environment Setup on Windows

Create the virtual environment from PowerShell in the project root:

```powershell
python -m venv .venv
```

Activate it and install the pinned dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

VS Code is configured to use `.venv\Scripts\python.exe` automatically. To verify the interpreter and imports:

```powershell
python --version
python -c "import numpy, scipy, matplotlib, pandas; print('Imports successful')"
```

## Experiment 1: Joint and Marginal Distributions

Experiment 1 generates 500 observations from each standardized bivariate normal model with theoretical correlations -0.9, 0, and 0.9. It saves the three samples as CSV files and produces publication-ready comparisons of the joint scatter plots and marginal density histograms. The random seed is fixed at `20261106` for reproducibility.

Run the experiment from the project root after activating the virtual environment:

```powershell
python src/experiment_01.py
```

The generated CSV files and 300-DPI PNG figures are written to `results/`.

## Experiment Plan

The planned study covers joint and marginal distributions, conditional distributions and prediction error, sample covariance and Pearson correlation estimation, the effect of sample size on estimation accuracy, and hypothesis tests for zero correlation with simulated Type I error rates and statistical power.

## Development Status

**Experiment 1 complete** — the environment is initialized, and the reproducible bivariate normal sampling and joint/marginal distribution visualizations are implemented.
