# Segment Forecasting Dashboard

A standard Python rebuild of my initial segments forecasting dashboard built with just HTML, CSS & Javascript.

Unlike the initial project which contained both the enhine and the design in just one simple HTML file, This project separates the original dashboard's data model, calculation engine, advisory logic, charting, reporting, tests, and UI into maintainable Python modules. The application uses Streamlit for the interactive dashboard and Plotly for visualizations.

## Features

- Segment-level revenue, cost, profit, margin, growth, confidence, risk, and trend calculations.
- Scenario growth adjustment.
- Risk, status, trend, and text filters.
- Stable sorting across calculated metrics.
- Revenue/profit comparison.
- Revenue mix visualization.
- Multi-year growth trajectory.
- Risk distribution.
- Segment health radar.
- Explainable advisory scoring.
- CSV export.
- Executive Markdown report export.
- Automated tests for the calculation engine, advisory layer, and reporting.
- Packaging through `pyproject.toml`.
- Ruff and pytest development tooling.

## Source lineage

The initial project was built as a demo to try out insights. Its JavaScript calculation engine defined the canonical segment dataset and formulas. This rebuild preserves those business rules while moving them into Python modules.

The original market ticker is retained only as a static data fixture in this version. It should not be presented as real-time financial data without connecting it to a verified market-data provider.

## Project structure

```text
segment-forecasting-dashboard/
├── app.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── .gitignore
├── .streamlit/
│   └── config.toml
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── forecasting-methodology.md
│   ├── operations.md
│   └── release-checklist.md
├── src/
│   └── segment_forecasting_dashboard/
│       ├── __init__.py
│       ├── analytics.py
│       ├── charts.py
│       ├── cli.py
│       ├── data.py
│       ├── forecasting.py
│       └── reporting.py
└── tests/
    ├── test_analytics.py
    ├── test_forecasting.py
    └── test_reporting.py
```

## Requirements

- Python 3.11+
- pip
- A browser for the Streamlit UI

Python 3.13 is supported by the project metadata, subject to the availability of compatible wheels for the selected dependencies.

## Installation

### macOS / Linux

```bash
git clone <repository-url>
cd segment-forecasting-dashboard

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Windows PowerShell

```powershell
git clone <repository-url>
cd segment-forecasting-dashboard

py -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run

```bash
streamlit run app.py
```

Or, after editable installation:

```bash
segment-dashboard
```

## Test

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Build package

```bash
python -m pip install --upgrade build
python -m build
```

## Git workflow

Before the first commit:

```bash
git init
git add .
git status
git diff --cached
git commit -m "feat: rebuild segment forecasting dashboard as Python project"
```

Then connect the GitHub remote:

```bash
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

Replace `<repository-url>` with the actual repository URL. The project intentionally does not hard-code a remote because repository ownership and destination are deployment choices.

## Design decisions

1. **Business logic is independent of Streamlit.** This makes the formulas testable and reusable.
2. **Data is explicit.** The original dashboard's nine-segment dataset is kept in `data.py`.
3. **Reports are generated from the same forecast dataframe used by the UI.** This prevents the report from drifting away from the dashboard.
4. **No fake live data.** Static ticker values are clearly labeled as fixtures.
5. **Tests target behavior, not implementation details.**
6. **Packaging uses PEP 621 metadata.**

## License

MIT. See `LICENSE`.
