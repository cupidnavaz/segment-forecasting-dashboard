"""Forecast calculation engine.

The formulas are intentionally kept equivalent to the original dashboard source.
They are deterministic and therefore straightforward to test and audit.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd


def calculate_metrics(row: dict) -> dict:
    """Calculate profitability, growth, risk, confidence, and trend."""
    revenue = float(row["revenue"])
    costs = float(row["costs"])
    profit = revenue - costs
    profit_margin = (profit / revenue) * 100 if revenue else 0.0

    growth = (
        (profit_margin * 0.8)
        + (float(row["market_share"]) * 0.3)
        + (float(row["units_sold"]) / 15)
        - (float(row["churn"]) * 0.6)
    )
    growth = round(growth, 1)

    if row.get("risk_override"):
        risk = row["risk_override"]
    elif profit_margin < 12 or row["churn"] > 18 or row["competitors"] > 5:
        risk = "high"
    elif profit_margin > 25 and row["churn"] < 8 and row["competitors"] < 3:
        risk = "low"
    else:
        risk = "medium"

    confidence = 60 + (revenue / 40) + (float(row["units_sold"]) / 10) - (float(row["churn"]) * 1.5)
    confidence = max(55, min(98, round(confidence)))

    trend = "up" if growth > 10 else "down" if growth < 0 else "flat"

    return {
        "growth": growth,
        "risk": risk,
        "confidence": confidence,
        "trend": trend,
        "profit": profit,
        "profit_margin": round(profit_margin, 2),
    }


def forecast_dataframe(segments: Iterable[dict], scenario: float = 0.0) -> pd.DataFrame:
    """Build the calculated forecast table."""
    rows = []
    for index, source in enumerate(segments):
        row = {**source, **calculate_metrics(source), "_index": index}
        row["scenario_growth"] = round(row["growth"] + scenario, 1)
        rows.append(row)
    return pd.DataFrame(rows)


def filter_forecast(
    frame: pd.DataFrame,
    *,
    risk: str = "all",
    status: str = "all",
    trend: str = "all",
    search: str = "",
    sort_by: str | None = None,
    ascending: bool = True,
) -> pd.DataFrame:
    """Apply dashboard filters and sorting."""
    result = frame.copy()
    if risk != "all":
        result = result[result["risk"] == risk]
    if status != "all":
        result = result[result["status"] == status]
    if trend != "all":
        result = result[result["trend"] == trend]
    if search.strip():
        query = search.strip().lower()
        result = result[
            result["segment"].str.lower().str.contains(query, regex=False)
            | result["period"].str.lower().str.contains(query, regex=False)
        ]
    if sort_by and sort_by in result.columns:
        result = result.sort_values(sort_by, ascending=ascending, kind="stable")
    return result.reset_index(drop=True)


def executive_summary(frame: pd.DataFrame) -> dict:
    """Return high-level KPIs and the strongest/weakest segments."""
    if frame.empty:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "avg_growth": 0.0,
            "avg_confidence": 0,
            "best_segment": None,
            "worst_segment": None,
            "high_risk_count": 0,
        }

    best = frame.loc[frame["scenario_growth"].idxmax()]
    worst = frame.loc[frame["scenario_growth"].idxmin()]
    return {
        "total_revenue": float(frame["revenue"].sum()),
        "total_profit": float(frame["profit"].sum()),
        "avg_growth": float(frame["scenario_growth"].mean()),
        "avg_confidence": int(round(frame["confidence"].mean())),
        "best_segment": str(best["segment"]),
        "worst_segment": str(worst["segment"]),
        "high_risk_count": int((frame["risk"] == "high").sum()),
    }
