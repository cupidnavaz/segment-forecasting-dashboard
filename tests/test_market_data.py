from __future__ import annotations

import pandas as pd
import pytest

from segment_forecasting_dashboard.market_data import (
    MarketDataError,
    market_briefing_markdown,
    market_snapshot,
    parse_chart_response,
)


def _payload(closes: list[float | None]) -> dict:
    return {
        "chart": {
            "result": [
                {
                    "timestamp": [1735689600 + index * 86400 for index in range(len(closes))],
                    "indicators": {"quote": [{"close": closes, "volume": [100] * len(closes)}]},
                }
            ],
            "error": None,
        }
    }


def test_parse_chart_response_normalizes_market_observations():
    frame = parse_chart_response(_payload([100.0, None, 102.0]), "^GSPC")

    assert list(frame.columns) == ["symbol", "instrument", "date", "close", "volume"]
    assert len(frame) == 2
    assert frame.iloc[0]["instrument"] == "S&P 500"
    assert frame.iloc[-1]["close"] == 102.0
    assert str(frame["date"].dtype) == "datetime64[ns, UTC]"


def test_parse_chart_response_raises_on_empty_vendor_result():
    with pytest.raises(MarketDataError, match="No data returned"):
        parse_chart_response({"chart": {"result": None, "error": None}}, "^GSPC")


def test_market_snapshot_calculates_change_from_prior_observation():
    frame = parse_chart_response(_payload([100.0, 105.0]), "^GSPC")

    snapshot = market_snapshot(frame)

    assert len(snapshot) == 1
    assert snapshot.iloc[0]["close"] == 105.0
    assert snapshot.iloc[0]["change_pct"] == pytest.approx(5.0)


def test_market_snapshot_handles_single_observation():
    frame = parse_chart_response(_payload([100.0]), "^GSPC")

    snapshot = market_snapshot(frame)

    assert pd.isna(snapshot.iloc[0]["change_pct"])


def test_briefing_includes_market_source_and_latest_change():
    frame = parse_chart_response(_payload([100.0, 101.0]), "^GSPC")

    report = market_briefing_markdown(market_snapshot(frame), "2025-01-02T00:00:00+00:00")

    assert "Yahoo Finance" in report
    assert "S&P 500 (^GSPC)" in report
    assert "+1.00%" in report


def test_briefing_explains_missing_market_observations():
    report = market_briefing_markdown(pd.DataFrame())

    assert "No live market observations" in report
