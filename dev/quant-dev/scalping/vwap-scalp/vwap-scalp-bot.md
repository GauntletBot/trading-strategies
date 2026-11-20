# Bot Operations Document: VWAP Scalp

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
| Bot name | vwap-scalp |
| Owner | quant-dev |
| Environment | dev |
| Status | inactive — backtesting only |
| Last reviewed | 2026-11-20 |

---

## Runtime Configuration

```yaml
execution_mode:    backtest
broker:            alpaca
account_type:      paper
capital_allocated: 25000           # Smaller allocation — high-frequency, test with less capital first
max_position_pct:  0.05
max_trades_per_day: 50
schedule:          market_hours_only
session_start_offset: 30m          # Skip first 30 min — VWAP unreliable at open
timezone:          America/New_York
```

---

## Databricks Job Config

```yaml
job_name:         vwap-scalp-backtest
cluster:          job-cluster-m5-2xlarge  # Larger — high trade count needs more memory
notebook_path:    /pipeline/03_run_backtest
parameters:
  strategy_name:  vwap-scalp
  strategy_ver:   "1"
  data_spec_id:   vwap-scalp-spy-1min-2023
mlflow_experiment: /backtests/quant-dev/vwap-scalp
```

---

## Execution Requirements

This strategy has stricter execution requirements than trend-following strategies:

| Requirement | Detail |
|---|---|
| Latency | < 100ms order placement from signal |
| Feed | SIP required — IEX will produce incorrect VWAP |
| Slippage model | At least 0.1% round-trip in backtest |
| Fill model | Use limit orders at VWAP price, not market orders |

---

## Monitoring & Alerts

- **Slack channel:** `#quant-dev-bots`
- **Trade count alert:** alert if > 40 trades by 2pm ET (pacing toward daily limit)
- **Daily P&L alert:** halt and alert if daily loss > 1.5%
- **VWAP integrity check:** alert if computed VWAP deviates > 0.5% from broker-reported VWAP
- **Consecutive loss alert:** alert if 5 consecutive losing trades — possible regime change

---

## Strategy-Specific Notes

- VWAP resets at session open (09:30 ET) — first 30 minutes of data are excluded from trading
- The `max_gap_minutes: 2` in the dataspec is intentional — gaps corrupt the cumulative VWAP
- Slippage is the most critical assumption for this strategy — overly optimistic fill assumptions will make backtest results look significantly better than live performance
- Upgrade path: replace 1-min bars with tick data for more realistic VWAP computation

---

## Known Issues

| Issue | Severity | Status |
|---|---|---|
| VWAP computed from bars, not ticks — less accurate | Medium | Planned — tick dataspec in progress |
| No SPY market regime filter implemented yet | Medium | Planned |
| Backtest engine does not natively support time-based exits | High | Workaround: implement in custom exit logic |

---

## Incident Log

| Date | Description | Resolution |
|---|---|---|
| — | No incidents yet | — |

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-11-20 | quant-dev | Initial bot.md created |
