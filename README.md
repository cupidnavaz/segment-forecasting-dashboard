# 📊 Segment Forecasting Dashboard

### Live market intelligence, explainable segment scenarios, and executive reporting.

This Streamlit demo combines **automatically refreshed public market history** with transparent descriptive indicators. The segment economics are a separate illustrative fixture dataset and are not linked to or recalculated from market prices.

[![CI](https://github.com/cupidnavaz/segment-forecasting-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/cupidnavaz/segment-forecasting-dashboard/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](#requirements)
[![License: MIT](https://img.shields.io/badge/License-MIT-7C3AED.svg)](LICENSE)

## What the demo does

- Fetches daily historical close and volume for a curated watchlist of indices, commodities, and crypto assets through the Yahoo Finance chart endpoint.
- Automatically refreshes market data and recalculates returns, rolling averages, historical volatility, drawdown, and neutral market observations on a selectable interval while the app session is open.
- Offers manual refresh, interactive price/average charts, and CSV/Markdown exports.
- Keeps the existing segment forecast and scenario analysis clearly marked as illustrative, static fixtures.

## Run locally

```bash
git clone https://github.com/cupidnavaz/segment-forecasting-dashboard.git
cd segment-forecasting-dashboard
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
streamlit run app.py
```

In the sidebar, select instruments, choose a lookback window, leave **Automatically refresh** enabled, and select the refresh cadence. The live market panel refreshes while the browser session remains connected. **Refresh now** fetches a fresh snapshot immediately.

## Data, update, and limitations

- **Market source:** Yahoo Finance chart endpoint. It provides the latest data available from the source; daily series do not mean real-time quotes. Provider availability, delay, terms, and rate limits may change. For production/commercial use, choose a licensed market-data provider and follow its terms.
- **Refresh behavior:** the Streamlit session reruns the market panel at the selected interval (1, 5, 15, or 30 minutes). A cache key changes on each interval, so new data is fetched and all derived indicators recalculate. The browser/app session must remain active. This is not a background server job or guaranteed market feed.
- **Indicators:** returns, 20/50-observation simple moving averages, annualized rolling historical volatility, and drawdown are descriptive calculations based on the selected history. They are not predictions.
- **Business segment figures:** remain static fixtures and are not live company financial statements or market-derived forecasts.

## Financial advice disclaimer

This project provides **general educational market data and descriptive analytics only**. It does not provide personalized financial, investment, tax, or legal advice; it does not recommend buying, selling, or holding any security; and it should not be used as the sole basis for an investment decision. Consult a qualified professional for advice tailored to your circumstances. Market data can be delayed, incomplete, or incorrect, and past performance does not guarantee future results.

## Tests and lint

```bash
pytest
ruff check .
```

## Project layout

```text
app.py
src/segment_forecasting_dashboard/
├── market_data.py       # public market source integration
├── market_analysis.py   # descriptive, reproducible indicators
├── forecasting.py       # segment fixture forecast calculations
├── charts.py
└── reporting.py
tests/
```

MIT — see [LICENSE](LICENSE).
