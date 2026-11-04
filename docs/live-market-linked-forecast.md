# Live market-linked scenario demo

The dashboard now recalculates its **scenario growth overlay** from refreshed market history. Each illustrative business segment is mapped to a broad market proxy; the proxy's recent return is converted into a bounded growth adjustment. The overlay feeds the growth trajectory chart, filtering/sorting, and downloadable forecast/report.

**This does not turn fixture revenues into live company fundamentals.** Revenue, costs, margin, confidence, churn, market share, and competition remain demo fixtures. Proxy assignments and the sensitivity formula are configurable heuristics, not empirically estimated sector betas, financial advice, or predictions. The live feed currently remains the Yahoo Finance chart endpoint; NxCore is not connected by these changes.

In the Streamlit sidebar, configure the feed instruments, return lookback, sensitivity, maximum adjustment, scenario override, and automatic refresh interval. The whole dashboard fragment refreshes together so live history and the forecast overlay are recalculated in the same update cycle while the browser session remains active.

Run `pytest` and `ruff check .` to validate changes. Production/commercial deployment requires a market-data license covering your intended use and a provider-backed adapter; configure authentication, API secrets, network policy, access control, and audit requirements for the chosen hosting environment.
