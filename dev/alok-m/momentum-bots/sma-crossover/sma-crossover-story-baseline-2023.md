# Story: SMA Crossover Baseline 2023

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
story_id:    sma-crossover-story-baseline-2023
bot:         sma-crossover
author:      alok-m
created:     2026-11-20
status:      open
hypothesis:  >
  SMA crossover with fast=10/slow=30 on SPY 1-min data for full year 2023
  will produce a positive Sharpe ratio, stay within a 10% max drawdown,
  and execute at least 50 trades — confirming the strategy generates
  meaningful signal on liquid intraday data.
```

---

## Hypothesis

SMA crossover (fast=10, slow=30) run on SPY 1-minute bars for calendar year 2023
will produce a viable baseline: positive returns, controlled drawdown, and
enough trade frequency to be statistically meaningful.

This is the foundation run. All future parameter sweeps and filter additions
will be measured against these baseline numbers.

---

## Acceptance Criteria

- [ ] Total return >= 0% (strategy must be profitable before costs)
- [ ] Sharpe ratio >= 0.5
- [ ] Max drawdown <= 10%
- [ ] Total trades >= 50 (enough signal to be meaningful)
- [ ] Win rate >= 40%

---

## Runs

| Run file | Date | Status | Notes |
|---|---|---|---|
| `sma-crossover-run (2026-11-20-001).md` | 2026-11-20 | pending | Initial baseline — default params |

---

## Result

**Story status:** OPEN — run not yet executed

**Summary:** -ToDo

---

## What We Learned

-ToDo
