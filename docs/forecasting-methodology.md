# Forecasting Methodology

The Python engine preserves the original dashboard's deterministic formulas.

## Profit

```text
profit = revenue - costs
```

## Profit margin

```text
profit_margin = (profit / revenue) × 100
```

## Base growth

```text
growth =
    (profit_margin × 0.8)
    + (market_share × 0.3)
    + (units_sold / 15)
    - (churn × 0.6)
```

Growth is rounded to one decimal place.

## Risk

If an explicit `risk_override` exists, it wins.

Otherwise:

- `high` if profit margin < 12%, churn > 18%, or competitors > 5.
- `low` if profit margin > 25%, churn < 8%, and competitors < 3.
- otherwise `medium`.

## Confidence

```text
confidence =
    60
    + (revenue / 40)
    + (units_sold / 10)
    - (churn × 1.5)
```

The result is rounded and bounded between 55 and 98.

## Trend

- `up` when growth > 10.
- `down` when growth < 0.
- `flat` otherwise.

## Scenario adjustment

The scenario slider adds a fixed percentage-point adjustment to calculated growth. In the live-linked scenario view, a separate bounded proxy adjustment is also applied:

```text
market_adjustment_pp =
    clip(proxy_return_over_lookback × sensitivity, -maximum_adjustment, +maximum_adjustment)

scenario_growth = growth + scenario + market_adjustment_pp
```

Proxy mappings are illustrative, editable assumptions—not measured sector betas. The bounded market-linked result is a scenario sensitivity tool, not a statistical forecasting model. It should not be interpreted as probabilistic forecasting or as evidence of causality. Market movements do not recalculate fixture revenue, costs, margin, churn, or confidence.
