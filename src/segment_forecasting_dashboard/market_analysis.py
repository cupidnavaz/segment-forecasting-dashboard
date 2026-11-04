"""Derive descriptive, non-personalized indicators from public market history."""

from __future__ import annotations

import pandas as pd


def market_indicators(history: pd.DataFrame) -> pd.DataFrame:
    """Calculate transparent price, return, trend, volatility, and drawdown metrics.

    Volatility is the standard deviation of daily percentage returns annualized
    using sqrt(252). It is a historical description, not a forecast.
    """
    columns = [
        "symbol", "instrument", "date", "close", "daily_return_pct",
        "sma_20", "sma_50", "volatility_annualized_pct", "drawdown_pct",
    ]
    if history.empty:
        return pd.DataFrame(columns=columns)

    results: list[pd.DataFrame] = []
    for _, group in history.sort_values("date").groupby("symbol", sort=False):
        data = group.copy()
        close = pd.to_numeric(data["close"], errors="coerce")
        returns = close.pct_change()
        data["daily_return_pct"] = returns * 100
        data["sma_20"] = close.rolling(20, min_periods=1).mean()
        data["sma_50"] = close.rolling(50, min_periods=1).mean()
        data["volatility_annualized_pct"] = returns.rolling(20, min_periods=2).std() * (252**0.5) * 100
        data["drawdown_pct"] = (close / close.cummax() - 1) * 100
        results.append(data)
    return pd.concat(results, ignore_index=True).reindex(columns=columns)


def market_risk_briefing(indicators: pd.DataFrame) -> list[str]:
    """Create neutral, rule-based educational observations, not trade signals."""
    if indicators.empty:
        return ["No observations are available for descriptive analysis."]

    notes: list[str] = []
    for symbol, group in indicators.sort_values("date").groupby("symbol", sort=False):
        latest = group.iloc[-1]
        instrument = latest["instrument"]
        if pd.notna(latest["sma_20"]) and pd.notna(latest["sma_50"]):
            relation = "above" if latest["sma_20"] >= latest["sma_50"] else "below"
            notes.append(f"{instrument} ({symbol})'s 20-observation average is {relation} its 50-observation average.")
        if pd.notna(latest["volatility_annualized_pct"]):
            notes.append(
                f"{instrument} ({symbol})'s 20-observation historical volatility is "
                f"{latest['volatility_annualized_pct']:.1f}% annualized."
            )
        if pd.notna(latest["drawdown_pct"]):
            notes.append(
                f"{instrument} ({symbol}) is {abs(latest['drawdown_pct']):.1f}% below its "
                "highest close in the selected window."
            )
    return notes or ["More historical observations are needed to calculate indicators."]
