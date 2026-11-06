"""Streamlit dashboard for live market intelligence and segment scenarios."""

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from segment_forecasting_dashboard.analytics import advisory_dataframe
from segment_forecasting_dashboard.charts import (
    growth_trend_chart,
    health_radar_chart,
    instrument_history_chart,
    market_comparison_chart,
    market_risk_chart,
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
from segment_forecasting_dashboard.market_forecasting import market_linked_forecast
from segment_forecasting_dashboard.reporting import build_markdown_report, export_csv

st.set_page_config(
    page_title="Market Intelligence | Segment Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

styles = Path(__file__).with_name("styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)


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


def _format_number(value: object, *, decimals: int = 2) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):,.{decimals}f}"


def _chart_motion(figure):
    if not st.session_state.get("animate_chart_transitions", True):
        figure.update_layout(transition={"duration": 0})
    return figure


def _render_market_overview(
    history: pd.DataFrame,
    indicators: pd.DataFrame,
    snapshot: pd.DataFrame,
    error: str | None,
    symbols: tuple[str, ...],
    period: str,
    refresh_minutes: int,
) -> None:
    st.title("Market overview")
    fetched_at = history.attrs.get("fetched_at")
    if fetched_at:
        retrieved = pd.to_datetime(fetched_at, utc=True).strftime("%b %d, %Y · %H:%M UTC")
        st.caption(
            f"Yahoo Finance daily history · Retrieved {retrieved} · "
            f"Refresh cadence {refresh_minutes} min · Latest close, not necessarily real-time"
        )
    else:
        st.caption("Live market context, with the source and freshness kept in view.")

    if error:
        st.warning(f"Live market data is unavailable: {error}. Use “Refresh data” to try again.")
    if history.attrs.get("unavailable"):
        unavailable = ", ".join(history.attrs["unavailable"])
        st.info(f"Some selected instruments were unavailable: {unavailable}")

    if snapshot.empty:
        if not error:
            st.info("Select one or more instruments in the sidebar to load market history.")
        return

    st.subheader("Market pulse")
    metric_columns = st.columns(min(len(snapshot), 4))
    for column, (_, row) in zip(metric_columns, snapshot.head(4).iterrows(), strict=False):
        delta = None if pd.isna(row["change_pct"]) else f"{row['change_pct']:+.2f}%"
        with column.container(border=True):
            st.metric(
                str(row["instrument"]),
                _format_number(row["close"]),
                delta,
                help=(
                    "Latest available daily close. Market data may be delayed "
                    "and is not a real-time quote."
                ),
            )
    if len(snapshot) > 4:
        st.caption(f"{len(snapshot)} instruments selected; remaining readings are in the table.")

    st.subheader("Price history")
    chart_mode, chart_options = st.columns([1.2, 1.8])
    with chart_mode:
        comparison = st.radio(
            "Chart view",
            ["Indexed comparison", "Price and averages"],
            horizontal=True,
            key="market_chart_view",
        )
    chart_frame = indicators
    if comparison == "Price and averages":
        available = [symbol for symbol in symbols if symbol in set(indicators["symbol"])]
        if not available:
            st.info("No selected instruments have usable observations for this view.")
            return
        with chart_options:
            focused_symbol = st.selectbox(
                "Instrument",
                available,
                format_func=lambda symbol: f"{WATCHLIST[symbol]} ({symbol})",
                key="focused_instrument",
            )
        chart_frame = indicators[indicators["symbol"] == focused_symbol]
        show_averages = st.toggle(
            "Show 20- and 50-observation averages", value=True, key="show_market_averages"
        )
        figure = instrument_history_chart(chart_frame, show_averages=show_averages)
    else:
        with chart_options:
            st.caption("Each series starts at 100 to compare change across different price scales.")
        figure = market_comparison_chart(indicators)

    with st.container(border=True):
        st.plotly_chart(
            _chart_motion(figure),
            use_container_width=True,
            config={"displaylogo": False, "scrollZoom": True, "displayModeBar": True},
            key=f"market-chart-{comparison}",
        )
    if comparison == "Indexed comparison":
        chart_caption = (
            f"History window: {period} · Hover or focus to trace a date across series. "
            "Indexed values compare relative change, not absolute prices."
        )
    else:
        chart_caption = (
            f"History window: {period} · Solid line: daily close. "
            "Dotted lines: descriptive rolling averages."
        )
    st.caption(chart_caption)

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Historical risk profile")
        with st.container(border=True):
            st.plotly_chart(
                _chart_motion(market_risk_chart(indicators)),
                use_container_width=True,
                config={"displaylogo": False},
                key="market-risk-profile",
            )
            st.caption(
                "Volatility is annualized; drawdown is relative to the selected window high."
            )
    with right:
        st.subheader("Latest indicator readings")
        latest = indicators.sort_values("date").groupby("symbol", sort=False).tail(1)
        fields = [
            "instrument",
            "date",
            "close",
            "daily_return_pct",
            "sma_20",
            "sma_50",
            "volatility_annualized_pct",
            "drawdown_pct",
        ]
        display = latest[fields].rename(
            columns={
                "instrument": "Instrument",
                "date": "Observation",
                "close": "Close",
                "daily_return_pct": "Daily change %",
                "sma_20": "20-observation avg",
                "sma_50": "50-observation avg",
                "volatility_annualized_pct": "Historical volatility %",
                "drawdown_pct": "Window drawdown %",
            }
        )
        with st.container(border=True):
            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
                height=min(450, 42 + 36 * len(display)),
                column_config={
                    "Close": st.column_config.NumberColumn(format="%.2f"),
                    "Daily change %": st.column_config.NumberColumn(format="%.2f%%"),
                    "20-observation avg": st.column_config.NumberColumn(format="%.2f"),
                    "50-observation avg": st.column_config.NumberColumn(format="%.2f"),
                    "Historical volatility %": st.column_config.NumberColumn(format="%.2f%%"),
                    "Window drawdown %": st.column_config.NumberColumn(format="%.2f%%"),
                },
            )

    st.subheader("Descriptive observations")
    notes = market_risk_briefing(indicators)
    st.markdown("\n".join(f"- {note}" for note in notes))
    download_col, _ = st.columns([1, 2])
    download_col.download_button(
        "Download market history CSV",
        history.to_csv(index=False).encode("utf-8"),
        file_name="market_history.csv",
        mime="text/csv",
    )
    st.markdown(
        '<div class="atlas-source">Source: Yahoo Finance chart endpoint. '
        "Daily history is not guaranteed real-time. "
        "Indicators describe selected observations; they are not predictions or trade signals. "
        "This dashboard does not provide personalized financial advice.</div>",
        unsafe_allow_html=True,
    )


def _render_instrument_analysis(
    indicators: pd.DataFrame,
    snapshot: pd.DataFrame,
    symbols: tuple[str, ...],
    period: str,
) -> None:
    st.title("Instrument analysis")
    available = [symbol for symbol in symbols if symbol in set(indicators["symbol"])]
    if not available:
        st.info("Choose an instrument in the sidebar with available history.")
        return

    symbol = st.selectbox(
        "Instrument",
        available,
        format_func=lambda value: f"{WATCHLIST[value]} ({value})",
        key="analysis_instrument",
    )
    selected = indicators[indicators["symbol"] == symbol]
    latest = snapshot[snapshot["symbol"] == symbol]
    if selected.empty or latest.empty:
        st.info(f"No observations are available for {WATCHLIST[symbol]}.")
        return

    row = latest.iloc[0]
    observation_date = pd.to_datetime(row["date"]).strftime("%b %d, %Y")
    st.caption(
        f"Daily close history · {period} · Latest observation {observation_date} · "
        "not a real-time quote"
    )
    metric_columns = st.columns(4)
    with metric_columns[0].container(border=True):
        st.metric("Latest close", _format_number(row["close"]))
    with metric_columns[1].container(border=True):
        st.metric(
            "Daily change",
            "—" if pd.isna(row["change_pct"]) else f"{row['change_pct']:+.2f}%",
        )
    with metric_columns[2].container(border=True):
        st.metric("20-observation average", _format_number(selected.iloc[-1]["sma_20"]))
    with metric_columns[3].container(border=True):
        st.metric(
            "Window drawdown",
            "—"
            if pd.isna(selected.iloc[-1]["drawdown_pct"])
            else f"{selected.iloc[-1]['drawdown_pct']:.2f}%",
        )

    show_averages = st.toggle("Show rolling averages", value=True, key="analysis_averages")
    with st.container(border=True):
        st.plotly_chart(
            _chart_motion(instrument_history_chart(selected, show_averages=show_averages)),
            use_container_width=True,
            config={"displaylogo": False, "scrollZoom": True, "displayModeBar": True},
            key="instrument-history",
        )
    st.subheader("Observation history")
    fields = [
        "date",
        "close",
        "daily_return_pct",
        "sma_20",
        "sma_50",
        "volatility_annualized_pct",
        "drawdown_pct",
    ]
    display = (
        selected[fields]
        .sort_values("date", ascending=False)
        .rename(
            columns={
                "date": "Observation",
                "close": "Daily close",
                "daily_return_pct": "Daily change %",
                "sma_20": "20-observation avg",
                "sma_50": "50-observation avg",
                "volatility_annualized_pct": "Historical volatility %",
                "drawdown_pct": "Window drawdown %",
            }
        )
    )
    st.dataframe(display, use_container_width=True, hide_index=True, height=440)
    st.download_button(
        "Download instrument history CSV",
        selected.to_csv(index=False).encode("utf-8"),
        file_name=f"{symbol.replace('^', '').replace('=', '-')}_history.csv",
        mime="text/csv",
    )


def _render_segment_scenarios(
    filtered: pd.DataFrame,
    scenario: float,
    sensitivity: float,
    adjustment_cap: float,
    lookback: int,
) -> None:
    st.title("Segment scenarios")
    st.markdown(
        '<div class="atlas-callout">'
        "<strong>Illustrative scenario, not a company forecast.</strong> "
        "Segment economics are static demo fixtures. A bounded proxy adjustment changes "
        "scenario growth only; "
        "it does not update fixture fundamentals or imply a causal relationship.</div>",
        unsafe_allow_html=True,
    )
    if filtered.empty:
        st.info("No segments match these filters. Adjust the sidebar filters to restore the table.")
        return

    summary = executive_summary(filtered)
    metric_columns = st.columns(5)
    for column, label, value in zip(
        metric_columns,
        [
            "Fixture revenue",
            "Fixture profit",
            "Adjusted scenario growth",
            "Fixture confidence",
            "High-risk fixtures",
        ],
        [
            f"{summary['total_revenue']:,.1f}",
            f"{summary['total_profit']:,.1f}",
            f"{summary['avg_growth']:.1f}%",
            f"{summary['avg_confidence']}%",
            str(summary["high_risk_count"]),
        ],
        strict=True,
    ):
        with column.container(border=True):
            st.metric(label, value)
    st.caption(
        f"Scenario: {scenario:+.1f} pp · Proxy lookback: {lookback} observations · "
        f"Sensitivity: {sensitivity:.1f} · Adjustment capped at ±{adjustment_cap:.1f} pp. "
        "Proxy assignments are illustrative."
    )

    overview, table, advisory = st.tabs(["Overview", "Forecast table", "Advisory"])
    with overview:
        first, second = st.columns(2)
        with first:
            st.subheader("Revenue and profit")
            with st.container(border=True):
                st.plotly_chart(
                    _chart_motion(revenue_profit_chart(filtered)),
                    use_container_width=True,
                    config={"displaylogo": False},
                )
        with second:
            st.subheader("Revenue mix")
            with st.container(border=True):
                st.plotly_chart(
                    _chart_motion(revenue_mix_chart(filtered)),
                    use_container_width=True,
                    config={"displaylogo": False},
                )
        third, fourth = st.columns(2)
        with third:
            st.subheader("Market-adjusted growth trajectory")
            with st.container(border=True):
                st.plotly_chart(
                    _chart_motion(growth_trend_chart(filtered)),
                    use_container_width=True,
                    config={"displaylogo": False},
                )
        with fourth:
            st.subheader("Fixture risk distribution")
            with st.container(border=True):
                st.plotly_chart(
                    _chart_motion(risk_distribution(filtered)),
                    use_container_width=True,
                    config={"displaylogo": False},
                )
        st.subheader("Segment health comparison")
        with st.container(border=True):
            st.plotly_chart(
                _chart_motion(health_radar_chart(filtered)),
                use_container_width=True,
                config={"displaylogo": False},
            )

    with table:
        display_columns = {
            "segment": "Segment",
            "market_proxy": "Illustrative market proxy",
            "proxy_return_pct": "Proxy return %",
            "market_adjustment_pp": "Market adjustment pp",
            "period": "Period",
            "revenue": "Fixture revenue",
            "costs": "Fixture costs",
            "profit": "Fixture profit",
            "scenario_growth": "Adjusted growth %",
            "profit_margin": "Fixture margin %",
            "confidence": "Fixture confidence",
            "risk": "Fixture risk",
            "status": "Status",
            "trend": "Adjusted trend",
            "market_share": "Fixture market share",
            "cac": "Fixture CAC",
            "churn": "Fixture churn",
            "competitors": "Fixture competitors",
        }
        table_frame = filtered[list(display_columns)].rename(columns=display_columns)
        st.dataframe(table_frame, use_container_width=True, hide_index=True, height=480)
        st.download_button(
            "Download market-linked forecast CSV",
            export_csv(filtered),
            file_name="market_linked_segment_forecast.csv",
            mime="text/csv",
        )

    with advisory:
        st.subheader("Explainable fixture advisory")
        st.dataframe(advisory_dataframe(filtered), use_container_width=True, hide_index=True)
        st.caption(
            "Advisory rules apply to fixture fundamentals, not personalized investment decisions."
        )


def _render_reports(
    filtered: pd.DataFrame,
    scenario: float,
    snapshot: pd.DataFrame,
    history: pd.DataFrame,
) -> None:
    st.title("Reports and exports")
    report = build_markdown_report(filtered, scenario=scenario)
    report += "\n\n" + market_briefing_markdown(snapshot, history.attrs.get("fetched_at"))
    st.download_button(
        "Download combined executive report",
        report.encode("utf-8"),
        file_name="market_linked_executive_report.md",
        mime="text/markdown",
    )
    st.download_button(
        "Download filtered segment forecast CSV",
        export_csv(filtered),
        file_name="market_linked_segment_forecast.csv",
        mime="text/csv",
    )
    st.markdown("---")
    st.markdown(report)


with st.sidebar:
    st.markdown(
        '<div class="atlas-brand">Segment Forecasting<span>Market intelligence</span></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    view = st.radio(
        "Workspace",
        ["Market overview", "Instrument analysis", "Segment scenarios", "Reports"],
        label_visibility="collapsed",
        key="active_view",
    )
    st.divider()
    st.subheader("Market feed")
    symbols = st.multiselect(
        "Instruments",
        options=list(WATCHLIST),
        default=["^GSPC", "^IXIC", "CL=F", "GC=F"],
        format_func=lambda symbol: f"{WATCHLIST[symbol]} ({symbol})",
        key="market_symbols",
    )
    period = st.selectbox("History window", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    auto_refresh = st.toggle("Auto-refresh", value=True)
    refresh_minutes = st.select_slider("Refresh interval", [1, 5, 15, 30], value=5)
    st.toggle("Animate chart transitions", value=True, key="animate_chart_transitions")

    if st.button("Refresh data", use_container_width=True):
        st.session_state.market_refresh_nonce = time.time_ns()
        st.rerun()

    st.divider()
    with st.expander("Scenario controls", expanded=view in {"Segment scenarios", "Reports"}):
        st.subheader("Scenario controls")
        sensitivity = st.slider("Market-scenario sensitivity", 0.0, 1.5, 0.5, 0.1)
        adjustment_cap = st.slider("Maximum market adjustment (pp)", 0.0, 10.0, 5.0, 0.5)
        lookback = st.select_slider("Proxy return lookback", [1, 3, 5, 10, 20], value=5)
        scenario = st.slider(
            "Additional scenario adjustment", -10.0, 20.0, 0.0, 0.5, format="%+.1f pp"
        )
        risk = st.selectbox("Risk", ["all", "low", "medium", "high"])
        status = st.selectbox("Status", ["all", "active", "review", "warning"])
        trend = st.selectbox("Trend", ["all", "up", "flat", "down"])
        search = st.text_input("Search segment or period")
        sort_by = st.selectbox(
            "Sort by",
            ["scenario_growth", "revenue", "profit", "confidence", "profit_margin", "churn"],
        )
        ascending = st.toggle("Ascending sort", value=False)
        if st.button("Reset segment fixtures", use_container_width=True):
            st.session_state.segments = default_segments()


@st.fragment(run_every=timedelta(minutes=refresh_minutes) if auto_refresh else None)
def render_dashboard() -> None:
    """Refresh source data, derived signals, and market-linked scenarios together."""
    bucket = int(time.time() // (refresh_minutes * 60))
    nonce = st.session_state.get("market_refresh_nonce", 0)
    with st.spinner("Fetching the latest available market history…"):
        history, error = load_market_data(tuple(symbols), period, bucket, nonce)

    snapshot = market_snapshot(history)
    indicators = market_indicators(history)
    segments = st.session_state.get("segments", default_segments())
    forecast = market_linked_forecast(
        segments,
        history,
        scenario=scenario,
        sensitivity=sensitivity,
        max_adjustment=adjustment_cap,
        lookback=lookback,
    )
    filtered = filter_forecast(
        forecast,
        risk=risk,
        status=status,
        trend=trend,
        search=search,
        sort_by=sort_by,
        ascending=ascending,
    )

    if view == "Market overview":
        _render_market_overview(
            history, indicators, snapshot, error, tuple(symbols), period, refresh_minutes
        )
    elif view == "Instrument analysis":
        if error:
            st.warning(
                f"Live market data is unavailable: {error}. Use “Refresh data” to try again."
            )
        _render_instrument_analysis(indicators, snapshot, tuple(symbols), period)
    elif view == "Segment scenarios":
        _render_segment_scenarios(filtered, scenario, sensitivity, adjustment_cap, lookback)
    else:
        _render_reports(filtered, scenario, snapshot, history)

    st.markdown(
        '<div class="atlas-source">Auto-refresh works while this browser session is active. '
        "Market data may be delayed or incomplete; segment economics remain illustrative fixtures. "
        "No personalized financial, investment, tax, or legal advice.</div>",
        unsafe_allow_html=True,
    )


render_dashboard()
