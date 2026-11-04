"""Streamlit entry point for live market intelligence and segment forecasting."""

from __future__ import annotations

import time
from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
from segment_forecasting_dashboard.forecasting import (
    executive_summary,
    filter_forecast,
    forecast_dataframe,
)
from segment_forecasting_dashboard.market_analysis import market_indicators, market_risk_briefing
from segment_forecasting_dashboard.market_data import (
    WATCHLIST,
    MarketDataError,
    fetch_market_history,
    market_briefing_markdown,
    market_snapshot,
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

if "segments" not in st.session_state:
    st.session_state.segments = default_segments()

st.title("🌐 Live Data Intelligence & Segment Forecasting")
st.caption("Automatically refreshed public market data, transparent indicators, and explainable segment scenarios")

with st.sidebar:
    st.header("Live market data")
    market_symbols = st.multiselect(
        "Instruments",
        options=list(WATCHLIST),
        default=["^GSPC", "^IXIC", "CL=F", "GC=F"],
        format_func=lambda symbol: f"{WATCHLIST[symbol]} ({symbol})",
    )
    market_period = st.selectbox("History window", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    auto_refresh = st.toggle("Automatically refresh", value=True)
    refresh_minutes = st.select_slider("Refresh every", options=[1, 5, 15, 30], value=5, disabled=not auto_refresh)
    if st.button("Refresh now", use_container_width=True):
        st.session_state.market_refresh_nonce = time.time_ns()
        st.rerun()
    st.divider()
    st.header("Segment forecast")
    scenario = st.slider("Scenario growth adjustment", -10.0, 20.0, 0.0, 0.5, format="%+.1f%%")
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
        st.rerun()


@st.cache_data(ttl=3600, show_spinner=False)
def load_market_data(
    symbols: tuple[str, ...], period: str, refresh_bucket: int, refresh_nonce: int
) -> tuple[pd.DataFrame, str | None]:
    """Fetch one fresh vendor snapshot per selected refresh interval."""
    del refresh_bucket, refresh_nonce  # cache-key inputs intentionally trigger scheduled refreshes
    try:
        return fetch_market_history(symbols, period), None
    except (MarketDataError, ValueError) as exc:
        return pd.DataFrame(), str(exc)


@st.fragment(run_every=timedelta(minutes=refresh_minutes) if auto_refresh else None)
def live_market_panel() -> None:
    """Live fragment refreshes the data and all derived indicators on schedule."""
    refresh_seconds = refresh_minutes * 60
    refresh_bucket = int(time.time() // refresh_seconds)
    refresh_nonce = st.session_state.get("market_refresh_nonce", 0)
    with st.spinner("Loading public market data…"):
        history, market_error = load_market_data(
            tuple(market_symbols), market_period, refresh_bucket, refresh_nonce
        )
    snapshot = market_snapshot(history)
    indicators = market_indicators(history)

    st.subheader("Market pulse")
    if market_error:
        st.warning(f"Live market data could not be loaded: {market_error}")
    elif snapshot.empty:
        st.info("Select one or more instruments in the sidebar to load live market history.")
    else:
        unavailable = history.attrs.get("unavailable", {})
        if unavailable:
            st.info("Some selected instruments were unavailable: " + ", ".join(unavailable))
        fetched_at = history.attrs.get("fetched_at")
        st.caption(
            f"Daily observations from Yahoo Finance · Retrieved {fetched_at or 'just now'} · "
            f"Automatic refresh: every {refresh_minutes} minute(s) · Latest available close, not necessarily real-time."
        )
        metric_columns = st.columns(min(len(snapshot), 4))
        for column, (_, row) in zip(metric_columns, snapshot.iterrows(), strict=False):
            change = None if pd.isna(row["change_pct"]) else f"{row['change_pct']:+.2f}%"
            column.metric(row["instrument"], f"{row['close']:,.2f}", change)

        st.subheader("Price history and rolling averages")
        chart = go.Figure()
        for _, group in indicators.groupby("symbol", sort=False):
            instrument = group.iloc[-1]["instrument"]
            chart.add_trace(go.Scatter(x=group["date"], y=group["close"], mode="lines", name=f"{instrument} close"))
            chart.add_trace(go.Scatter(x=group["date"], y=group["sma_20"], mode="lines", line={"dash": "dot"}, name=f"{instrument} 20-day avg"))
        chart.update_layout(height=450, hovermode="x unified", margin=dict(l=10, r=10, t=25, b=10))
        st.plotly_chart(chart, use_container_width=True)

        st.subheader("Recalculated market indicators")
        latest_indicators = indicators.sort_values("date").groupby("symbol", sort=False).tail(1)
        indicator_columns = [
            "instrument", "symbol", "date", "close", "daily_return_pct", "sma_20",
            "sma_50", "volatility_annualized_pct", "drawdown_pct",
        ]
        st.dataframe(latest_indicators[indicator_columns], use_container_width=True, hide_index=True)
        st.caption("Volatility is historical, annualized realized volatility; moving averages and drawdowns describe the selected history window.")

        st.subheader("Neutral market observations")
        for note in market_risk_briefing(indicators):
            st.markdown(f"- {note}")

        export_left, export_right = st.columns(2)
        export_left.download_button(
            "Download market history CSV",
            history.to_csv(index=False).encode("utf-8"),
            file_name="market_history.csv",
            mime="text/csv",
        )
        briefing = market_briefing_markdown(snapshot, fetched_at)
        briefing += "\n\n## Descriptive Indicators\n\n" + "\n".join(
            f"- {note}" for note in market_risk_briefing(indicators)
        )
        export_right.download_button(
            "Download live market briefing",
            briefing.encode("utf-8"),
            file_name="live_market_briefing.md",
            mime="text/markdown",
        )

    st.caption(
        "Source: Yahoo Finance chart endpoint. Data availability, licensing, and delay depend on the provider. "
        "Indicators are educational and descriptive only; this app does not provide personalized financial advice or trade recommendations."
    )


market_tab, segment_tab = st.tabs(["🌍 Live Market Intelligence", "📊 Segment Forecasting"])
with market_tab:
    live_market_panel()

with segment_tab:
    st.markdown(
        '<div class="hero"><h2>Forecast command center</h2><p>Explore the provided segment fixtures with scenario controls, risk intelligence, and explainable reporting. These segment figures are illustrative, not live business data.</p></div>',
        unsafe_allow_html=True,
    )
    forecast = forecast_dataframe(st.session_state.segments, scenario=scenario)
    filtered = filter_forecast(
        forecast,
        risk=risk,
        status=status,
        trend=trend,
        search=search,
        sort_by=sort_by,
        ascending=ascending,
    )
    summary = executive_summary(filtered)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Fixture revenue", f"{summary['total_revenue']:,.1f}")
    m2.metric("Fixture profit", f"{summary['total_profit']:,.1f}")
    m3.metric("Avg Growth", f"{summary['avg_growth']:.1f}%")
    m4.metric("Avg Confidence", f"{summary['avg_confidence']}%")
    m5.metric("High Risk", summary["high_risk_count"])

    tab_overview, tab_forecast, tab_advisory, tab_report = st.tabs(
        ["Overview", "Forecast table", "Advisory", "Executive report"]
    )
    with tab_overview:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Revenue and profit")
            st.plotly_chart(revenue_profit_chart(filtered), use_container_width=True)
        with c2:
            st.subheader("Revenue mix")
            st.plotly_chart(revenue_mix_chart(filtered), use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Growth trajectory")
            st.plotly_chart(growth_trend_chart(filtered), use_container_width=True)
        with c4:
            st.subheader("Risk distribution")
            st.plotly_chart(risk_distribution(filtered), use_container_width=True)
        st.subheader("Segment health radar")
        st.plotly_chart(health_radar_chart(filtered), use_container_width=True)

    with tab_forecast:
        display_columns = {
            "segment": "Segment", "period": "Period", "revenue": "Revenue", "costs": "Costs",
            "profit": "Profit", "scenario_growth": "Growth %", "profit_margin": "Margin %",
            "confidence": "Confidence", "risk": "Risk", "status": "Status", "trend": "Trend",
            "market_share": "Market Share", "cac": "CAC", "churn": "Churn", "competitors": "Competitors",
        }
        st.dataframe(filtered[list(display_columns)].rename(columns=display_columns), use_container_width=True, hide_index=True)
        st.download_button("Download forecast CSV", export_csv(filtered), file_name="segment_forecast.csv", mime="text/csv")

    with tab_advisory:
        st.subheader("Explainable segment advisory")
        st.dataframe(advisory_dataframe(filtered), use_container_width=True, hide_index=True)
        st.caption("Rule-based signals on illustrative segment fixtures; not financial advice.")

    with tab_report:
        report = build_markdown_report(filtered, scenario=scenario)
        st.markdown(report)
        st.download_button(
            "Download segment forecast report", report.encode("utf-8"),
            file_name="segment_forecast_report.md", mime="text/markdown",
        )

st.divider()
st.caption("Market indicators refresh on the selected schedule while this app session remains open. Segment economics remain static illustrative fixtures.")
