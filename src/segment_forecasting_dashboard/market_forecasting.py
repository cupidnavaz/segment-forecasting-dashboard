"""Experimental market-linked segment scenario calculations.

This applies bounded, lagged market movement as a scenario input to the existing
segment fixture forecast. It does not derive company revenue from securities,
claim empirical sector correlations, or provide investment advice.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from .forecasting import forecast_dataframe

# Illustrative proxy assignments only. They are user-editable in the app and are
# not validated sector betas or claims of causal relationships.
SEGMENT_MARKET_PROXIES: dict[str, str] = {
    "Retail & E-Commerce": "^GSPC",
    "Financial Services": "^GSPC",
    "Manufacturing": "^GSPC",
    "Logistics": "CL=F",
    "Tech & SaaS": "^IXIC",
    "Healthcare": "^GSPC",
    "Energy & Utilities": "CL=F",
    "Telecom & Media": "^IXIC",
    "Consumer Goods": "^GSPC",
}


def proxy_returns(history: pd.DataFrame, lookback: int = 5) -> dict[str, float]:
    """Return latest close-to-close percentage moves over available observations."""
    if lookback < 1:
        raise ValueError("lookback must be at least one observation")
    if history.empty:
        return {}

    returns: dict[str, float] = {}
    for symbol, group in history.sort_values("date").groupby("symbol", sort=False):
        closes = pd.to_numeric(group["close"], errors="coerce").dropna()
        if len(closes) >= 2:
            periods = min(lookback, len(closes) - 1)
            starting_close = closes.iloc[-periods - 1]
            if starting_close != 0:
                returns[str(symbol)] = float((closes.iloc[-1] / starting_close - 1) * 100)
    return returns


def market_linked_forecast(
    segments: Iterable[dict],
    history: pd.DataFrame,
    *,
    scenario: float = 0.0,
    sensitivity: float = 0.5,
    max_adjustment: float = 5.0,
    lookback: int = 5,
    proxies: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Calculate an explicitly bounded market-linked scenario forecast.

    Market adjustment in growth percentage points is:
    ``clip(proxy lookback return * sensitivity, -max_adjustment, max_adjustment)``.
    The usual user scenario is then added to baseline segment growth. Missing proxy
    history contributes zero adjustment and is marked as unavailable in output.
    """
    if not np.isfinite(sensitivity) or sensitivity < 0:
        raise ValueError("sensitivity must be a finite, non-negative number")
    if not np.isfinite(max_adjustment) or max_adjustment < 0:
        raise ValueError("max_adjustment must be a finite, non-negative number")

    frame = forecast_dataframe(segments, scenario=0.0)
    if frame.empty:
        frame["market_proxy"] = pd.Series(dtype=str)
        frame["proxy_return_pct"] = pd.Series(dtype=float)
        frame["market_adjustment_pp"] = pd.Series(dtype=float)
        frame["scenario_growth"] = pd.Series(dtype=float)
        return frame

    proxy_map = proxies or SEGMENT_MARKET_PROXIES
    changes = proxy_returns(history, lookback)
    frame["market_proxy"] = frame["segment"].map(proxy_map).fillna("")
    frame["proxy_return_pct"] = frame["market_proxy"].map(changes)
    frame["market_adjustment_pp"] = (
        frame["proxy_return_pct"]
        .fillna(0.0)
        .mul(sensitivity)
        .clip(-max_adjustment, max_adjustment)
        .round(2)
    )
    frame["scenario_growth"] = (
        frame["growth"] + float(scenario) + frame["market_adjustment_pp"]
    ).round(1)
    frame["trend"] = frame["scenario_growth"].map(
        lambda growth: "up" if growth > 10 else "down" if growth < 0 else "flat"
    )
    return frame
