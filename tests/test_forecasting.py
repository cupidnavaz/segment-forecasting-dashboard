from segment_forecasting_dashboard.data import default_segments
from segment_forecasting_dashboard.forecasting import (
    calculate_metrics,
    executive_summary,
    filter_forecast,
    forecast_dataframe,
)


def test_metrics_match_expected_retail_values():
    row = default_segments()[0]
    result = calculate_metrics(row)
    assert result["profit"] == 130
    assert result["growth"] == 25.5
    assert result["risk"] == "medium"
    assert result["confidence"] == 71
    assert result["trend"] == "up"


def test_forecast_dataframe_contains_all_segments():
    frame = forecast_dataframe(default_segments())
    assert len(frame) == 9
    assert {"growth", "risk", "confidence", "trend", "profit", "scenario_growth"} <= set(frame.columns)


def test_filters_and_search():
    frame = forecast_dataframe(default_segments())
    result = filter_forecast(frame, status="active", search="saas")
    assert len(result) == 1
    assert result.iloc[0]["segment"] == "Tech & SaaS"


def test_executive_summary_empty():
    frame = forecast_dataframe(default_segments()).iloc[0:0]
    result = executive_summary(frame)
    assert result["total_revenue"] == 0
    assert result["best_segment"] is None
