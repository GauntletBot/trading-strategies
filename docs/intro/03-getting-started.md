# 3. Getting Started — Bootstrap a New Strategy

[← 2. Architecture](02-architecture.md) · [Intro index](README.md) · Next: [4. Glossary →](04-glossary.md)

---

This guide takes you from an idea to a first recorded, graded backtest. The [demo bot](../../dev/demo/demo-bot/) is a complete worked example. Keep it open in another tab and copy from it.

**The steps at a glance**

| # | Step | You produce |
|---|---|---|
| 0 | Get access and tools | Accounts, a local clone |
| 1 | Write a one-line hypothesis | One sentence |
| 2 | Explore in TradingView (optional, Stage 1) | A candidate worth building |
| 3 | Create your bot folder | `dev/{you}/{category}/{bot}/` |
| 4 | Write the DataSpec | `{bot}-dataspec.yaml` |
| 5 | Write the strategy | `{bot}-strategy (YYYY-MM-DD).md` |
| 6 | Write the bot ops doc | `{bot}-bot.md` |
| 7 | Write a story | `{bot}-story-{name}.md` |
| 8 | Write a run file with expected results | `{bot}-run (YYYY-MM-DD-NNN).md` |
| 9 | Validate locally | Clean CI check output |
| 10 | Commit, open a PR, merge | Files on `main` |
| 11 | Run the backtest | MLflow run with metrics |
| 12 | Record actual results | Graded run file |
| 13 | Update the story | `passing` or `failing` |
| 14 | Iterate honestly | New runs and new strategy versions |
| 15 | Promote | `staging/`, then `prod/` |

---

## Step 0 — Get access and tools

You need:

- **GitHub:** access to the [GauntletBot](https://github.com/GauntletBot) organization, plus `git` installed.
- **Python 3.11** or newer, to run the CI checks on your machine.
- **Databricks:** access to the workspace that holds the `gauntlet` catalog.
- **Alpaca:** an account with paper-trading API keys. Keep the keys in environment variables or a secrets manager. **Never commit keys to the repo.**
- **TradingView** (optional): only needed for Stage 1 exploration.

Then clone the repo and start a branch:

```bash
git clone https://github.com/GauntletBot/trading-strategies.git
cd trading-strategies
git checkout -b add-my-first-bot
pip install -r scripts/requirements.txt
```

## Step 1 — Write a one-line hypothesis

Before touching any code, write one sentence saying **why the edge should exist** and **who is on the other side of the trade**.

> Example: "On SPY 1-minute bars, short-term momentum persists for 10–30 minutes after a volume-confirmed moving-average cross, because slower participants keep buying after the move starts."

If you can't write this sentence, any result you find is probably noise.

## Step 2 — Explore in TradingView (optional, Stage 1)

Stage 1 is a cheap filter, not proof.

1. Paste the Pine harness (`harness_v1.pine`) into TradingView's Pine Editor and add it to a chart.
2. Set **realistic commission and slippage** in `strategy()`. Optimistic costs are the most common way a backtest lies.
3. Set the end date to the **vault boundary**. The vault must stay invisible in Stage 1 too.
4. Change one thing at a time. After each run, export the trade list (Strategy Tester → List of Trades → Download) and run:

   ```bash
   python analyze_trades.py is.csv --log experiments.csv --window IS --label "fast=10 slow=30"
   ```

5. Move on only when you have: the hypothesis, at least 100 trades, a profit-factor 90% confidence interval whose lower bound is above 1, and a **plateau** — neighbouring settings also work, not just one sharp best value.

Every variant you tried stays in the log. That count follows the idea into later stages.

## Step 3 — Create your bot folder

Folders live under `dev/` and use **lowercase letters, numbers and hyphens only**.

```bash
mkdir -p dev/your-github-username/momentum-bots/spy-volume-cross
```

- `your-github-username` — your personal sandbox. Only you merge into it.
- `momentum-bots` — a category. You can nest categories as deep as you like.
- `spy-volume-cross` — the **bot folder**. It must be a leaf: no folders inside it.

The bot folder name is the prefix of every file inside it.

## Step 4 — Write the DataSpec (`{bot}-dataspec.yaml`)

Declare the data **before** writing any strategy logic, and lock it before tuning anything.

```yaml
spec_id:     spy-volume-cross-spy-1min-2023
description: SPY 1-minute bars, calendar year 2023
version:     "1.0.0"
created:     "2026-11-20"
author:      your-github-username
bot:         spy-volume-cross

symbols:
  - SPY

start:       "2023-01-03"
end:         "2023-12-29"
frequency:   1Min          # tick, quote, 1Min, 5Min, 15Min, 30Min, 1Hour, 4Hour, 1Day, 1Week, 1Month
source:      alpaca        # alpaca, polygon, yahoo, tiingo
feed:        sip           # sip (full market, paid for live data) or iex (free live data)
adjust:      true          # apply split and dividend adjustments
data_type:   bars          # bars, trades, quotes

min_bars_per_day:  300     # flag days with too few bars
max_gap_minutes:   5       # flag gaps longer than this
drop_extended:     true    # regular session only (09:30–16:00 ET)
fill_gaps:         false
```

**Required by CI:** `spec_id`, `symbols`, `start`, `end`, `frequency`, `source`, `feed`. Dates must be `YYYY-MM-DD`, and the values must come from the lists in the comments.

**Keep the vault in mind:** your development work should end at the vault boundary. Don't choose dates that reach into the newest 20% of history. The holdback sets inside the vault are fixed before Stage 1 (see [Multiple holdback sets](02-architecture.md#multiple-holdback-sets)).

## Step 5 — Write the strategy (`{bot}-strategy (YYYY-MM-DD).md`)

Copy [`demo-bot-strategy (2026-11-20).md`](<../../dev/demo/demo-bot/demo-bot-strategy (2026-11-20).md>) and rename it with **today's date**. It must contain these sections:

| Section | What to write |
|---|---|
| **Metadata** (a `yaml` block, first in the file) | `name` (= bot folder name), `version` (`X.Y.Z`), `author`, `status` (`draft`, `review`, `approved`, `deprecated`), `created`, `updated` |
| **Description** | One plain-English paragraph: what the strategy does and why |
| **Signal Logic** | Checklists under **Entry Conditions** and **Exit Conditions**, plus any filters |
| **Parameters** | A table: every tunable value with type, **units**, default, sweep range, constraint and the formula ID that defines it |
| **Calculation Logic** | The exact formula for every indicator, entry, exit, fill price, cost, position size and risk limit |
| **Risk Rules** | Position size, stops, targets, daily loss limit, overnight policy |
| **Python Implementation** | The strategy class. It must do exactly what Calculation Logic says |
| **Approval Checklist** | At least one checklist item |

**Be exact in Calculation Logic.** "Take profit 1%" isn't enough. Say 1% of *which* price, checked against *which* bar price, filled at *what* price, and what happens if the stop and the target are both hit in the same bar. The demo's [Calculation Logic section](<../../dev/demo/demo-bot/demo-bot-strategy (2026-11-20).md#calculation-logic>) shows the expected level of detail.

**When you change the logic**, update `version` and `updated`, and rename the file to the new date in the same commit. Git history keeps the old versions.

## Step 6 — Write the bot ops doc (`{bot}-bot.md`)

Copy [`demo-bot-bot.md`](../../dev/demo/demo-bot/demo-bot-bot.md). Required sections:

- **Identity** — a table with `Bot name`, `Owner`, `Environment` (`dev`, `staging` or `prod`) and `Status`. Start with `inactive — backtesting only`.
- **Runtime Configuration** — set `execution_mode: backtest`, capital, maximum position size and timezone.
- **Monitoring & Alerts** — your daily loss alert and drawdown circuit breaker.
- **Known Issues** — can start empty.
- **Change Log** — at least one dated entry.

Also point the **Databricks Job Config** at your files: `strategy_name` is your bot name and `data_spec_id` is your DataSpec's `spec_id`.

## Step 7 — Write a story (`{bot}-story-{name}.md`)

Copy [`STORY_TEMPLATE.md`](../STORY_TEMPLATE.md). The story is **why you are running**: without one you are exploring, with one you are testing.

1. **Hypothesis** — a specific, falsifiable claim.
2. **Acceptance Criteria** — numeric thresholds for every metric that matters, such as total return ≥ 0%, Sharpe ≥ 0.5, maximum drawdown ≤ 10%, win rate ≥ 40% and at least 50 trades.
3. Set `status: open`. Leave **Result** and **What We Learned** blank for now.

## Step 8 — Write a run file with expected results (`{bot}-run (YYYY-MM-DD-NNN).md`)

Copy [`RUN_TEMPLATE.md`](../RUN_TEMPLATE.md). `NNN` counts runs on that day: `001`, `002` and so on.

Fill in:

- **Metadata** — `run_id`, `bot`, `strategy_file`, `dataspec_file`, `run_date`, `run_number`, `author`, and `status: expected`.
- **Inputs** — symbols, period, frequency, starting cash, fees and slippage.
- **Parameters Used** — the exact value of **every** parameter for this run.
- **Expected Results** — your acceptance criteria as numeric targets.

Leave **Actual Results** blank. **This is the TDD contract:** expected results are written and committed *before* the backtest runs. CI fails if they still say `-ToDo`.

## Step 9 — Validate locally

Run the same checks CI will run:

```bash
echo '["dev/your-github-username/momentum-bots/spy-volume-cross"]' > /tmp/changed.json
PYTHONPATH=scripts python3 scripts/validate_all.py /tmp/changed.json
PYTHONPATH=scripts python3 scripts/validate_naming.py
```

Fix anything reported. Common mistakes: an uppercase letter or an underscore in a folder name, a missing date in the strategy filename, a metadata `name` that doesn't match the folder, or a missing required section.

## Step 10 — Commit, open a PR, merge

```bash
git add dev/your-github-username
git commit -m "Add spy-volume-cross bot with baseline story and run 001"
git push -u origin add-my-first-bot
```

Open a pull request into `main`. The **Validate Bot Files** workflow runs automatically. In `dev/` you merge your own PR once it passes.

## Step 11 — Run the backtest

As documented in each `bot.md`, merging the strategy or DataSpec to `main` triggers the bot's Databricks job (`{bot}-backtest`). The job:

1. loads the data named by your DataSpec from the `gauntlet` catalog,
2. runs your strategy class with the parameters in the run file,
3. logs metrics, the equity curve and the trade log to the MLflow experiment named in `bot.md`.

You can also start the job by hand in Databricks under **Jobs & Pipelines**.

## Step 12 — Record actual results

From the MLflow run:

1. Fill in **Actual Results** and mark each row ✓ or ✗.
2. Set `status: completed` (or `failed` if the run broke), and add `mlflow_run_id`.
3. Add the equity curve link and a **Trade Log Summary**.
4. Write **Observations** — what you noticed, including anything surprising.
5. List **Next Actions**.

CI fails if a `completed` run still contains `-ToDo`.

## Step 13 — Update the story

1. Add the run to the story's **Runs** table.
2. If every acceptance criterion passed, set `status: passing` and fill in **Result**.
3. If any failed, set `status: failing` and note which ones.
4. Write **What We Learned**. This is the most important section.

## Step 14 — Iterate honestly

- **One change per run.** New parameters mean a new run file. New logic means a new strategy version.
- **Count every attempt.** Every variant is a trial, including the ones that failed.
- **Prefer plateaus to peaks.** If only one exact setting works, it's probably luck.
- **Stress test.** Rerun with costs doubled, on 2–3 related symbols and on a neighbouring bar size. A real edge weakens under stress; it doesn't vanish.
- **Keep it simple.** Aim for at most 3–4 tuned parameters.

## Step 15 — Promote

| Move | How | Requires |
|---|---|---|
| `dev/` → `staging/` | PR that moves the bot folder | 1 approval, Databricks backtest passes, story `passing` |
| Vault test (Stage 3) | Freeze the model, run it once on the next unopened holdback set | Keeps ≥ 50% of development performance, inside the development 90% confidence interval, 95th-percentile Monte Carlo drawdown below 25% |
| Fine-tune and retest (optional) | Fold the opened set into training, retune, freeze a new version, run it once on the next set | An unopened holdback set remains; the round counts toward the trial count |
| Paper trading | Set `execution_mode: paper` in `bot.md` | A holdback set passed; runs 1–3 months |
| `staging/` → `prod/` | PR | 2 approvals, CI passes, paper results attached, every story `passing` |

Run and story files move with the bot. They are its evidence record.

---

[← 2. Architecture](02-architecture.md) · [Intro index](README.md) · Next: [4. Glossary →](04-glossary.md)
