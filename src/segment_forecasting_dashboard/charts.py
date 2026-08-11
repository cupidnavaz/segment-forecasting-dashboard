"""Plotly chart builders for the Streamlit dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CHART_COLORS = [
    "#3b82f6", "#14b8a6", "#8b5cf6", "#f97316", "#ec4899",
    "#10b981", "#f59e0b", "#6366f1", "#ef4444",
]


def revenue_profit_chart(frame: pd.DataFrame) -> go.Figure:
    data = frame.copy()
    fig = go.Figure()
    fig.add_bar(x=data["segment"], y=data["revenue"], name="Revenue")
    fig.add_bar(x=data["segment"], y=data["profit"], name="Profit")
    fig.update_layout(barmode="group", height=380, margin=dict(l=10, r=10, t=35, b=80))
    return fig


def revenue_mix_chart(frame: pd.DataFrame) -> go.Figure:
    fig = px.pie(
        frame,
        values="revenue",
        names="segment",
        hole=0.55,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=35, b=10), showlegend=False)
    return fig


def health_radar_chart(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return go.Figure()
    top = frame.nlargest(5, "scenario_growth")
    categories = ["Profit Margin", "Market Share", "Confidence", "Low Churn", "Low Competition"]
    fig = go.Figure()
    for _, row in top.iterrows():
        values = [
            min(100, max(0, row["profit_margin"] * 3)),
            min(100, row["market_share"] * 3),
            row["confidence"],
            max(0, 100 - row["churn"] * 4),
            max(0, 100 - row["competitors"] * 12),
        ]
        values += values[:1]
        fig.add_trace(go.Scatterpolar(r=values, theta=categories + [categories[0]], fill="toself", name=row["segment"]))
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def growth_trend_chart(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return go.Figure()
    periods = ["2024", "2025", "2026", "2027", "2028", "2029", "2030"]
    fig = go.Figure()
    for i, (_, row) in enumerate(frame.iterrows()):
        base = float(row["revenue"])
        growth = float(row["scenario_growth"]) / 100
        values = [base * ((1 + growth) ** max(0, year - 2024)) for year in range(2024, 2031)]
        fig.add_trace(go.Scatter(x=periods, y=np.round(values, 1), mode="lines+markers", name=row["segment"]))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=35, b=40), hovermode="x unified")
    return fig


def risk_distribution(frame: pd.DataFrame) -> go.Figure:
    counts = frame["risk"].value_counts().reindex(["low", "medium", "high"], fill_value=0)
    fig = px.bar(x=counts.index, y=counts.values, labels={"x": "Risk", "y": "Segments"})
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=35, b=30))
    return fig
