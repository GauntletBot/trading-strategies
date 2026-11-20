# Story: VWAP Scalp Baseline 2023

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
story_id:    vwap-scalp-story-baseline-2023
bot:         vwap-scalp
author:      quant-dev
created:     2026-11-20
status:      open
hypothesis:  >
  VWAP scalp with default params on SPY 1-min data for 2023 will produce a
  Sharpe ratio above 0.8, stay within a 5% max drawdown, and win on at least
  50% of trades — confirming that VWAP bounce entries with volume confirmation
  generate high-probability scalps on liquid intraday data.
```

---

## Hypothesis

VWAP scalp (default params) run on SPY 1-minute bars for calendar year 2023
will produce a viable baseline: better risk-adjusted returns than trend-following
(Sharpe > 0.8), tighter drawdowns (< 5%), high win rate (> 50%), and high
trade frequency (> 100 trades).

This is the foundation run. Realistic slippage (0.1% round-trip) is included
to guard against overly optimistic fill assumptions common in scalping backtests.

---

## Acceptance Criteria

- [ ] Total return >= 0%
- [ ] Sharpe ratio >= 0.8
- [ ] Max drawdown <= 5%
- [ ] Win rate >= 50%
- [ ] Total trades >= 100

---

## Runs

| Run file | Date | Status | Notes |
|---|---|---|---|
| `vwap-scalp-run (2026-11-20-001).md` | 2026-11-20 | pending | Initial baseline — default params, 0.1% slippage |

---

## Result

**Story status:** OPEN — run not yet executed

**Summary:** -ToDo

---

## What We Learned

-ToDo
