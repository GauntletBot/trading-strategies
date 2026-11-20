# Story: RSI Reversion Baseline 2023

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
story_id:    rsi-reversion-story-baseline-2023
bot:         rsi-reversion
author:      trader-jane
created:     2026-11-20
status:      open
hypothesis:  >
  RSI reversion with default params (period=14, oversold=30, exit=55) on QQQ
  1-min data for 2023 will produce a positive Sharpe ratio, stay within an 8%
  max drawdown, and win on at least 45% of trades — confirming mean reversion
  captures reliable oversold bounces on Nasdaq intraday data.
```

---

## Hypothesis

RSI reversion (rsi_period=14, oversold=30, exit=55, vwap_filter=true) run on QQQ
1-minute bars for calendar year 2023 will produce a viable baseline: positive
returns, tighter drawdowns than trend-following, and a win rate above 45%.

This is the foundation run. All future parameter adjustments and filter additions
will be measured against these baseline numbers.

---

## Acceptance Criteria

- [ ] Total return >= 0%
- [ ] Sharpe ratio >= 0.5
- [ ] Max drawdown <= 8%
- [ ] Win rate >= 45%
- [ ] Total trades >= 30

---

## Runs

| Run file | Date | Status | Notes |
|---|---|---|---|
| `rsi-reversion-run (2026-11-20-001).md` | 2026-11-20 | pending | Initial baseline — default params |

---

## Result

**Story status:** OPEN — run not yet executed

**Summary:** -ToDo

---

## What We Learned

-ToDo
