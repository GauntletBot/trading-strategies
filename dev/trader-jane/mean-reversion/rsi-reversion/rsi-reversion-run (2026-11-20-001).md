# Run: rsi-reversion — 2026-11-20 #001

## Docs

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](/docs/ARCHITECTURE.md) | Folder hierarchy, file roles, TDD workflow, promotion path, CI checks |
| [NAMING_CONVENTION.md](/docs/NAMING_CONVENTION.md) | Naming rules, valid/invalid examples, and update guidance for all 5 file types |
| [RUN_TEMPLATE.md](/docs/RUN_TEMPLATE.md) | Copy-paste template for a new run file |
| [STORY_TEMPLATE.md](/docs/STORY_TEMPLATE.md) | Copy-paste template for a new story file |

---

## Metadata
```yaml
run_id:           rsi-reversion-run-2026-11-20-001
bot:              rsi-reversion
strategy_file:    rsi-reversion-strategy (2026-11-20).md
dataspec_file:    rsi-reversion-dataspec.yaml
run_date:         2026-11-20
run_number:       "001"
author:           trader-jane
engine:           vectorbt
engine_version:   0.26.0
status:           expected
mlflow_run_id:    ~
```

---

## Inputs

| Field | Value |
|---|---|
| Strategy | `rsi-reversion-strategy (2026-11-20).md` |
| DataSpec | `rsi-reversion-dataspec.yaml` |
| Symbols | QQQ |
| Period | 2023-01-03 → 2023-12-29 |
| Frequency | 1Min |
| Feed | sip |
| Init cash | $50,000 |
| Fees | 0.1% round-trip |
| Slippage | 0.1% round-trip |

## Parameters Used

| Parameter | Value |
|---|---|
| rsi_period | 14 |
| oversold_threshold | 30 |
| exit_threshold | 55 |
| stop_loss | 0.006 |
| vwap_filter | true |

---

## Expected Results (TDD — fill before running)

| Metric | Expected | Operator | Rationale |
|---|---|---|---|
| Total return | 0% | >= | Strategy must be profitable before iterating |
| Sharpe ratio | 0.5 | >= | Minimum viable risk-adjusted return |
| Max drawdown | 8% | <= | Mean reversion should have tighter drawdowns than trend-following |
| Win rate | 45% | >= | RSI oversold bounces should win more often than SMA crossovers |
| Total trades | 30 | >= | Need sufficient trades for statistical confidence |

**Pass criteria:** run PASSES if ALL expected metrics are met.

---

## Actual Results (filled after execution)

| Metric | Expected | Actual | Pass |
|---|---|---|---|
| Total return | >= 0% | -ToDo | -ToDo |
| Sharpe ratio | >= 0.5 | -ToDo | -ToDo |
| Max drawdown | <= 8% | -ToDo | -ToDo |
| Win rate | >= 45% | -ToDo | -ToDo |
| Total trades | >= 30 | -ToDo | -ToDo |

**Overall result:** -ToDo — PASS / FAIL

---

## Equity Curve

MLflow artifact: -ToDo

---

## Trade Log Summary

| Stat | Value |
|---|---|
| Total trades | -ToDo |
| Winning trades | -ToDo |
| Losing trades | -ToDo |
| Avg win | -ToDo |
| Avg loss | -ToDo |
| Largest win | -ToDo |
| Largest loss | -ToDo |
| Avg hold time | -ToDo |

---

## Observations

-ToDo

---

## Next Actions

- [ ] -ToDo
