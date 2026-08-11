"""Canonical dashboard data and market ticker fixtures."""

from __future__ import annotations

from copy import deepcopy

SEGMENTS: list[dict] = [
    {"segment": "Retail & E-Commerce", "icon": "🛒", "revenue": 450, "costs": 320, "units_sold": 85, "market_share": 18.5, "cac": 45, "churn": 8.2, "competitors": 4, "period": "2024 – 2028", "status": "active"},
    {"segment": "Financial Services", "icon": "💰", "revenue": 820, "costs": 580, "units_sold": 42, "market_share": 24.0, "cac": 120, "churn": 5.5, "competitors": 3, "period": "2024 – 2029", "status": "active"},
    {"segment": "Manufacturing", "icon": "🏭", "revenue": 310, "costs": 245, "units_sold": 120, "market_share": 12.3, "cac": 35, "churn": 12.1, "competitors": 5, "period": "2024 – 2027", "status": "review"},
    {"segment": "Logistics", "icon": "🚚", "revenue": 580, "costs": 410, "units_sold": 95, "market_share": 15.8, "cac": 28, "churn": 7.3, "competitors": 4, "period": "2024 – 2028", "status": "active"},
    {"segment": "Tech & SaaS", "icon": "💻", "revenue": 950, "costs": 520, "units_sold": 65, "market_share": 31.2, "cac": 85, "churn": 4.8, "competitors": 2, "period": "2024 – 2030", "status": "active"},
    {"segment": "Healthcare", "icon": "🏥", "revenue": 210, "costs": 195, "units_sold": 30, "market_share": 6.5, "cac": 150, "churn": 18.5, "competitors": 7, "period": "2024 – 2028", "status": "warning"},
    {"segment": "Energy & Utilities", "icon": "⚡", "revenue": 680, "costs": 490, "units_sold": 55, "market_share": 22.1, "cac": 65, "churn": 9.4, "competitors": 3, "period": "2024 – 2029", "status": "active"},
    {"segment": "Telecom & Media", "icon": "📡", "revenue": 390, "costs": 310, "units_sold": 78, "market_share": 14.2, "cac": 42, "churn": 14.8, "competitors": 6, "period": "2024 – 2027", "status": "review"},
    {"segment": "Consumer Goods", "icon": "🛍", "revenue": 230, "costs": 210, "units_sold": 140, "market_share": 8.7, "cac": 22, "churn": 11.2, "competitors": 5, "period": "2024 – 2028", "status": "review"},
]

TICKER_DATA: list[dict] = [
    {"name": "S&P 500", "icon": "📈", "price": 7489.72, "change": 0.70, "up": True, "type": "index"},
    {"name": "NASDAQ", "icon": "📊", "price": 25373.85, "change": 1.00, "up": True, "type": "index"},
    {"name": "DOW", "icon": "🏛", "price": 52485.03, "change": 0.53, "up": True, "type": "index"},
    {"name": "EUR/USD", "icon": "💶", "price": 1.1527, "change": -0.01, "up": False, "type": "forex"},
    {"name": "GBP/USD", "icon": "💷", "price": 1.3482, "change": 0.14, "up": True, "type": "forex"},
    {"name": "BTC", "icon": "₿", "price": 62953.87, "change": 0.25, "up": True, "type": "crypto"},
    {"name": "ETH", "icon": "Ξ", "price": 1869.76, "change": 0.31, "up": True, "type": "crypto"},
    {"name": "BNB", "icon": "🔶", "price": 577.02, "change": -1.49, "up": False, "type": "crypto"},
]


def default_segments() -> list[dict]:
    """Return a fresh copy of the default segment dataset."""
    return deepcopy(SEGMENTS)
