# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-08-11

### Added

- Rebuilt the supplied `ultramodern.html` dashboard as a standard Python project.
- Added Streamlit application entry point.
- Extracted segment data into a dedicated data module.
- Ported the original forecasting formulas to Python.
- Added filtering, sorting, scenario analysis, and executive summary calculations.
- Added Plotly visualizations.
- Added explainable advisory analytics.
- Added Markdown executive reporting and CSV export.
- Added automated tests.
- Added PEP 621 packaging metadata.
- Added development tooling configuration.
- Added architecture, methodology, data model, operations, and release documentation.
- Added Git-ready ignore rules and contribution/security policies.

## Migration notes

The original HTML/CSS presentation layer was replaced by a maintainable Python/Streamlit presentation layer. The original calculation logic and source segment dataset are the authoritative basis for the Python implementation.

The original browser-only simulated market ticker was not promoted to a real data feed.
