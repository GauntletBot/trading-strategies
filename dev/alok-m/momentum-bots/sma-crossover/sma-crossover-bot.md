# Bot Operations Document: SMA Crossover

## Docs

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](/docs/ARCHITECTURE.md) | Folder hierarchy, file roles, TDD workflow, promotion path, CI checks |
| [NAMING_CONVENTION.md](/docs/NAMING_CONVENTION.md) | Naming rules, valid/invalid examples, and update guidance for all 5 file types |
| [RUN_TEMPLATE.md](/docs/RUN_TEMPLATE.md) | Copy-paste template for a new run file |
| [STORY_TEMPLATE.md](/docs/STORY_TEMPLATE.md) | Copy-paste template for a new story file |

---

## Identity

| Field | Value |
|---|---|
| Bot name | sma-crossover |
| Owner | alok-m |
| Environment | dev |
| Status | inactive — backtesting only |
| Last reviewed | 2026-11-20 |

---

## Runtime Configuration

```yaml
execution_mode:   backtest          # backtest | paper | live
broker:           alpaca
account_type:     paper
capital_allocated: 100000           # USD — paper account allocation
max_position_pct: 0.10              # 10% of capital per trade
schedule:         market_hours_only # 09:30–16:00 ET, Mon–Fri
timezone:         America/New_York
```

---

## Databricks Job Config

```yaml
job_name:         sma-crossover-backtest
cluster:          job-cluster-m5-xlarge
notebook_path:    /pipeline/03_run_backtest
parameters:
  strategy_name:  sma-crossover
  strategy_ver:   "1"
  data_spec_id:   sma-crossover-spy-1min-2023
mlflow_experiment: /backtests/alok-m/sma-crossover
```

---

## Monitoring & Alerts

- **Daily P&L alert:** Slack `#alok-m-bots` if daily loss > 1.5%
- **Position stuck alert:** alert if any position held > 60 minutes without an exit signal
- **Data gap alert:** alert if Alpaca feed goes silent > 2 minutes during market hours
- **Drawdown circuit breaker:** halt bot if portfolio drawdown exceeds 5% from session high

---

## Dependencies

| Dependency | Version | Notes |
|---|---|---|
| `alpaca-trade-api` | >=3.0.0 | Data + order execution |
| `vectorbt` | >=0.26.0 | Backtest engine |
| `pandas` | >=2.0.0 | |
| `mlflow` | >=2.10.0 | Experiment tracking |

---

## Deployment Notes

- Currently in **backtest mode only** — no live or paper trading wired up yet
- Requires Alpaca SIP data subscription for accurate intraday fills
- Databricks job triggered automatically when `sma-crossover-dataspec.yaml` is merged to `main`

---

## Known Issues

| Issue | Severity | Status |
|---|---|---|
| Strategy underperforms in choppy/sideways markets | Medium | Planned — add volatility regime filter |
| No overnight gap protection | Low | N/A — strategy is intraday only |

---

## Incident Log

| Date | Description | Resolution |
|---|---|---|
| — | No incidents yet | — |

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-11-20 | alok-m | Initial bot.md created |
