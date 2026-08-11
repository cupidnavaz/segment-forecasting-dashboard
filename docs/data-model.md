# Data Model

Each segment contains:

| Field | Meaning |
|---|---|
| `segment` | Business segment name |
| `icon` | Presentation icon |
| `revenue` | Revenue baseline |
| `costs` | Cost baseline |
| `units_sold` | Units sold |
| `market_share` | Market share percentage |
| `cac` | Customer acquisition cost |
| `churn` | Churn percentage |
| `competitors` | Number of relevant competitors |
| `period` | Forecast period label |
| `status` | Workflow status: `active`, `review`, or `warning` |
| `risk_override` | Optional explicit risk classification |

Calculated fields:

| Field | Meaning |
|---|---|
| `profit` | Revenue minus costs |
| `profit_margin` | Profit divided by revenue |
| `growth` | Base calculated growth |
| `scenario_growth` | Growth plus scenario adjustment |
| `risk` | `low`, `medium`, or `high` |
| `confidence` | Bounded forecast confidence score |
| `trend` | `up`, `flat`, or `down` |

The baseline data is inherited from the supplied HTML source and should be treated as dashboard/demo data unless a business data source is connected.
