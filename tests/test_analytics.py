from segment_forecasting_dashboard.analytics import analyze_segment, advisory_dataframe
from segment_forecasting_dashboard.data import default_segments
from segment_forecasting_dashboard.forecasting import forecast_dataframe


def test_high_risk_health_signal():
    frame = forecast_dataframe(default_segments())
    healthcare = frame.loc[frame["segment"] == "Healthcare"].iloc[0]
    result = analyze_segment(healthcare)
    assert result["impact_class"] in {"critical", "warning"}
    assert result["health_score"] < 65


def test_advisory_dataframe():
    frame = forecast_dataframe(default_segments())
    advisory = advisory_dataframe(frame)
    assert len(advisory) == 9
    assert {"segment", "health_score", "impact", "gaps", "priority_actions"} <= set(advisory.columns)
