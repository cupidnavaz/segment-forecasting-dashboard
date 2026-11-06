# Architecture

## Overview

The application follows a layered Python structure:

```text
Streamlit UI (app.py)
        │
        ├── charts.py
        ├── reporting.py
        └── analytics.py
                │
                └── forecasting.py
                        │
                        └── data.py
```

### `data.py`

Owns the canonical illustrative segment dataset. Market instruments and public
daily history are handled separately by `market_data.py`.

### `forecasting.py`

Contains deterministic business calculations:

- profit
- profit margin
- growth
- risk
- confidence
- trend
- scenario-adjusted growth
- filtering
- executive summary

This module does not import Streamlit.

### `market_data.py`

Fetches daily observations from the Yahoo Finance chart endpoint for the curated
watchlist, records per-symbol availability, and builds latest-close snapshots.

### `market_analysis.py`

Calculates descriptive returns, moving averages, historical volatility, and
selected-window drawdowns from fetched observations.

### `market_forecasting.py`

Combines the deterministic segment fixture forecast with an optional bounded,
illustrative market-proxy adjustment to scenario growth only.

### `analytics.py`

Converts forecast metrics into explainable health scores, gaps, impact classifications, and recommended actions.

### `charts.py`

Contains Plotly figure builders. Charts receive data and return figures, keeping rendering logic out of the calculation engine.

### `reporting.py`

Builds executive reports and CSV exports from the same dataframe used by the dashboard.

### `app.py`

Owns user interaction, session state, layout, controls, and presentation.

## State model

Streamlit session state currently stores the editable segment dataset. Scenario and filter controls are represented by widget state and passed into pure functions.

## Extension points

Future versions can replace `data.py` with:

- CSV ingestion
- PostgreSQL
- REST API
- warehouse queries
- authenticated data connectors

without rewriting the core calculation engine.
