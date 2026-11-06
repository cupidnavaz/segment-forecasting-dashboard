# Segment Forecasting Dashboard

**A modern, interactive workspace for daily market context, transparent segment scenarios, and executive-ready exports.**

The Streamlit app pairs automatically refreshed public market history with descriptive indicators and a separate, explainable segment-scenario experiment. The segment figures are static illustrative fixtures. Market-proxy adjustments can change scenario growth only; they do not update revenue, costs, margins, churn, or confidence and are not measured relationships or predictions.

[![CI](https://github.com/cupidnavaz/segment-forecasting-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/cupidnavaz/segment-forecasting-dashboard/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](#requirements)
[![License: MIT](https://img.shields.io/badge/License-MIT-7C3AED.svg)](LICENSE)

> **Start the interactive dashboard:** `streamlit run app.py`
> README tables and diagrams explain the app; the widgets, KPI cards, filters, and charts are interactive in the running dashboard.

## Contents

- [Dashboard at a glance](#dashboard-at-a-glance)
- [Interactive controls and KPIs](#interactive-controls-and-kpis)
- [Charts and analysis](#charts-and-analysis)
- [Automated refresh and market data](#automated-refresh-and-market-data)
- [Scenario methodology](#scenario-methodology)
- [Reports and exports](#reports-and-exports)
- [Quick start](#quick-start)
- [Project structure](#project-structure)
- [Tests and quality checks](#tests-and-quality-checks)
- [Data limitations and disclaimer](#data-limitations-and-disclaimer)

## Dashboard at a glance

Choose a workspace from the sidebar. Each view retains the shared market and scenario controls, so changing a filter updates the relevant dashboard results and exports.

| Workspace | What it shows |
|---|---|
| **Market overview** | Latest available closes and daily changes, interactive instrument comparison, historical risk chart, latest indicator table, and descriptive observations. |
| **Instrument analysis** | A selected instrument’s close history, optional 20- and 50-observation averages, current-window KPIs, and downloadable observation history. |
| **Segment scenarios** | Illustrative fixture KPIs, revenue/profit and mix charts, adjusted growth and risk views, a segment-health comparison, forecast table, and explainable advisory signals. |
| **Reports** | A combined market briefing and executive scenario report, with Markdown and CSV downloads. |

The interface uses a restrained “Statistical Atlas” visual language: warm chart-stock surfaces, ink-blue navigation, precise chart annotations, and responsive metric/chart cards. Cards group related information rather than decorating it; source freshness and illustrative-data caveats remain visible.

## Interactive controls and KPIs

### Market widgets

| Widget | Interaction |
|---|---|
| **Instruments** | Select one or more symbols from the curated watchlist. |
| **History window** | Choose `1mo`, `3mo`, `6mo`, `1y`, or `2y` of daily observations. |
| **Auto-refresh** | Re-fetch the selected history while the Streamlit browser session is active. |
| **Refresh interval** | Set the automatic refresh cadence to 1, 5, 15, or 30 minutes. |
| **Chart view** | Switch between normalized indexed comparison and one instrument’s close with optional rolling averages. |
| **Refresh data** | Request a fresh snapshot immediately. |
| **Animate chart transitions** | Enable or disable Plotly transitions. Reduced-motion preferences are also honored in the stylesheet. |

Market pulse cards show latest available closes and previous-observation changes for up to four selected instruments. Instrument-analysis KPI cards show the latest close, daily change, 20-observation average, and drawdown for the active selection.

### Segment widgets

Scenario controls are available in the sidebar:

- **Scenario adjustment:** add a user-selected growth adjustment in percentage points.
- **Proxy sensitivity, lookback, and adjustment cap:** tune the illustrative market-linked growth experiment.
- **Risk, status, and trend:** filter segment rows.
- **Search:** find a segment name or forecast period.
- **Sort field and direction:** reorder the filtered view.
- **Reset segment fixtures:** restore the built-in illustrative dataset for the current session.

The segment KPI cards summarize filtered fixture revenue, fixture profit, adjusted scenario growth, fixture confidence, and the number of high-risk fixtures. These values update with the filters and scenario inputs; they are not reported company results.

## Charts and analysis

Plotly charts support hover inspection, legends, zoom, and pan where applicable. Chart annotations and labels distinguish historical observations from scenario outputs.

| View | Visualizations |
|---|---|
| **Market overview** | Indexed close comparison; focused close history with optional 20-/50-observation averages; annualized historical volatility and selected-window drawdown. |
| **Instrument analysis** | Focused daily close and moving-average chart plus a sortable-by-date observation table. |
| **Segment scenarios** | Grouped fixture revenue/profit bars; revenue-mix doughnut; market-adjusted growth trajectory; risk distribution; and a health-comparison radar for up to five leading segments. |

Market indicators include daily percentage return, 20- and 50-observation simple moving averages, 20-observation annualized historical volatility, and drawdown from the selected-window high. Rule-based observations describe those readings; they do not issue trade signals.

## Automated refresh and market data

- **Provider:** Yahoo Finance chart endpoint, using daily intervals for a curated list of indices, commodities, and crypto assets.
- **Symbols:** S&P 500 (`^GSPC`), NASDAQ Composite (`^IXIC`), Dow Jones Industrial Average (`^DJI`), crude oil futures (`CL=F`), gold futures (`GC=F`), Bitcoin (`BTC-USD`), and Ethereum (`ETH-USD`).
- **Refresh cadence:** the Streamlit fragment refreshes the view at the selected interval while the app session remains connected. A manual refresh is also available.
- **Resilience:** individual symbol failures are surfaced while available instruments can still load; if no selected market history is available, the app displays a recoverable provider error.
- **Freshness:** retrieval time is shown when supplied by the data fetch. Daily observations are not guaranteed real-time quotes.
- **Caching:** market fetches use Streamlit’s data cache and a refresh-bucket key to allow a new request on the configured cadence.

This is a session-driven dashboard refresh, not a scheduled background job or guaranteed market feed. Provider delays, outages, terms, and rate limits may change.

## Scenario methodology

The dashboard combines deterministic calculations on the built-in segment fixtures with an optional, bounded market-proxy adjustment. The user scenario and proxy adjustment affect `scenario_growth` only:

```text
market_adjustment_pp =
    clip(proxy_return_over_lookback × sensitivity, -maximum_adjustment, +maximum_adjustment)

scenario_growth = base_growth + user_scenario + market_adjustment_pp
```

Proxy mappings are illustrative assumptions—not empirical sector betas. Missing proxy history contributes no proxy adjustment and is marked in the scenario data. The underlying fixture fundamentals are not recalculated from market movements.

The baseline profit, margin, growth, risk, confidence, trend, and proxy-adjustment rules are documented in [Forecasting Methodology](docs/forecasting-methodology.md). Segment fields and derived values are described in the [Data Model](docs/data-model.md), and implementation boundaries are covered in [Architecture](docs/architecture.md).

## Reports and exports

Download actions are available from the dashboard:

- **Market history CSV** for the selected instruments.
- **Instrument history CSV** for the focused symbol.
- **Filtered market-linked forecast CSV** from the scenario table or Reports view.
- **Combined executive Markdown report** with the filtered fixture summary and source-attributed latest market context.

Exports use the active filters and scenario settings. They retain the demo/illustrative framing in report text and field labels.

## Quick start

### Requirements

- Python 3.11 or newer
- Internet access for the Yahoo Finance chart endpoint

### Windows PowerShell

```powershell
git clone https://github.com/cupidnavaz/segment-forecasting-dashboard.git
Set-Location segment-forecasting-dashboard
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
streamlit run app.py
```

If PowerShell blocks activation, use the Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS / Linux

```bash
git clone https://github.com/cupidnavaz/segment-forecasting-dashboard.git
cd segment-forecasting-dashboard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
streamlit run app.py
```

After launch, open the local URL printed by Streamlit. Select instruments and a history window in the sidebar, then leave **Auto-refresh** enabled to refresh the live market context while the browser session remains active. To start the same app from an installed environment, use `segment-dashboard`.

## Project structure

```text
.
├── app.py
├── styles.css
├── pyproject.toml
├── src/
│   └── segment_forecasting_dashboard/
│       ├── analytics.py             # explainable fixture advisory signals
│       ├── charts.py                # reusable Plotly figures
│       ├── cli.py                   # installed dashboard launcher
│       ├── data.py                  # canonical illustrative segment fixtures
│       ├── forecasting.py           # deterministic calculations and filters
│       ├── market_analysis.py       # descriptive market indicators
│       ├── market_data.py           # Yahoo Finance fetch and snapshot helpers
│       ├── market_forecasting.py    # bounded proxy-linked scenario experiment
│       └── reporting.py             # Markdown and CSV exports
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── forecasting-methodology.md
│   ├── live-market-linked-forecast.md
│   ├── operations.md
│   └── release-checklist.md
└── tests/
```

The UI, data fetching, calculations, chart builders, and reporting helpers are separated so the deterministic forecast logic can be tested independently from Streamlit. See [Architecture](docs/architecture.md) for module responsibilities and extension points.

## Tests and quality checks

Install the development extras with `python -m pip install -e ".[dev]"`, then run:

```bash
pytest
ruff check .
```

The tests cover market-data parsing and snapshots, descriptive market indicators, forecast and scenario calculations, chart generation, advisory logic, and reporting/export behavior.

## Data limitations and disclaimer

This project is for general educational market context and descriptive analytics. It does **not** provide personalized financial, investment, tax, or legal advice, and it does not recommend buying, selling, or holding any security. It should not be used as the sole basis for an investment decision.

Market history may be delayed, incomplete, unavailable, or incorrect. Historical returns, averages, volatility, and drawdowns are descriptive—not predictions. Segment economics are static demo fixtures, not live company financial statements. Market-proxy mappings and scenario adjustments are illustrative and do not establish causality or forecast company performance. Past performance does not guarantee future results.

For production or commercial use, select a properly licensed market-data provider and comply with its terms. See [SECURITY.md](SECURITY.md) for vulnerability reporting and [LICENSE](LICENSE) for license terms.
