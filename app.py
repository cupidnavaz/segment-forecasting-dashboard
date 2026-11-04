"""Streamlit entry point for live market intelligence and segment forecasting."""

from __future__ import annotations

import pandas as pd
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
st.caption("Live public market context paired with explainable segment scenarios and executive reporting")

with st.sidebar:
    st.header("Live market data")
    market_symbols = st.multiselect(
        "Instruments",
        options=list(WATCHLIST),
        default=["^GSPC", "^IXIC", "CL=F", "GC=F"],
        format_func=lambda symbol: f"{WATCHLIST[symbol]} ({symbol})",
    )
    market_period = st.selectbox("History window", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    refresh_market = st.button("Refresh live data", use_container_width=True)
    if refresh_market:
        st.cache_data.clear()
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


@st.cache_data(ttl=900, show_spinner=False)
def load_market_data(symbols: tuple[str, ...], period: str) -> tuple[pd.DataFrame, str | None]:
    """Cache live vendor responses briefly to keep reruns responsive."""
    try:
        return fetch_market_history(symbols, period), None
    except MarketDataError as exc:
        return pd.DataFrame(), str(exc)


with st.spinner("Loading public market data…"):
    history, market_error = load_market_data(tuple(market_symbols), market_period)
snapshot = market_snapshot(history)

market_tab, segment_tab = st.tabs(["🌍 Live Market Intelligence", "📊 Segment Forecasting"])

with market_tab:
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
            "15-minute cache · Latest available market close, which may not be real-time."
        )
        metric_columns = st.columns(min(len(snapshot), 4))
        for column, (_, row) in zip(metric_columns, snapshot.iterrows(), strict=False):
            change = None if pd.isna(row["change_pct"]) else f"{row['change_pct']:+.2f}%"
            column.metric(
                row["instrument"],
                f"{row['close']:,.2f}",
                change,
                delta_color="normal",
            )

        left, right = st.columns([1.7, 1])
        with left:
            st.subheader("Price history")
            st.plotly_chart(
                px.line(
                    history,
                    x="date",
                    y="close",
                    color="instrument",
                    labels={"date": "Date", "close": "Close", "instrument": "Instrument"},
                    template="plotly_dark",
                ).update_layout(height=430, margin=dict(l=10, r=10, t=25, b=10)),
                use_container_width=True,
            )
        with right:
            st.subheader("Latest market observations")
            display_snapshot = snapshot[["instrument", "symbol", "date", "close", "change_pct"]].copy()
            display_snapshot["date"] = display_snapshot["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(display_snapshot, use_container_width=True, hide_index=True)
            st.download_button(
                "Download market snapshot CSV",
                display_snapshot.to_csv(index=False).encode("utf-8"),
                file_name="live_market_snapshot.csv",
                mime="text/csv",
            )

    st.caption(
        "Market feed: Yahoo Finance chart endpoint. Data availability and delay depend on the provider; "
        "this project is for analytics demonstration, not trading or investment advice."
    )

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
            "segment": "Segment",
            "period": "Period",
            "revenue": "Revenue",
            "costs": "Costs",
            "profit": "Profit",
            "scenario_growth": "Growth %",
            "profit_margin": "Margin %",
            "confidence": "Confidence",
            "risk": "Risk",
            "status": "Status",
            "trend": "Trend",
            "market_share": "Market Share",
            "cac": "CAC",
            "churn": "Churn",
            "competitors": "Competitors",
        }
        st.dataframe(
            filtered[list(display_columns)].rename(columns=display_columns),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download forecast CSV",
            export_csv(filtered),
            file_name="segment_forecast.csv",
            mime="text/csv",
        )

    with tab_advisory:
        advisory = advisory_dataframe(filtered)
        st.subheader("Explainable segment advisory")
        st.dataframe(advisory, use_container_width=True, hide_index=True)
        st.caption(
            "Advisory signals are deterministic rules derived from margin, growth, churn, competition, market share, and confidence."
        )

    with tab_report:
        report = build_markdown_report(filtered, scenario=scenario)
        report += "\n\n" + market_briefing_markdown(snapshot, history.attrs.get("fetched_at"))
        st.markdown(report)
        st.download_button(
            "Download executive report",
            report.encode("utf-8"),
            file_name="executive_intelligence_report.md",
            mime="text/markdown",
        )

st.divider()
st.caption(
    "Live market observations are fetched from Yahoo Finance and cached for 15 minutes. "
    "Segment economics remain static illustrative fixtures; neither dataset is financial advice."
)
