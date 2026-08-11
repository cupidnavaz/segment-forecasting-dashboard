from segment_forecasting_dashboard.data import default_segments
from segment_forecasting_dashboard.forecasting import forecast_dataframe
from segment_forecasting_dashboard.reporting import build_markdown_report, export_csv


def test_report_contains_core_sections():
    frame = forecast_dataframe(default_segments())
    report = build_markdown_report(frame)
    assert "# Executive Forecast Report" in report
    assert "## Executive Summary" in report
    assert "Tech & SaaS" in report


def test_csv_export():
    frame = forecast_dataframe(default_segments())
    data = export_csv(frame)
    assert data.startswith(b"segment,period")
    assert b"Tech & SaaS" in data
