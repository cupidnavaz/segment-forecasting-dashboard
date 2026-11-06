import pandas as pd
import pytest

from segment_forecasting_dashboard.charts import (
    instrument_history_chart,
    market_comparison_chart,
    market_risk_chart,
)
from segment_forecasting_dashboard.market_analysis import market_indicators


def _indicators() -> pd.DataFrame:
    history = pd.DataFrame(
        {
            "symbol": ["^GSPC", "^GSPC", "^GSPC", "GC=F", "GC=F", "GC=F"],
            "instrument": ["S&P 500"] * 3 + ["Gold"] * 3,
            "date": list(pd.date_range("2025-01-01", periods=3, tz="UTC")) * 2,
            "close": [100.0, 110.0, 105.0, 50.0, 55.0, 45.0],
        }
    )
    return market_indicators(history)


def test_market_comparison_indexes_each_instrument_to_100():
    chart = market_comparison_chart(_indicators())

    assert len(chart.data) == 2
    assert list(chart.data[0].y) == pytest.approx([100.0, 110.0, 105.0])
    assert list(chart.data[1].y) == pytest.approx([100.0, 110.0, 90.0])
    assert chart.layout.yaxis.title.text == "Indexed close · first observation = 100"


def test_instrument_history_can_toggle_rolling_averages_and_motion():
    indicators = _indicators()
    full_chart = instrument_history_chart(indicators[indicators["symbol"] == "^GSPC"])
    quiet_chart = instrument_history_chart(
        indicators[indicators["symbol"] == "^GSPC"],
        show_averages=False,
        animate=False,
    )

    assert len(full_chart.data) == 3
    assert len(quiet_chart.data) == 1
    assert quiet_chart.layout.transition.duration == 0


def test_market_risk_chart_compares_volatility_and_drawdown():
    chart = market_risk_chart(_indicators())

    assert len(chart.data) == 2
    assert chart.layout.barmode == "group"
    assert chart.data[1].name == "Window drawdown"


def test_market_charts_accept_empty_history():
    empty = market_indicators(pd.DataFrame())

    assert len(market_comparison_chart(empty).data) == 0
    assert len(instrument_history_chart(empty).data) == 0
    assert len(market_risk_chart(empty).data) == 0
