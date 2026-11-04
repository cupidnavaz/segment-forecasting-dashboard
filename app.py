"""Streamlit dashboard for live market intelligence and market-linked scenarios."""

from __future__ import annotations

import time
from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from segment_forecasting_dashboard.analytics import advisory_dataframe
from segment_forecasting_dashboard.charts import (
    growth_trend_chart,
    health_radar_chart,
    revenue_mix_chart,
    revenue_profit_chart,
    risk_distribution,
)
from segment_forecasting_dashboard.data import default_segments
from segment_forecasting_dashboard.forecasting import executive_summary, filter_forecast
from segment_forecasting_dashboard.market_analysis import market_indicators, market_risk_briefing
from segment_forecasting_dashboard.market_data import (
    WATCHLIST,
    MarketDataError,
    fetch_market_history,
    market_briefing_markdown,
    market_snapshot,
)
from segment_forecasting_dashboard.market_forecasting import (
    SEGMENT_MARKET_PROXIES,
    market_linked_forecast,
)
from segment_forecasting_dashboard.reporting import build_markdown_report, export_csv

st.set_page_config(
    page_title="Live Data Intelligence | Segment Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
    .block-container {max-width: 1500px; padding-top: 1.5rem;}
    [data-testid="stMetric"] {border: 1px solid rgba(148,163,184,.22); border-radius: 14px; padding: 14px;}
    .hero {padding: 1.4rem 1.5rem; border-radius: 18px; border: 1px solid rgba(59,130,246,.20); background: linear-gradient(135deg, rgba(59,130,246,.10), rgba(20,184,166,.07));}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Live market feed")
    symbols = st.multiselect(
        "Instruments",
        options=list(WATCHLIST),
        default=["^GSPC", "^IXIC", "CL=F", "GC=F"],
        format_func=lambda symbol: f"{WATCHLIST[symbol]} ({symbol})",
    )
    period = st.selectbox("History window", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    auto_refresh = st.toggle("Auto-refresh and recalculate", value=True)
    refresh_minutes = st.select_slider("Refresh interval (minutes)", [1, 5, 15, 30], value=5)
    sensitivity = st.slider("Market-scenario sensitivity", 0.0, 1.5, 0.5, 0.1)
    adjustment_cap = st.slider("Maximum market growth adjustment (pp)", 0.0, 10.0, 5.0, 0.5)
    lookback = st.select_slider("Market return lookback (observations)", [1, 3, 5, 10, 20], value=5)
    if st.button("Refresh now", use_container_width=True):
        st.session_state.market_refresh_nonce = time.time_ns()
        st.rerun()
    st.divider()
    st.header("Forecast controls")
    scenario = st.slider("Additional scenario adjustment", -10.0, 20.0, 0.0, 0.5, format="%+.1f%%")
    risk = st.selectbox("Risk", ["all", "low", "medium", "high"])
    status = st.selectbox("Status", ["all", "active", "review", "warning"])
    trend = st.selectbox("Trend", ["all", "up", "flat", "down"])
    search = st.text_input("Search segment or period")
    sort_by = st.selectbox(
        "Sort by",
        ["scenario_growth", "revenue", "profit", "confidence", "profit_margin", "churn"],
    )
    ascending = st.toggle("Ascending", value=False)
    if st.button("Reset segment fixtures", use_container_width=True):
        st.session_state.segments = default_segments()


@st.cache_data(ttl=3600, show_spinner=False)
def load_market_data(
    selected_symbols: tuple[str, ...], selected_period: str, interval_bucket: int, nonce: int
) -> tuple[pd.DataFrame, str | None]:
    """Fetch and briefly cache public daily market observations."""
    del interval_bucket, nonce
    try:
        return fetch_market_history(selected_symbols, selected_period), None
    except (MarketDataError, ValueError) as exc:
        return pd.DataFrame(), str(exc)


@st.fragment(run_every=timedelta(minutes=refresh_minutes) if auto_refresh else None)
def render_dashboard() -> None:
    """Refresh source data, derived signals, and market-linked forecast together."""
    bucket = int(time.time() // (refresh_minutes * 60))
    nonce = st.session_state.get("market_refresh_nonce", 0)
    with st.spinner("Fetching latest available market data and recalculating forecasts…"):
        history, error = load_market_data(tuple(symbols), period, bucket, nonce)

    market_tab, forecast_tab = st.tabs(["🌍 Live Market Intelligence", "📊 Market-linked Segment Forecast"])
    snapshot = market_snapshot(history)
    indicators = market_indicators(history)
    with market_tab:
        st.subheader("Market pulse")
        if error:
            st.warning(f"Live market data is unavailable: {error}")
        elif snapshot.empty:
            st.info("Select one or more instruments from the sidebar.")
        else:
            unavailable = history.attrs.get("unavailable", {})
            if unavailable:
                st.info("Some selected instruments were unavailable: " + ", ".join(unavailable))
            fetched_at = history.attrs.get("fetched_at", "unknown")
            st.caption(
                f"Yahoo Finance daily history · Retrieved {fetched_at} · Refresh every {refresh_minutes} minute(s) · "
                "Latest available close, not necessarily real-time."
            )
            cols = st.columns(min(len(snapshot), 4))
            for col, (_, row) in zip(cols, snapshot.iterrows(), strict=False):
                delta = None if pd.isna(row["change_pct"]) else f"{row['change_pct']:+.2f}%"
                col.metric(row["instrument"], f"{row['close']:,.2f}", delta)

            st.subheader("Live prices and rolling averages")
            chart = go.Figure()
            for _, group in indicators.groupby("symbol", sort=False):
                name = group.iloc[-1]["instrument"]
                chart.add_trace(go.Scatter(x=group["date"], y=group["close"], mode="lines", name=f"{name} close"))
                chart.add_trace(go.Scatter(x=group["date"], y=group["sma_20"], mode="lines", line={"dash": "dot"}, name=f"{name} 20-observation avg"))
            chart.update_layout(height=430, hovermode="x unified", margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(chart, use_container_width=True)

            latest = indicators.sort_values("date").groupby("symbol", sort=False).tail(1)
            fields = ["instrument", "symbol", "date", "close", "daily_return_pct", "sma_20", "sma_50", "volatility_annualized_pct", "drawdown_pct"]
            st.subheader("Recalculated indicators")
            st.dataframe(latest[fields], use_container_width=True, hide_index=True)
            st.subheader("Descriptive market observations")
            for note in market_risk_briefing(indicators):
                st.markdown(f"- {note}")

            left, right = st.columns(2)
            left.download_button(
                "Download market history CSV", history.to_csv(index=False).encode("utf-8"),
                file_name="market_history.csv", mime="text/csv",
            )
            briefing = market_briefing_markdown(snapshot, fetched_at)
            briefing += "\n\n## Descriptive Indicators\n\n" + "\n".join(
                f"- {note}" for note in market_risk_briefing(indicators)
            )
            right.download_button(
                "Download market briefing", briefing.encode("utf-8"),
                file_name="market_briefing.md", mime="text/markdown",
            )
        st.caption(
            "Market data source: Yahoo Finance chart endpoint. For commercial use, replace with a provider and plan "
            "whose license grants your intended display and derived-data rights. No personalized financial advice."
        )

    with forecast_tab:
        st.markdown(
            '<div class="hero"><h2>Live-market-linked scenario forecast</h2><p>Each fixture segment’s baseline growth is adjusted using a configurable, capped move in its illustrative market proxy. This is a scenario experiment, not a measured sector beta or a prediction of company performance.</p></div>',
            unsafe_allow_html=True,
        )
        segments = st.session_state.get("segments", default_segments())
        forecast = market_linked_forecast(
            segments, history, scenario=scenario, sensitivity=sensitivity,
            max_adjustment=adjustment_cap, lookback=lookback,
        )
        filtered = filter_forecast(
            forecast, risk=risk, status=status, trend=trend, search=search,
            sort_by=sort_by, ascending=ascending,
        )
        summary = executive_summary(filtered)
        cols = st.columns(5)
        cols[0].metric("Fixture revenue", f"{summary['total_revenue']:,.1f}")
        cols[1].metric("Fixture profit", f"{summary['total_profit']:,.1f}")
        cols[2].metric("Avg adjusted growth", f"{summary['avg_growth']:.1f}%")
        cols[3].metric("Avg confidence", f"{summary['avg_confidence']}%")
        cols[4].metric("High risk", summary["high_risk_count"])
        st.caption(
            f"Formula: baseline growth + user scenario ({scenario:+.1f} pp) + clip({lookback}-observation proxy return × "
            f"{sensitivity:.1f}, ±{adjustment_cap:.1f} pp). Proxy mappings are illustrative, editable in code, and do not imply causal sector relationships."
        )

        overview, table, advisory, report_tab = st.tabs(["Overview", "Forecast table", "Advisory", "Report"])
        with overview:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Revenue and profit (fixtures)")
                st.plotly_chart(revenue_profit_chart(filtered), use_container_width=True)
            with c2:
                st.subheader("Revenue mix (fixtures)")
                st.plotly_chart(revenue_mix_chart(filtered), use_container_width=True)
            c3, c4 = st.columns(2)
            with c3:
                st.subheader("Market-adjusted growth trajectory")
                st.plotly_chart(growth_trend_chart(filtered), use_container_width=True)
            with c4:
                st.subheader("Risk distribution")
                st.plotly_chart(risk_distribution(filtered), use_container_width=True)
            st.subheader("Segment health radar")
            st.plotly_chart(health_radar_chart(filtered), use_container_width=True)
        with table:
            display = {
                "segment": "Segment", "market_proxy": "Market proxy", "proxy_return_pct": "Proxy return %",
                "market_adjustment_pp": "Market adjustment (pp)", "period": "Period", "revenue": "Fixture revenue",
                "costs": "Fixture costs", "profit": "Fixture profit", "scenario_growth": "Adjusted growth %",
                "profit_margin": "Fixture margin %", "confidence": "Fixture confidence", "risk": "Fixture risk",
                "status": "Status", "trend": "Adjusted trend", "market_share": "Fixture market share",
                "cac": "Fixture CAC", "churn": "Fixture churn", "competitors": "Fixture competitors",
            }
            st.dataframe(filtered[list(display)].rename(columns=display), use_container_width=True, hide_index=True)
            st.download_button("Download market-linked forecast CSV", export_csv(filtered), file_name="market_linked_segment_forecast.csv", mime="text/csv")
        with advisory:
            st.subheader("Explainable fixture advisory")
            st.dataframe(advisory_dataframe(filtered), use_container_width=True, hide_index=True)
            st.caption("The existing advisory rules apply to static fixture fundamentals, not to personalized investment decisions.")
        with report_tab:
            report = build_markdown_report(filtered, scenario=scenario)
            report += "\n\n" + market_briefing_markdown(snapshot, history.attrs.get("fetched_at"))
            st.markdown(report)
            st.download_button("Download combined executive report", report.encode("utf-8"), file_name="market_linked_executive_report.md", mime="text/markdown")
        st.caption("Live prices recalculate the market-scenario overlay and growth charts. Fixture revenue, costs, margin, churn, and confidence are not updated by market prices.")


st.title("🌐 Live Data Intelligence & Segment Forecasting")
st.caption("Live market context with automatically recalculated, bounded segment scenarios")
render_dashboard()
st.divider()
st.caption("Auto-refresh runs while this Streamlit browser session is active. The current feed is not NxCore; integrating NxCore requires a supported licensed adapter and feed host.")
