"""Plotly chart builders for market intelligence and segment scenarios."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_COLORS = [
    "#9a4939",
    "#3d6c83",
    "#5f7656",
    "#d0a64f",
    "#7a6388",
    "#387c78",
    "#a36a39",
    "#455d77",
    "#b45c52",
]

_INK = "#263a50"
_MUTED = "#65717a"
_GRID = "#e3ddd1"
_PAPER = "#f8f5ed"


def _style_figure(
    fig: go.Figure, *, height: int = 360, show_legend: bool = True, animate: bool = True
) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "IBM Plex Sans, sans-serif", "color": _INK, "size": 12},
        colorway=CHART_COLORS,
        hovermode="x unified",
        hoverlabel={"bgcolor": _INK, "font": {"color": "#fff", "family": "IBM Plex Sans"}},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"color": _MUTED},
        },
        showlegend=show_legend,
        margin={"l": 8, "r": 14, "t": 28, "b": 10},
        transition={"duration": 320 if animate else 0, "easing": "cubic-in-out"},
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor=_GRID,
        tickfont={"color": _MUTED},
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikecolor="#7e8d92",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=_GRID,
        zeroline=False,
        tickfont={"color": _MUTED},
        title_font={"color": _MUTED},
    )
    return fig


def market_comparison_chart(indicators: pd.DataFrame, *, animate: bool = True) -> go.Figure:
    """Compare selected instruments from a shared 100-point starting value."""
    fig = go.Figure()
    if indicators.empty:
        return _style_figure(fig, animate=animate)

    ordered = indicators.sort_values("date")
    for index, (_, group) in enumerate(ordered.groupby("symbol", sort=False)):
        close = pd.to_numeric(group["close"], errors="coerce")
        first = close.dropna().iloc[0] if close.notna().any() else np.nan
        if not np.isfinite(first) or first == 0:
            continue
        indexed = close.div(first).mul(100)
        name = str(group.iloc[-1]["instrument"])
        fig.add_trace(
            go.Scatter(
                x=group["date"],
                y=indexed,
                mode="lines",
                name=name,
                line={"color": CHART_COLORS[index % len(CHART_COLORS)], "width": 2.5},
                customdata=close,
                hovertemplate=(
                    "%{fullData.name}<br>"
                    "Indexed close: %{y:.2f}<br>"
                    "Close: %{customdata:,.2f}<extra></extra>"
                ),
            )
        )
    fig.add_hline(y=100, line={"color": "#aeb7b2", "dash": "dot", "width": 1})
    _style_figure(fig, height=390, animate=animate)
    fig.update_layout(
        yaxis_title="Indexed close · first observation = 100",
        xaxis_title=None,
    )
    return fig


def instrument_history_chart(
    indicators: pd.DataFrame, *, show_averages: bool = True, animate: bool = True
) -> go.Figure:
    """Show one instrument's close with optional 20- and 50-observation averages."""
    fig = go.Figure()
    if indicators.empty:
        return _style_figure(fig, animate=animate)

    group = indicators.sort_values("date")
    name = str(group.iloc[-1]["instrument"])
    fig.add_trace(
        go.Scatter(
            x=group["date"],
            y=group["close"],
            mode="lines",
            name=f"{name} close",
            line={"color": CHART_COLORS[0], "width": 2.8},
            hovertemplate="%{x|%b %d, %Y}<br>Close: %{y:,.2f}<extra></extra>",
        )
    )
    if show_averages:
        for field, label, color in (
            ("sma_20", "20-observation average", CHART_COLORS[1]),
            ("sma_50", "50-observation average", CHART_COLORS[2]),
        ):
            fig.add_trace(
                go.Scatter(
                    x=group["date"],
                    y=group[field],
                    mode="lines",
                    name=label,
                    line={"color": color, "width": 1.7, "dash": "dot"},
                    hovertemplate=f"%{{x|%b %d, %Y}}<br>{label}: %{{y:,.2f}}<extra></extra>",
                )
            )
    _style_figure(fig, height=420, animate=animate)
    fig.update_layout(yaxis_title="Daily close", xaxis_title=None)
    return fig


def market_risk_chart(indicators: pd.DataFrame, *, animate: bool = True) -> go.Figure:
    """Compare latest historical volatility and window drawdown by instrument."""
    fig = go.Figure()
    if indicators.empty:
        return _style_figure(fig, animate=animate)

    latest = indicators.sort_values("date").groupby("symbol", sort=False).tail(1)
    fig.add_bar(
        x=latest["instrument"],
        y=latest["volatility_annualized_pct"],
        name="20-observation volatility",
        marker_color=CHART_COLORS[1],
        hovertemplate="%{x}<br>Historical volatility: %{y:.1f}%<extra></extra>",
    )
    fig.add_bar(
        x=latest["instrument"],
        y=latest["drawdown_pct"],
        name="Window drawdown",
        marker_color=CHART_COLORS[0],
        hovertemplate="%{x}<br>Drawdown: %{y:.1f}%<extra></extra>",
    )
    _style_figure(fig, height=320, animate=animate)
    fig.update_layout(
        barmode="group",
        yaxis_title="Percent",
        xaxis_title=None,
    )
    return fig


def revenue_profit_chart(frame: pd.DataFrame, *, animate: bool = True) -> go.Figure:
    data = frame.copy()
    fig = go.Figure()
    fig.add_bar(
        x=data["segment"],
        y=data["revenue"],
        name="Fixture revenue",
        marker_color=_INK,
        hovertemplate="%{x}<br>Fixture revenue: %{y:,.1f}<extra></extra>",
    )
    fig.add_bar(
        x=data["segment"],
        y=data["profit"],
        name="Fixture profit",
        marker_color=CHART_COLORS[0],
        hovertemplate="%{x}<br>Fixture profit: %{y:,.1f}<extra></extra>",
    )
    _style_figure(fig, height=360, animate=animate)
    fig.update_layout(
        barmode="group",
        xaxis={"tickangle": -25},
        yaxis_title="Illustrative units",
    )
    return fig


def revenue_mix_chart(frame: pd.DataFrame, *, animate: bool = True) -> go.Figure:
    fig = px.pie(
        frame,
        values="revenue",
        names="segment",
        hole=0.58,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="%{label}<br>Fixture revenue: %{value:,.1f}<br>%{percent}<extra></extra>",
        marker={"line": {"color": _PAPER, "width": 2}},
    )
    _style_figure(fig, height=360, show_legend=True, animate=animate)
    fig.update_layout(
        legend={"orientation": "v", "x": 1.02, "y": 0.5}, margin={"l": 5, "r": 80, "t": 24, "b": 8}
    )
    return fig


def health_radar_chart(frame: pd.DataFrame, *, animate: bool = True) -> go.Figure:
    if frame.empty:
        return _style_figure(go.Figure(), height=390, animate=animate)
    top = frame.nlargest(5, "scenario_growth")
    categories = ["Profit margin", "Market share", "Confidence", "Low churn", "Low competition"]
    fig = go.Figure()
    for index, (_, row) in enumerate(top.iterrows()):
        values = [
            min(100, max(0, row["profit_margin"] * 3)),
            min(100, row["market_share"] * 3),
            row["confidence"],
            max(0, 100 - row["churn"] * 4),
            max(0, 100 - row["competitors"] * 12),
        ]
        values += values[:1]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill="toself",
                opacity=0.55,
                name=row["segment"],
                line={"color": CHART_COLORS[index % len(CHART_COLORS)]},
            )
        )
    _style_figure(fig, height=390, animate=animate)
    fig.update_layout(
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {"gridcolor": _GRID, "range": [0, 100], "tickfont": {"color": _MUTED}},
            "angularaxis": {"gridcolor": _GRID, "tickfont": {"color": _MUTED}},
        }
    )
    return fig


def growth_trend_chart(frame: pd.DataFrame, *, animate: bool = True) -> go.Figure:
    if frame.empty:
        return _style_figure(go.Figure(), height=390, animate=animate)
    periods = ["2024", "2025", "2026", "2027", "2028", "2029", "2030"]
    fig = go.Figure()
    for index, (_, row) in enumerate(frame.iterrows()):
        base = float(row["revenue"])
        growth = float(row["scenario_growth"]) / 100
        values = [base * ((1 + growth) ** max(0, int(year) - 2024)) for year in periods]
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=np.round(values, 1),
                mode="lines+markers",
                name=row["segment"],
                line={"color": CHART_COLORS[index % len(CHART_COLORS)], "width": 2},
                marker={"size": 5},
            )
        )
    _style_figure(fig, height=390, animate=animate)
    fig.update_layout(yaxis_title="Illustrative revenue units", xaxis_title=None)
    return fig


def risk_distribution(frame: pd.DataFrame, *, animate: bool = True) -> go.Figure:
    counts = frame["risk"].value_counts().reindex(["low", "medium", "high"], fill_value=0)
    colors = ["#5f7656", "#d0a64f", "#9a4939"]
    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=colors,
            hovertemplate="%{x} risk<br>Segments: %{y}<extra></extra>",
        )
    )
    _style_figure(fig, height=320, show_legend=False, animate=animate)
    fig.update_layout(yaxis_title="Fixture segments", xaxis_title=None)
    return fig
