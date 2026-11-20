# Run: {bot-name} — {YYYY-MM-DD} #{NNN}

## Docs

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Folder hierarchy, file roles, TDD workflow, promotion path, CI checks |
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | Naming rules, valid/invalid examples, and update guidance for all 5 file types |
| [RUN_TEMPLATE.md](RUN_TEMPLATE.md) | This file — copy-paste template for a new run file |
| [STORY_TEMPLATE.md](STORY_TEMPLATE.md) | Copy-paste template for a new story file |

---

## Metadata
```yaml
run_id:           {bot-name}-run-{YYYY-MM-DD}-{NNN}   # matches filename
bot:              {bot-name}                            # matches bot folder name
strategy_file:    {bot-name}-strategy ({YYYY-MM-DD}).md
dataspec_file:    {bot-name}-dataspec.yaml
run_date:         {YYYY-MM-DD}
run_number:       {NNN}
author:           {github-username}
engine:           vectorbt                              # vectorbt | backtrader | custom
engine_version:   0.26.0
status:           expected                             # expected | completed | failed
mlflow_run_id:    ~                                    # filled after execution
```

---

## Inputs

| Field | Value |
|---|---|
| Strategy | `{bot-name}-strategy ({YYYY-MM-DD}).md` |
| DataSpec | `{bot-name}-dataspec.yaml` |
| Symbols | -ToDo |
| Period | -ToDo |
| Frequency | -ToDo |
| Feed | -ToDo |
| Init cash | -ToDo |
| Fees | -ToDo |
| Slippage | -ToDo |

## Parameters Used

| Parameter | Value |
|---|---|
| -ToDo | -ToDo |

---

## Expected Results (TDD — fill before running)

> Define what a passing run looks like before executing.
> These become the acceptance criteria the actual results are measured against.

| Metric | Expected | Operator | Rationale |
|---|---|---|---|
| Total return | -ToDo | >= | -ToDo |
| Sharpe ratio | -ToDo | >= | -ToDo |
| Max drawdown | -ToDo | <= | -ToDo |
| Win rate | -ToDo | >= | -ToDo |
| Total trades | -ToDo | between | -ToDo |

**Pass criteria:** run PASSES if ALL expected metrics are met.

---

## Actual Results (filled after execution)

| Metric | Expected | Actual | Pass |
|---|---|---|---|
| Total return | -ToDo | -ToDo | -ToDo |
| Sharpe ratio | -ToDo | -ToDo | -ToDo |
| Max drawdown | -ToDo | -ToDo | -ToDo |
| Win rate | -ToDo | -ToDo | -ToDo |
| Total trades | -ToDo | -ToDo | -ToDo |

**Overall result:** -ToDo — PASS / FAIL

---

## Equity Curve

> Attach or link equity curve artifact after execution.

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

> Notes on what the results mean, anomalies, and what to investigate next.

-ToDo

---

## Next Actions

> What changes to strategy or dataspec are warranted based on this run?

- [ ] -ToDo
