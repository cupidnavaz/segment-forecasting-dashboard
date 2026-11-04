"""Tests for the bounded live-market scenario overlay."""

import pandas as pd
import pytest

from segment_forecasting_dashboard.data import default_segments
from segment_forecasting_dashboard.forecasting import forecast_dataframe
from segment_forecasting_dashboard.market_forecasting import market_linked_forecast, proxy_returns


def _history(prices: list[float], symbol: str = "^GSPC") -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": symbol,
            "instrument": symbol,
            "date": pd.date_range("2025-01-01", periods=len(prices), tz="UTC"),
            "close": prices,
            "volume": 10,
        }
    )


def test_proxy_returns_uses_last_available_lookback_observations():
    assert proxy_returns(_history([100.0, 100.0, 110.0]), lookback=2)["^GSPC"] == pytest.approx(10.0)


def test_live_proxy_changes_growth_and_is_bounded():
    baseline = forecast_dataframe(default_segments())
    result = market_linked_forecast(
        default_segments(), _history([100.0, 110.0]), sensitivity=1.0, max_adjustment=2.0
    )

    retail = result.loc[result["segment"] == "Retail & E-Commerce"].iloc[0]
    assert retail["market_adjustment_pp"] == 2.0
    assert retail["scenario_growth"] == round(baseline.loc[0, "growth"] + 2.0, 1)
    assert retail["proxy_return_pct"] == pytest.approx(10.0)


def test_missing_proxy_data_leaves_base_forecast_unchanged():
    result = market_linked_forecast(default_segments(), _history([100.0, 105.0], "BTC-USD"))
    retail = result.loc[result["segment"] == "Retail & E-Commerce"].iloc[0]

    assert retail["market_adjustment_pp"] == 0.0
    assert pd.isna(retail["proxy_return_pct"])
    assert retail["scenario_growth"] == retail["growth"]


def test_manual_scenario_is_combined_with_market_adjustment():
    result = market_linked_forecast(
        default_segments(), _history([100.0, 102.0]), scenario=1.5, sensitivity=0.5
    )
    retail = result.loc[result["segment"] == "Retail & E-Commerce"].iloc[0]

    assert retail["scenario_growth"] == round(retail["growth"] + 1.0 + 1.5, 1)


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError, match="sensitivity"):
        market_linked_forecast(default_segments(), pd.DataFrame(), sensitivity=-1)
