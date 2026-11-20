# Bot Operations Document: Demo Bot

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
| Bot name | demo-bot |
| Owner | demo |
| Environment | dev |
| Status | inactive — backtesting only |
| Last reviewed | 2026-11-20 |

---

## Purpose

The demo bot is the canonical reference implementation for the GauntletBot platform. It is not intended for live trading. Its purpose is to:

1. **Validate the pipeline end-to-end** — data fetch → backtest → metrics → MLflow → TDD story
2. **Demonstrate all five file types** — strategy, dataspec, bot, run, and story all fully populated
3. **Set the platform baseline** — the simplest viable trend-following strategy on liquid data with realistic costs, against which all future strategies are benchmarked
4. **Onboard new users** — copy this bot folder as a starting point for a new bot

---

## Runtime Configuration

```yaml
execution_mode:    backtest           # backtest | paper | live
broker:            alpaca
account_type:      paper
capital_allocated: 100000            # USD — paper account allocation
max_position_pct:  0.10              # 10% of capital per trade
schedule:          market_hours_only # 09:30–16:00 ET, Mon–Fri
timezone:          America/New_York
```

---

## Databricks Job Config

```yaml
job_name:          demo-bot-backtest
cluster:           job-cluster-m5-xlarge
notebook_path:     /pipeline/03_run_backtest
parameters:
  strategy_name:   demo-bot
  strategy_ver:    "1"
  data_spec_id:    demo-bot-spy-1min-2023
mlflow_experiment: /backtests/demo/demo-bot
```

---

## Monitoring & Alerts

- **Daily P&L alert:** Slack `#demo-bots` if daily loss > 1.5%
- **Position stuck alert:** alert if any position held > 60 minutes without an exit signal
- **Data gap alert:** alert if Alpaca feed goes silent > 2 minutes during market hours
- **Drawdown circuit breaker:** halt bot if portfolio drawdown exceeds 5% from session high

> Note: Monitoring is documented here for reference. The demo bot runs in backtest mode only — no live alerts are active.

---

## Dependencies

| Dependency | Version | Notes |
|---|---|---|
| `alpaca-trade-api` | >=3.0.0 | Data fetch (SIP feed) |
| `vectorbt` | >=0.26.0 | Backtest engine |
| `pandas` | >=2.0.0 | |
| `mlflow` | >=2.10.0 | Experiment tracking |
| `pyyaml` | >=6.0 | DataSpec parsing |

---

## Deployment Notes

- **Backtest mode only** — no live or paper order routing wired up
- Requires Alpaca SIP data subscription for accurate intraday 1-min bars
- Databricks job is triggered automatically when strategy or dataspec files are merged to `main`
- MLflow artifacts (equity curve, trade log) are stored under `/backtests/demo/demo-bot`

---

## Stories

| Story | Status | Notes |
|---|---|---|
| `demo-bot-story-demo.md` | passing | Baseline 2023 — all 5 criteria met, 9.3% return, 0.87 Sharpe |

---

## Known Issues

| Issue | Severity | Status |
|---|---|---|
| Underperforms in choppy/sideways markets (Q2 2023 drag) | Medium | Planned — add VIX or ADX regime filter |
| No overnight gap protection | Low | N/A — strategy is intraday only, always flat overnight |

---

## Incident Log

| Date | Description | Resolution |
|---|---|---|
| — | No incidents | — |

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-11-20 | demo | Initial bot.md created — full demo instance |
| 2026-11-20 | demo | Strategy 1.1.0: explicit calculation logic for all parameters; Python now applies stop, target, time window, EOD exit and daily limit. Status back to review pending re-run. |
