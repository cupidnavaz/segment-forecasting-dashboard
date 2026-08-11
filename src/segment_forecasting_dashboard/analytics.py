"""Advisory analytics derived from the forecast engine."""

from __future__ import annotations

import pandas as pd


def analyze_segment(row: pd.Series) -> dict:
    """Generate explainable advisory signals for one segment."""
    margin = float(row["profit_margin"])
    growth = float(row["scenario_growth"])
    churn = float(row["churn"])
    confidence = int(row["confidence"])
    competitors = int(row["competitors"])
    market_share = float(row["market_share"])

    score = 50
    score += min(25, max(-25, (margin - 15) * 1.2))
    score += min(15, max(-15, growth))
    score -= min(20, churn)
    score -= max(0, competitors - 3) * 3
    health = max(0, min(100, round(score)))

    gaps = []
    actions = []

    if margin < 12:
        gaps.append(("critical", "Thin profit margin", "Review pricing and operating costs."))
        actions.append((1, "Margin recovery", "Prioritize cost reduction and pricing discipline."))
    if churn > 15:
        gaps.append(("critical", "Elevated churn", "Retention is materially weakening forecast quality."))
        actions.append((1, "Retention program", "Target churn drivers with segment-specific retention offers."))
    if competitors > 5:
        gaps.append(("warning", "Crowded market", "Competitive pressure may limit share expansion."))
        actions.append((2, "Differentiate", "Strengthen positioning, distribution, or product defensibility."))
    if market_share < 10:
        gaps.append(("warning", "Low market share", "The segment has room to expand but needs focused acquisition."))
        actions.append((2, "Share expansion", "Concentrate acquisition spend on high-conversion channels."))
    if growth > 15:
        gaps.append(("info", "Strong growth signal", "Current economics support an expansion case."))

    if not gaps:
        gaps.append(("info", "Balanced outlook", "No major structural warning was detected."))

    impact = "critical" if health < 45 else "warning" if health < 65 else "positive"

    return {
        "health_score": health,
        "impact_class": impact,
        "gaps": gaps,
        "actions": actions,
    }


def advisory_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    """Flatten advisory results for presentation."""
    records = []
    for _, row in frame.iterrows():
        analysis = analyze_segment(row)
        records.append(
            {
                "segment": row["segment"],
                "health_score": analysis["health_score"],
                "impact": analysis["impact_class"],
                "risk": row["risk"],
                "growth": row["scenario_growth"],
                "profit_margin": row["profit_margin"],
                "confidence": row["confidence"],
                "gaps": len([g for g in analysis["gaps"] if g[0] != "info"]),
                "priority_actions": len([a for a in analysis["actions"] if a[0] <= 2]),
            }
        )
    return pd.DataFrame(records)
