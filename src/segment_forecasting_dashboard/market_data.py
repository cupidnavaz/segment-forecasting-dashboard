"""Fetch public daily market history from Yahoo Finance's chart endpoint.

The segment fixture dataset remains local; this module adds a separate live-data
layer for market context. Tickers are restricted to a curated watchlist and the
remote request has a short timeout so a vendor outage cannot hang the dashboard.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd

WATCHLIST: dict[str, str] = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ Composite",
    "^DJI": "Dow Jones Industrial Average",
    "CL=F": "Crude Oil Futures",
    "GC=F": "Gold Futures",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
}
PERIODS = {"1mo", "3mo", "6mo", "1y", "2y"}


class MarketDataError(RuntimeError):
    """Raised when no selected market instruments can be loaded."""


def parse_chart_response(payload: dict, symbol: str) -> pd.DataFrame:
    """Convert a Yahoo chart API response into normalized daily observations."""
    results = payload.get("chart", {}).get("result") or []
    if not results:
        error = payload.get("chart", {}).get("error") or {}
        raise MarketDataError(error.get("description", f"No data returned for {symbol}"))

    result = results[0]
    timestamps = result.get("timestamp") or []
    quote_data = (result.get("indicators", {}).get("quote") or [{}])[0]
    closes = quote_data.get("close") or []
    volumes = quote_data.get("volume") or []
    name = WATCHLIST.get(symbol, symbol)
    rows = [
        {
            "symbol": symbol,
            "instrument": name,
            "date": pd.to_datetime(timestamp, unit="s", utc=True),
            "close": close,
            "volume": volumes[index] if index < len(volumes) else None,
        }
        for index, (timestamp, close) in enumerate(zip(timestamps, closes, strict=False))
        if close is not None
    ]
    return pd.DataFrame(rows, columns=["symbol", "instrument", "date", "close", "volume"])


def fetch_market_history(
    symbols: Iterable[str], period: str = "6mo", timeout: float = 8.0
) -> pd.DataFrame:
    """Fetch daily close/volume observations for curated symbols.

    Individual symbol failures are tolerated when another symbol succeeds. The
    failures are recorded in ``DataFrame.attrs['unavailable']`` for the UI.
    """
    if period not in PERIODS:
        raise ValueError(f"Unsupported period: {period}")
    selected = list(dict.fromkeys(symbols))
    unknown = [symbol for symbol in selected if symbol not in WATCHLIST]
    if unknown:
        raise ValueError(f"Unsupported market symbol(s): {', '.join(unknown)}")
    if not selected:
        return pd.DataFrame(columns=["symbol", "instrument", "date", "close", "volume"])

    frames: list[pd.DataFrame] = []
    unavailable: dict[str, str] = {}
    for symbol in selected:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}?range={period}&interval=1d"
        request = Request(url, headers={"User-Agent": "segment-forecasting-dashboard/1.0"})
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            frame = parse_chart_response(payload, symbol)
            if frame.empty:
                unavailable[symbol] = "No observations returned"
            else:
                frames.append(frame)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, MarketDataError) as exc:
            unavailable[symbol] = str(exc) or exc.__class__.__name__

    if not frames:
        details = "; ".join(f"{symbol}: {reason}" for symbol, reason in unavailable.items())
        raise MarketDataError(f"Market data is currently unavailable. {details}")

    history = pd.concat(frames, ignore_index=True).sort_values(["date", "symbol"])
    history.attrs["unavailable"] = unavailable
    history.attrs["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return history.reset_index(drop=True)


def market_snapshot(history: pd.DataFrame) -> pd.DataFrame:
    """Return the latest close and previous-observation change per instrument."""
    columns = ["symbol", "instrument", "date", "close", "change_pct", "volume"]
    if history.empty:
        return pd.DataFrame(columns=columns)

    snapshot = history.sort_values("date").groupby("symbol", as_index=False, sort=False).tail(2)
    snapshot = snapshot.sort_values(["symbol", "date"])
    snapshot["change_pct"] = snapshot.groupby("symbol")["close"].pct_change() * 100
    latest = snapshot.groupby("symbol", as_index=False, sort=False).tail(1).copy()
    return latest.reindex(columns=columns).sort_values("instrument").reset_index(drop=True)


def market_briefing_markdown(snapshot: pd.DataFrame, fetched_at: str | None = None) -> str:
    """Create a concise, source-attributed market section for executive reports."""
    lines = ["## Live Market Context", "", "Source: Yahoo Finance chart data; not investment advice.", ""]
    if fetched_at:
        lines.append(f"Data retrieved: {fetched_at}")
        lines.append("")
    if snapshot.empty:
        lines.append("No live market observations were available when this report was generated.")
        return "\n".join(lines)

    lines.extend(["| Instrument | Latest close | Daily change |", "|---|---:|---:|"])
    for _, row in snapshot.iterrows():
        change = "N/A" if pd.isna(row["change_pct"]) else f"{row['change_pct']:+.2f}%"
        lines.append(f"| {row['instrument']} ({row['symbol']}) | {row['close']:,.2f} | {change} |")
    return "\n".join(lines)
