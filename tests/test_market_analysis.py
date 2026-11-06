"""Tests for transparent descriptive market indicators."""

import pandas as pd
import pytest

from segment_forecasting_dashboard.market_analysis import market_indicators, market_risk_briefing


def _history(prices: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": "TEST",
            "instrument": "Test Instrument",
            "date": pd.date_range("2025-01-01", periods=len(prices), tz="UTC"),
            "close": prices,
            "volume": 100,
        }
    )


def test_indicators_recalculate_returns_averages_and_drawdown():
    indicators = market_indicators(_history([100.0, 110.0, 99.0]))

    assert indicators.iloc[1]["daily_return_pct"] == pytest.approx(10.0)
    assert indicators.iloc[-1]["sma_20"] == pytest.approx(103.0)
    assert indicators.iloc[-1]["drawdown_pct"] == pytest.approx(-10.0)


def test_volatility_requires_multiple_returns():
    indicators = market_indicators(_history([100.0, 101.0, 102.0]))

    assert pd.isna(indicators.iloc[0]["volatility_annualized_pct"])
    assert pd.notna(indicators.iloc[-1]["volatility_annualized_pct"])


def test_empty_history_returns_expected_columns():
    indicators = market_indicators(pd.DataFrame())

    assert "drawdown_pct" in indicators
    assert indicators.empty
    assert market_risk_briefing(indicators) == [
        "No observations are available for descriptive analysis."
    ]


def test_briefing_is_descriptive_and_never_issues_trade_instruction():
    notes = market_risk_briefing(market_indicators(_history([100.0, 103.0, 105.0])))

    assert any("historical volatility" in note for note in notes)
    assert all("buy" not in note.lower() and "sell" not in note.lower() for note in notes)
