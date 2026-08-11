"""Executive report and CSV export helpers."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from .forecasting import executive_summary


def build_markdown_report(frame: pd.DataFrame, scenario: float = 0.0) -> str:
    """Build a concise, auditable executive forecast report."""
    summary = executive_summary(frame)
    scenario_line = f"Scenario adjustment: **{scenario:+.1f}%**" if scenario else "Scenario adjustment: **Base case**"

    lines = [
        "# Executive Forecast Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        scenario_line,
        "",
        "## Executive Summary",
        f"- Total revenue: **{summary['total_revenue']:,.1f}**",
        f"- Total profit: **{summary['total_profit']:,.1f}**",
        f"- Average growth: **{summary['avg_growth']:.1f}%**",
        f"- Average confidence: **{summary['avg_confidence']}%**",
        f"- High-risk segments: **{summary['high_risk_count']}**",
        f"- Strongest growth segment: **{summary['best_segment'] or 'N/A'}**",
        f"- Weakest growth segment: **{summary['worst_segment'] or 'N/A'}**",
        "",
        "## Forecast Table",
        "",
        "| Segment | Revenue | Profit | Growth | Confidence | Risk | Status |",
        "|---|---:|---:|---:|---:|---|---|",
    ]

    for _, row in frame.iterrows():
        lines.append(
            f"| {row['segment']} | {row['revenue']:,.1f} | {row['profit']:,.1f} | "
            f"{row['scenario_growth']:.1f}% | {row['confidence']}% | {row['risk']} | {row['status']} |"
        )

    return "\n".join(lines)


def export_csv(frame: pd.DataFrame) -> bytes:
    """Return a user-downloadable CSV representation."""
    columns = [
        "segment", "period", "revenue", "costs", "profit", "scenario_growth",
        "confidence", "risk", "status", "trend", "profit_margin",
    ]
    return frame[columns].to_csv(index=False).encode("utf-8")
