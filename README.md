<div align="center">

# 📊 Segment Forecasting Dashboard

### Turn segment economics into an explainable forecast.

Forecasting, scenario analysis, risk intelligence, and executive reporting — built with Python, Streamlit, and Plotly.

[![CI](https://github.com/cupidnavaz/segment-forecasting-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/cupidnavaz/segment-forecasting-dashboard/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/cupidnavaz/segment-forecasting-dashboard?label=coverage)](https://app.codecov.io/gh/cupidnavaz/segment-forecasting-dashboard)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](#requirements)
[![License: MIT](https://img.shields.io/badge/License-MIT-7C3AED.svg)](LICENSE)

[🚀 Get started](#-get-started) · [📸 See the dashboard](#-dashboard-gallery) · [🧭 Explore features](#-what-you-can-do) · [🐛 Report an issue](https://github.com/cupidnavaz/segment-forecasting-dashboard/issues)

</div>

---

## ✨ At a glance

| 📈 Revenue | 💹 Profit | 🌱 Average growth | 🎯 Confidence | ⚠️ High-risk segments |
|:---:|:---:|:---:|:---:|:---:|
| **4,620.0** | **1,340.0** | **23.6%** | **67%** | **3** |

*Illustrative values from the default fixture dataset; they are not live financial data.*

## 🧭 What you can do

| | Capability | What it helps you answer |
|:--:|---|---|
| 📊 | **Compare segment economics** | How do revenue, costs, profit, margin, and growth vary by segment? |
| 🎚️ | **Explore scenarios** | How do forecasts change when you adjust expected growth? |
| 🔎 | **Filter and sort** | Which segments match a risk, status, trend, or search criterion? |
| 🛡️ | **Review risk and health** | Which segments need attention, and what signals drive that assessment? |
| 🧠 | **Use explainable advisory** | What deterministic recommendations follow from the segment metrics? |
| 📤 | **Export executive outputs** | Can I share the forecast as CSV or a Markdown report? |

## 📸 Dashboard gallery

The gallery is arranged as full-width views so chart labels, controls, and table values stay readable. Select **🚀 Launch locally** below to explore the live, interactive dashboard.

### 1 · Overview — summary, revenue & mix

![Dashboard overview with summary metrics, revenue and profit, and revenue mix](docs/images/mockup-dashboard-overview.svg)

### 2 · Growth, risk & segment health

![Growth trajectory and risk distribution charts with the segment health radar](docs/images/mockup-multi-monitor-hero.svg)

### 3 · Segment health radar and controls

![Segment health radar with dashboard filters and source note](docs/images/mockup-segment-card.svg)

### 4 · Forecast table

![Forecast command center and readable segment forecast table](docs/images/mockup-mobile-header.svg)

## 🚀 Get started

### Install and run

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

<div align="center">

**[▶️ Launch the dashboard locally](#install-and-run)**　 **[📦 View the source](https://github.com/cupidnavaz/segment-forecasting-dashboard)**

</div>

## 📊 Analytics preview

The default fixture includes nine business segments. The bars below are a compact, illustrative view of revenue; exact values can be explored in the app and forecast table.

| Segment | Revenue | Relative scale |
|---|---:|:---|
| Tech & SaaS | 950 | `██████████` |
| Financial Services | 820 | `█████████░` |
| Energy & Utilities | 680 | `███████░░░` |
| Logistics | 580 | `██████░░░░` |
| Retail & E-Commerce | 450 | `█████░░░░░` |
| Telecom & Media | 390 | `████░░░░░░` |
| Manufacturing | 310 | `███░░░░░░░` |
| Consumer Goods | 230 | `██░░░░░░░░` |
| Healthcare | 210 | `██░░░░░░░░` |

*These bars are static README illustrations, not interactive charts. Use the Streamlit app for interactive Plotly visualizations, filters, sorting, and scenario controls.*

## 🧰 Features

- **Forecasting:** segment-level revenue, costs, profit, margin, growth, confidence, risk, and trend.
- **Scenario analysis:** adjust growth assumptions and compare multi-year trajectories.
- **Interactive dashboard:** Plotly charts, filtering, search, sorting, and risk/status controls.
- **Explainable advisory:** deterministic signals with human-readable rationale.
- **Executive reporting:** generate Markdown reports and download forecast data as CSV.
- **Testable Python package:** forecasting and analytics logic is separate from the Streamlit interface.

## 🖱️ Dashboard controls

| Control | Purpose |
|---|---|
| Scenario growth adjustment | Model an alternative growth assumption. |
| Risk, status, and trend | Narrow the view to the segments that matter. |
| Search segment or period | Find a segment or forecast period quickly. |
| Sort by + ascending | Reorder results by a selected forecast metric. |
| Reset dataset | Restore the default segment fixtures. |
| Forecast table / Advisory / Executive report | Review detail, recommendations, or a shareable summary. |

## 📤 Reports & exports

- **CSV:** per-segment forecast data, downloadable from the app.
- **Markdown:** executive summary and report, downloadable from the app or generated by the CLI.

```bash
segment-dashboard export --format csv --output reports/segments.csv
segment-dashboard report --output reports/executive.md
```

## ⚙️ Requirements

- Python 3.11 or newer
- pip
- A browser for the Streamlit interface

## 🧪 Test and lint

```bash
pytest
ruff check .
```

## 🗂️ Project structure

```text
segment-forecasting-dashboard/
├── app.py
├── pyproject.toml
├── docs/                 # Methodology, operations, and screenshots
├── docs/images/          # README dashboard visuals
├── src/segment_forecasting_dashboard/
│   ├── analytics.py
│   ├── charts.py
│   ├── cli.py
│   ├── data.py
│   ├── forecasting.py
│   └── reporting.py
└── tests/
```

## 🛡️ Data notes

The project is a Python port of an earlier single-file HTML/JS demo. The included segment dataset and market ticker are static fixtures for illustration and reproducibility. **They are not live market data or financial advice.** See [data policy and operations](docs/operations.md) before connecting external data sources.

## 🤝 Contributing

Issues and pull requests are welcome. Please run `pytest` and `ruff check .` before submitting changes, and include screenshots for substantial UI updates. See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Made for clearer, more explainable segment decisions. · [⬆ Back to top](#-segment-forecasting-dashboard)

</div>

> **GitHub README limitation:** GitHub sanitizes embedded HTML and does not run custom JavaScript or CSS in README files. The README uses badges, links, tables, icons, and chart visuals for a modern presentation; the actual interactive analytics are in the Streamlit app. Animated media can be added as a GIF/video asset when one is available.
