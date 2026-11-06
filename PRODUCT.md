# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Executives and analysts reviewing business segment performance, scenario assumptions, and market context.

## Product Purpose

Provide a dashboard for exploring public market history and descriptive indicators alongside segment performance fixtures and scenario analysis. Success means users can scan market context quickly, inspect the assumptions behind segment scenarios, and export the underlying information.

## Positioning

Combines automatically refreshed public market history and transparent, rule-based descriptive indicators with explainable segment scenarios in one dashboard. Market observations are not predictions or personalized financial advice.

## Operating Context

Users select market instruments and a history window, review refreshed market data and indicators, adjust scenario and segment filters, and export CSV or Markdown reports. The Streamlit session must remain active for automatic refresh.

## Capabilities and Constraints

- The web app uses Streamlit and Plotly.
- Market history comes from the Yahoo Finance chart endpoint; data is daily, may be delayed or unavailable, and is not guaranteed real-time.
- Market indicators are descriptive calculations based on selected history, not forecasts or trade signals.
- Segment economics are illustrative static fixtures, not live company financial statements.
- The running app includes a configurable market-linked segment scenario experiment using illustrative market proxies; it is not a measured sector beta or a prediction of company performance.
- Preserve existing dashboard workflows, calculations, filters, refresh controls, and CSV/Markdown exports unless explicitly changed.
- The repository's README and running app differ on whether segment scenarios are market-linked; the running app and forecasting implementation currently include the linked scenario experiment.

## Brand Commitments

Retain the product name “Segment Forecasting Dashboard” and its educational, non-advisory framing.

## Evidence on Hand

- Existing Streamlit app: `app.py`.
- Market data, analysis, forecasting, chart, and reporting modules: `src/segment_forecasting_dashboard/`.
- Segment data is defined in `src/segment_forecasting_dashboard/data.py`.
- Forecasting methodology: `docs/forecasting-methodology.md`.
- The repository includes screenshot and dashboard mockup assets under `docs/images/`.
- Do not fabricate market data, segment financial facts, customer proof, or investment recommendations.

## Product Principles

- Make market data freshness and source limitations legible.
- Distinguish observed market data from illustrative segment scenarios.
- Keep calculations and scenario assumptions explainable.
- Preserve useful filtering, refresh, and export workflows.
- Use neutral, educational language rather than recommendations.
