# Run: sma-crossover — 2026-11-20 #001

## Metadata
```yaml
run_id:           sma-crossover-run-2026-11-20-001
bot:              sma-crossover
strategy_file:    sma-crossover-strategy (2026-11-20).md
dataspec_file:    sma-crossover-dataspec.yaml
run_date:         2026-11-20
run_number:       "001"
author:           alok-m
engine:           vectorbt
engine_version:   0.26.0
status:           expected
mlflow_run_id:    ~
```

---

## Inputs

| Field | Value |
|---|---|
| Strategy | `sma-crossover-strategy (2026-11-20).md` |
| DataSpec | `sma-crossover-dataspec.yaml` |
| Symbols | SPY |
| Period | 2023-01-03 → 2023-12-29 |
| Frequency | 1Min |
| Feed | sip |
| Init cash | $100,000 |
| Fees | 0.1% round-trip |
| Slippage | 0.1% round-trip |

## Parameters Used

| Parameter | Value |
|---|---|
| fast_window | 10 |
| slow_window | 30 |
| stop_loss | 0.005 |
| take_profit | 0.010 |
| volume_lookback | 20 |

---

## Expected Results (TDD — fill before running)

| Metric | Expected | Operator | Rationale |
|---|---|---|---|
| Total return | 0% | >= | Strategy must be profitable before we iterate |
| Sharpe ratio | 0.5 | >= | Minimum viable risk-adjusted return |
| Max drawdown | 10% | <= | Acceptable intraday drawdown ceiling |
| Win rate | 40% | >= | SMA crossover typically wins ~45% but exits early |
| Total trades | 50 | >= | Need enough trades for statistical confidence |

**Pass criteria:** run PASSES if ALL expected metrics are met.

---

## Actual Results (filled after execution)

| Metric | Expected | Actual | Pass |
|---|---|---|---|
| Total return | >= 0% | -ToDo | -ToDo |
| Sharpe ratio | >= 0.5 | -ToDo | -ToDo |
| Max drawdown | <= 10% | -ToDo | -ToDo |
| Win rate | >= 40% | -ToDo | -ToDo |
| Total trades | >= 50 | -ToDo | -ToDo |

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
