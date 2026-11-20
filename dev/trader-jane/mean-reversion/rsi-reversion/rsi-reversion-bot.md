# Bot Operations Document: RSI Reversion

## Identity

| Field | Value |
|---|---|
| Bot name | rsi-reversion |
| Owner | trader-jane |
| Environment | dev |
| Status | inactive — backtesting only |
| Last reviewed | 2026-11-20 |

---

## Runtime Configuration

```yaml
execution_mode:    backtest
broker:            alpaca
account_type:      paper
capital_allocated: 50000
max_position_pct:  0.08
schedule:          market_hours_only
timezone:          America/New_York
```

---

## Databricks Job Config

```yaml
job_name:         rsi-reversion-backtest
cluster:          job-cluster-m5-xlarge
notebook_path:    /pipeline/03_run_backtest
parameters:
  strategy_name:  rsi-reversion
  strategy_ver:   "1"
  data_spec_id:   rsi-reversion-qqq-1min-2023
mlflow_experiment: /backtests/trader-jane/rsi-reversion
```

---

## Monitoring & Alerts

- **Slack channel:** `#trader-jane-bots`
- **Daily P&L alert:** if daily loss > 2%
- **RSI data quality:** alert if RSI values are NaN for more than 5 consecutive bars
- **VWAP recalculation:** VWAP resets at market open (09:30 ET) — verify reset logic

---

## Strategy-Specific Notes

- VWAP filter is critical — disable only when explicitly testing without it
- QQQ has higher intraday volatility than SPY; stop loss may need widening in high-VIX regimes
- Mean reversion strategies tend to perform poorly in strong trending markets (e.g., post-Fed announcement days)
- Consider adding a news/event calendar filter to avoid FOMC, CPI, and earnings days

---

## Known Issues

| Issue | Severity | Status |
|---|---|---|
| Performance degrades on high-VIX days | Medium | Planned — add VIX regime filter |
| Hourly RSI filter not yet implemented | Low | Planned — in next version |
| VWAP not volume-weighted in first bar of session | Low | Investigating |

---

## Incident Log

| Date | Description | Resolution |
|---|---|---|
| — | No incidents yet | — |

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-11-20 | trader-jane | Initial bot.md created |
