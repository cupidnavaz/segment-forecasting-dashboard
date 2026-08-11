"""Streamlit entry point for the Segment Forecasting Dashboard."""

from __future__ import annotations

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
from segment_forecasting_dashboard.reporting import build_markdown_report, export_csv

st.set_page_config(
    page_title="CupidCreativeX Ventures | Segment Forecasting",
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

st.title("📊 Segment Forecasting Dashboard")
st.caption("CupidCreativeX Ventures • Forecasting, scenario analysis, risk intelligence, and executive reporting")

with st.sidebar:
    st.header("Controls")
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
    st.divider()
    if st.button("Reset dataset", use_container_width=True):
        st.session_state.segments = default_segments()
        st.rerun()

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

st.markdown(
    '<div class="hero"><h2>Forecast command center</h2><p>Turn segment economics into an explainable forecast instead of making executives stare at decorative charts and hope.</p></div>',
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Revenue", f"{summary['total_revenue']:,.1f}")
m2.metric("Profit", f"{summary['total_profit']:,.1f}")
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
    st.caption("Advisory signals are deterministic rules derived from margin, growth, churn, competition, market share, and confidence.")

with tab_report:
    report = build_markdown_report(filtered, scenario=scenario)
    st.markdown(report)
    st.download_button(
        "Download executive report",
        report.encode("utf-8"),
        file_name="executive_forecast_report.md",
        mime="text/markdown",
    )

st.divider()
st.caption("Source lineage: rebuilt from the supplied ultramodern.html dashboard. Market ticker values are static fixtures and are not live market data.")
