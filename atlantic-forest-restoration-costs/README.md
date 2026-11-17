# Atlantic Forest restoration costs

Data and Python code supporting the study **Costs of Restoring Degraded Areas in the Atlantic Forest of Southwestern Bahia: A Monte Carlo Simulation Approach** (*Forests*, manuscript forests-4637810).

## Contents

- `data/restoration_project_budget.xlsx`: detailed original budget, including establishment and four maintenance years; footnotes removed and money displayed to two decimal places.
- `data/input_price_quotations.csv`: 10 anonymized quotations for each of eight stochastic inputs (80 records).
- `notebooks/restoration_costs_bootstrap_monte_carlo.ipynb`: step-by-step Monte Carlo simulation, risk metrics, convergence, and sensitivity.
- `src/restoration_monte_carlo.py`: reusable Python implementation using the same data files.
- `requirements.txt`: required Python packages.

## Run the analysis

From the repository root:

```bash
python -m pip install -r requirements.txt
jupyter notebook notebooks/restoration_costs_bootstrap_monte_carlo.ipynb
```

Select **Restart & Run All** in Jupyter. Alternatively, run `python src/restoration_monte_carlo.py`.

The notebook reads the budget directly from the Excel workbook. It independently resamples the original observed quotations with replacement, computes a mean price per input, multiplies by quantities from the workbook, and adds deterministic costs. The cost of brush-cutter operations is BRL 30/h × 60 h = BRL 1,800 (BRL 200 at establishment; BRL 400 in each of four maintenance years). The full budget is BRL 28,455.13/ha (inputs BRL 17,975.13; services BRL 10,480.00).

### Data consistency and reproducibility

**Important:** The observed price quotations in the earlier CSV have some mean prices that differ slightly from the mean unit prices used in the supplied final budget workbook (e.g., NPK 06-30-06: 5.2520 versus 5.2588038 BRL). The CSV is retained unchanged as observational data; the workbook is used as the authoritative deterministic budget. Two-decimal display formatting does not remove this underlying difference. Consequently, a fresh bootstrap Monte Carlo run may not exactly reproduce every published statistic. The source quotations and original random-state configuration should be reconciled to achieve exact replication. No observations have been modified or simulated results forced to match the manuscript.

All currency results in notebook tables are formatted to two decimal places, without premature rounding of computations. The seed `123` reproduces this repository run, **not necessarily the published run**.
