# Run: vwap-scalp — 2026-11-20 #001

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
run_id:           vwap-scalp-run-2026-11-20-001
bot:              vwap-scalp
strategy_file:    vwap-scalp-strategy (2026-11-20).md
dataspec_file:    vwap-scalp-dataspec.yaml
run_date:         2026-11-20
run_number:       "001"
author:           quant-dev
engine:           vectorbt
engine_version:   0.26.0
status:           expected
mlflow_run_id:    ~
```

---

## Inputs

| Field | Value |
|---|---|
| Strategy | `vwap-scalp-strategy (2026-11-20).md` |
| DataSpec | `vwap-scalp-dataspec.yaml` |
| Symbols | SPY |
| Period | 2023-01-03 → 2023-12-29 |
| Frequency | 1Min |
| Feed | sip |
| Init cash | $25,000 |
| Fees | 0.1% round-trip |
| Slippage | 0.1% round-trip |

## Parameters Used

| Parameter | Value |
|---|---|
| vwap_band | 0.0005 |
| take_profit | 0.003 |
| stop_loss | 0.002 |
| max_hold_bars | 15 |
| volume_mult | 1.5 |
| momentum_period | 5 |

---

## Expected Results (TDD — fill before running)

| Metric | Expected | Operator | Rationale |
|---|---|---|---|
| Total return | 0% | >= | Strategy must be profitable before iterating |
| Sharpe ratio | 0.8 | >= | Scalping with tight stops should produce better risk-adjusted returns |
| Max drawdown | 5% | <= | Tight stops should limit drawdown more than trend strategies |
| Win rate | 50% | >= | VWAP bounces with volume confirmation should be high probability |
| Total trades | 100 | >= | Scalping should generate high trade frequency |

**Pass criteria:** run PASSES if ALL expected metrics are met.

---

## Actual Results (filled after execution)

| Metric | Expected | Actual | Pass |
|---|---|---|---|
| Total return | >= 0% | -ToDo | -ToDo |
| Sharpe ratio | >= 0.8 | -ToDo | -ToDo |
| Max drawdown | <= 5% | -ToDo | -ToDo |
| Win rate | >= 50% | -ToDo | -ToDo |
| Total trades | >= 100 | -ToDo | -ToDo |

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
