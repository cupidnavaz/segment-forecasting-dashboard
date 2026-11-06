# Operations Guide

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
streamlit run app.py
```

## Production deployment

The application can be deployed anywhere that supports Python and Streamlit.

Minimum production checklist:

1. Pin and audit dependencies.
2. Configure secrets outside source control.
3. Connect an approved data source.
4. Replace demo/static data with validated production data.
5. Run automated tests in CI.
6. Restrict access if the dashboard contains confidential business information.
7. Add application logging and monitoring.
8. Back up any persistent data source independently of the UI.

## Environment variables

The current rebuild does not require environment variables.

Future external integrations should document each variable in this file and provide a `.env.example` containing names only.

## Data limitations

Market observations are fetched as daily history from the Yahoo Finance chart
endpoint. They may be delayed, incomplete, unavailable, or incorrect and are
not guaranteed real-time quotes.

Segment economics are static illustrative fixtures, not verified company
financial statements. Market-proxy assignments are configurable scenario
assumptions, not measured sector relationships or predictions. The app does not
recalculate fixture fundamentals from market movement.

## Troubleshooting

### `ModuleNotFoundError: segment_forecasting_dashboard`

Install the project in editable mode:

```bash
python -m pip install -e .
```

### Streamlit does not start

Check:

```bash
python --version
python -m pip show streamlit
python -m streamlit run app.py
```

### Tests cannot import package

Run tests from the repository root and ensure `pytest` is installed from the development dependencies.
