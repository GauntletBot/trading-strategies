# Story: Demo Bot Baseline 2023

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
story_id:    demo-bot-story-demo
bot:         demo-bot
author:      demo
created:     2026-11-20
status:      passing
hypothesis:  >
  A simple moving average crossover on SPY 1-min data for 2023 will produce
  a positive Sharpe ratio above 0.5, stay within a 10% max drawdown, and
  generate at least 50 trades — confirming the strategy captures genuine
  intraday trend signal on liquid data with realistic costs applied.
```

---

## Hypothesis

A simple trend-following strategy (fast MA / slow MA crossover) run on SPY
1-minute bars for calendar year 2023 with realistic fees (0.1% round-trip)
and slippage (0.1% round-trip) will produce a viable baseline result:
positive returns, controlled drawdown, and enough trade frequency to be
statistically meaningful.

This is the foundation story. All subsequent parameter sweeps and filter
additions will be measured against the numbers established here.

---

## Acceptance Criteria

- [x] Total return >= 0%
- [x] Sharpe ratio >= 0.5
- [x] Max drawdown <= 10%
- [x] Win rate >= 40%
- [x] Total trades >= 50

---

## Runs

| Run file | Date | Status | Notes |
|---|---|---|---|
| `demo-bot-run (2026-11-20-001).md` | 2026-11-20 | completed — PASS | Baseline, default params, full year 2023 |

---

## Result

**Story status:** PASSING

**Summary:** All five acceptance criteria met on the first run. Total return
of 9.3%, Sharpe of 0.87, max drawdown of 6.2%, win rate of 46.1%, and 73
trades across the year. The profit factor of 2.08 (avg win $412 / avg loss
$198) indicates the strategy has a genuine edge — winners run significantly
further than losers.

---

## What We Learned

1. **The strategy works on trending data.** Q1 and Q3 (trending months)
   drove the bulk of returns. Q2 (choppy, sideways) was a drag.

2. **A regime filter is the most promising next step.** Adding a VIX or
   ADX filter to avoid trading in low-volatility sideways conditions could
   materially improve risk-adjusted returns without changing the core logic.

3. **Costs matter but don't kill the strategy.** At 0.1% round-trip fees
   and slippage, the strategy remains profitable. However, any further
   friction (wider spreads, partial fills) should be stress-tested.

4. **Win rate (46%) is less important than profit factor (2.08).** This is
   a strategy that is right less than half the time but wins big when it is.
   Parameter tuning should preserve this asymmetry rather than chase a
   higher win rate.
