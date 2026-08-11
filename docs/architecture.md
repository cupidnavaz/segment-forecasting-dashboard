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

Owns the canonical source dataset and static ticker fixtures.

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
