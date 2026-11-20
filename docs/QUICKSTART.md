# Quick Start — from idea to candidate in TradingView

This guide gets you from a trading idea to a **candidate** worth porting to Python, using only TradingView and one Python script on your laptop. It covers the first two stages of the gauntlet:

| Stage | Question it answers | You finish with |
|---|---|---|
| **0 — Quick backtest (benchmark)** | Does the idea, exactly as written and untuned, make money after costs? | A pass/fail and a benchmark to beat |
| **1 — Discover** | Is this idea worth building properly? | A candidate spec, ready for Stage 2 |

Plan on an afternoon for your first idea. For the full picture, see the [intro for beginners](intro/README.md) or the [slide deck](https://drive.google.com/drive/folders/1LKs8QqLk9bggxP_k-VIWt-hlOmJST0SS).

---

## Before you start

You need:

- **TradingView**, any plan. Premium or higher adds Bar Magnifier (realistic fills inside a bar) and Deep Backtesting (full intraday history). Without them, pick a timeframe where enough bars load.
- **Python 3.11+** with `pip install pandas numpy openpyxl tabulate`.
- **The two tools:**
  - `harness_v2.pine`: the Pine Script strategy harness, with a vault lock, test windows and risk-based sizing.
  - `analyze_trades.py`: grades a TradingView trade list and logs every trial.
- **Your split dates:** development end and vault start for your symbol. Everything on or after development end is off-limits during Stages 0 and 1.

**Write one sentence first.** Say why the edge should exist and who is on the other side of the trade. If you can't, any result you find is probably noise.

> *Example: "On SPY 15-minute bars, breakouts above the 20-bar high keep running when the daily trend is up, because slower participants chase the move."*

---

## Setup (once per idea, about 10 minutes)

1. **Load the harness.** Pine Editor → paste `harness_v2.pine` → Add to chart. Open the chart on the symbol and timeframe from your hypothesis.
2. **Set real costs.** In `strategy()`, set `commission_value` and `slippage` to your broker's real numbers. Then open the Strategy Tester's **Properties** and check nothing overrides them. Optimistic costs are the most common way a backtest lies.
3. **Lock the vault.** In the *Vault lock* inputs, enter your **Development end** and **Vault start**. The harness never trades on or after development end, and shades the embargo orange and the vault red.
4. **Set the test windows.** In *Test window*, set **Data start** and **In-sample end / OOS start**, about 60–70% in-sample and 30–40% out-of-sample, both inside the development period.
5. **Pick your signal.** In *Signal*, choose the module that matches your hypothesis, such as Donchian breakout, EMA cross or RSI pullback. A new idea goes in as another option in section 2 of the script.
6. **Create a work folder** for this idea, for example `~/gauntlet/{bot-name}/`. Every export and the experiment log go here.

---

## Stage 0 — Quick backtest (the benchmark)

**Goal:** one honest run of the idea exactly as written. No tuning.

1. Set **Window = In-sample**. Leave every parameter at the value your hypothesis states.
2. Strategy Tester → **List of Trades** → Download, and save as `stage0.csv`.
3. Grade it and start the experiment log:

   ```bash
   python analyze_trades.py stage0.csv --log experiments.csv --window IS --label "benchmark, untuned" --out stage0-report.md
   ```

   This is **trial #1**. Every later run adds to the count.
4. From the Strategy Tester's *Performance Summary*, note the **buy-and-hold return** for the same period. That's the number every later version has to beat.

**Pass gate (proposal):** enough trades to judge, at least 30 and ideally 100, and **positive expectancy after costs**.

**If it fails, stop.** An idea that loses money untuned rarely becomes real through tuning. More often you'd just be fitting noise. Rewrite the hypothesis, which counts as a new idea and starts again at Stage 0, or move on.

---

## Stage 1 — Discover

**Goal:** find out whether the idea holds up, without fooling yourself.

### 1. Explore on in-sample only

- Keep **Window = In-sample**.
- **Change one thing at a time**, such as the Donchian length, the HTF filter on or off, or the stop multiple.
- **Log every run**, failures included:

  ```bash
  python analyze_trades.py is-don25.csv --log experiments.csv --window IS --label "don=25 htf=D/50 stop=2ATR"
  ```

  The trial count drives the Deflated Sharpe hurdle. Skipped logs make a lucky result look real.
- Keep to **at most 3–4 tuned parameters**. Each extra knob is another way to overfit.

### 2. Look for a plateau, not a peak

A setting is robust when its neighbours also work. For example, a Donchian length that profits at 15, 20, 25 and 30 is a plateau, while one that only works at 22 is overfit. Pick the **middle of the plateau**, not the single best value.

### 3. Stress-test the plateau

| Test | How | What you want |
|---|---|---|
| Costs ×2 | Double commission and slippage | Profit shrinks but stays positive |
| Related symbols | Run on 2–3 similar markets (e.g. QQQ, IWM) | Works on most, not just one |
| Neighbouring timeframe | One step up or down (e.g. 15m → 30m) | Similar behaviour |

A real edge weakens under stress; a fake one disappears. Log these runs too.

### 4. Walk-forward (optional, stronger evidence)

For each fold k = 2…N:
1. Set **Window = WF train (folds before k)**, choose settings, and log the runs.
2. Set **Window = WF test (fold k)** without changing settings, and export.

Judge the **combined** test results, not the best fold.

### 5. Out-of-sample: one shot

When in-sample passes, switch **Window = Out-of-sample** and change **nothing else**:

```bash
python analyze_trades.py oos.csv --compare is.csv --log experiments.csv --window OOS --out oos-report.md
```

If you go back and tweak anything after seeing this result, the out-of-sample period is now in-sample. Say so in the log label, and don't count it as an out-of-sample pass.

### Stage 1 pass gate

Move on only when **all** of these hold:

- [ ] A one-line hypothesis that names who is on the other side
- [ ] At least **100 trades**
- [ ] Profit factor **90% confidence lower bound above 1** (from the analyzer)
- [ ] A **plateau**: neighbouring settings also work
- [ ] Out-of-sample keeps at least **50% of in-sample CAGR**
- [ ] Survives costs ×2 and at least one related symbol

The analyzer also reports Deflated Sharpe, Monte Carlo drawdown and year-by-year stability. They aren't required to leave Stage 1, but a weak result there is a warning for Stage 2.

---

## Finalize the candidate (hand-off to Stage 2)

The hand-off is a **written spec**, not the Pine code. Stage 2 rebuilds the strategy in Python from your spec, so write it so someone else could code it.

1. **Create your bot folder:** `dev/{your-github-username}/{category}/{bot-name}/`.
2. **Write the strategy file**, `{bot-name}-strategy (YYYY-MM-DD).md`:
   - the one-line hypothesis
   - entry, exit and risk rules **in plain language**
   - each parameter with its **plateau range**, not just the single value you used
   - costs used (commission, slippage) and the split dates
3. **Write the DataSpec**, `{bot-name}-dataspec.yaml`: symbols, timeframe, date range, data source and feed, matching what you tested.
4. **Write the bot ops doc**, `{bot-name}-bot.md`. A stub is fine at this point.
5. **Attach the evidence** in the folder or linked from the strategy file:
   - `experiments.csv`, which carries the **trial count** into Stage 2
   - `stage0-report.md`, the in-sample report and `oos-report.md`
   - a screenshot of the harness **run card** showing the exact settings and vault lock dates
6. **Validate locally**, then commit:

   ```bash
   pip install -r scripts/requirements.txt
   python scripts/validate_all.py
   ```

   Strategy files are code-adjacent, so open a PR; CI checks every file.

Stage 2's first job is to **reproduce your TradingView trades in Python** within a small tolerance before any tuning. A clear spec makes that quick.

---

## Common traps

- **Repainting.** Only read higher timeframes with `request.security(..., [close[1]], lookahead = barmerge.lookahead_on)`. The harness already does this. Never use `lookahead_on` without the `[1]` offset.
- **Same-bar stop and target.** Without Bar Magnifier, TradingView guesses which one hit first. Treat those trades with suspicion.
- **Properties dialog overrides.** Settings changed there override `strategy()`. Check them before every comparison.
- **Default sizing.** 100% of equity per trade hides risk. The harness sizes by risk per trade instead (default 1%).
- **Deep Backtesting trades** don't appear on the chart, only in the report. Export from there.
- **Survivorship.** A stock you pick today is one that survived. Test baskets, and include delisted names where you can.

---

## Next steps

- [Getting started, steps 3–15](intro/03-getting-started.md): the full path from your bot folder to a graded Databricks backtest and promotion.
- [Glossary](intro/04-glossary.md): every term, in plain English.
- [Naming convention](NAMING_CONVENTION.md): exact file-name rules CI enforces.
