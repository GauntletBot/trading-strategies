# Strategy File Guide — `strategy.md`

## Docs

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Folder hierarchy, file roles, TDD workflow, promotion path, CI checks |
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | Naming rules, valid/invalid examples, and update guidance for all 5 file types |
| [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) | This file — every section of a strategy file, how each parameter is calculated, the Search Space section and its genetic-algorithm encoding |
| [RUN_TEMPLATE.md](RUN_TEMPLATE.md) | Copy-paste template for a new run file |
| [STORY_TEMPLATE.md](STORY_TEMPLATE.md) | Copy-paste template for a new story file |

---

The strategy file, `{bot-name}-strategy (YYYY-MM-DD).md`, is the **single source of truth** for a strategy. Its plain-language rules define every term that rule-based and ML models use, and each platform's code (Pine for TradingView, Python for Alpaca and Databricks) is derived from it. If the code and the file disagree, the file is right and the code is a bug.

The worked example throughout this guide is the demo bot: [`demo-bot-strategy (2026-11-20).md`](<../dev/demo/demo-bot/demo-bot-strategy (2026-11-20).md>).

**Contents**

1. [The file at a glance](#1-the-file-at-a-glance)
2. [Metadata](#2-metadata)
3. [Description and Signal Logic](#3-description-and-signal-logic)
4. [Parameters](#4-parameters)
5. [How each parameter is calculated (demo bot)](#5-how-each-parameter-is-calculated-demo-bot)
6. [Calculation Logic](#6-calculation-logic)
7. [Risk Rules, Target Dataset, Python Implementation, Backtest Results](#7-risk-rules-target-dataset-python-implementation-backtest-results)
8. [Search Space](#8-search-space)
9. [Genetic algorithm encoding](#9-genetic-algorithm-encoding)
10. [Approval Checklist](#10-approval-checklist)
11. [Changing a strategy](#11-changing-a-strategy)
12. [Common mistakes](#12-common-mistakes)

---

## 1. The file at a glance

Sections appear in this order. "CI" shows what [`validate_strategy.py`](../scripts/validate_strategy.py) enforces today.

| # | Section | Required | CI checks | What it answers |
|---|---|---|---|---|
| 1 | **Metadata** (`yaml` block) | Yes | Fields present and valid | Which strategy, which version, what status |
| 2 | **Description** | Yes | Present | What it does and why the edge should exist |
| 3 | **Signal Logic** (Entry Conditions, Exit Conditions, Filters) | Yes | Entry and Exit headings present | When it trades, in plain English |
| 4 | **Parameters** | Yes | At least one row | Every tunable value, with type, units, default, sweep range, constraint and formula |
| 5 | **Calculation Logic** | Yes (by review) | Not yet | The exact formula for every indicator, signal, fill, cost, size and limit |
| 6 | **Risk Rules** | Yes | Present | Position size, stops, targets, daily loss limit, overnight policy |
| 7 | **Search Space** | Only for genetic-algorithm (GA) tuning | Not yet | Which parameters the GA may change, over which grid |
| 8 | **Target Dataset** | Recommended | Not yet | Which DataSpec, symbols, bar frequency, warm-up history |
| 9 | **Python Implementation** | Yes | Present | The class that implements Calculation Logic exactly |
| 10 | **Backtest Results** | Recommended | Not yet | One row per version tested |
| 11 | **Approval Checklist** | Yes | At least one `- [ ]` item | What reviewers confirmed |

---

## 2. Metadata

The first `yaml` code block in the file. CI parses it.

| Field | Required | Format | Meaning |
|---|---|---|---|
| `name` | Yes | lowercase-hyphen | Must equal the bot folder name, e.g. `demo-bot`. |
| `version` | Yes | `X.Y.Z` (semver) | Changes whenever the logic, a default, a fixed constant or the Search Space changes. See [Changing a strategy](#11-changing-a-strategy). |
| `author` | Yes | username | Your folder username under `dev/`. |
| `status` | Yes | `draft`, `review`, `approved`, `deprecated` | Only `approved` strategies can be promoted. |
| `created` | Yes | `YYYY-MM-DD` | Date the strategy was first written. Never changes. |
| `updated` | Yes | `YYYY-MM-DD` | Date of the last change. Must match the date in the filename. |
| `env` | No | `dev`, `staging`, `prod` | Where the bot folder lives. |
| `tags` | No | list | Free-form labels for search, e.g. `[trend-following, intraday]`. |

---

## 3. Description and Signal Logic

**Description.** One plain-English paragraph: what the strategy does, on what market and timeframe, and the hypothesis — why the edge should exist and who is on the other side of the trade.

**Signal Logic.** Checklists under three headings:

- **Entry Conditions** — every condition that must be true to open a position.
- **Exit Conditions** — every way a position closes, in **priority order** (the first one listed wins if several fire on the same bar).
- **Filters** — conditions that block entries (volume, time of day, regime).

End each line with the formula ID that defines it, e.g. `— formula E1`. A reader should be able to go from any rule to its exact formula in one click.

---

## 4. Parameters

### 4.1 Column reference

| Column | Meaning | Rules |
|---|---|---|
| **Parameter** | Code name, in backticks. Must match the Python constructor argument exactly. | `snake_case` |
| **Type** | `int`, `float`, `bool` or `choice`. | `int` for counts of bars, minutes or shares; `float` for fractions and multipliers. |
| **Units** | What one unit means. | Always say bars of *which* frequency (`bars (1-min)`), and *fraction of which price* (`fraction of entry fill price (0.005 = 0.5%)`). Ambiguous units are the most common source of Python/Pine mismatches. |
| **Default** | The value used when nothing is specified. Stage 0 runs the defaults. | Must satisfy the constraint, and must lie on the Search Space grid if one exists. |
| **Sweep Range** | The values tried in a manual sweep (Stage 1 or 2). | A short list, usually 3 values around the default. Each value tried counts as a trial. |
| **Constraint** | Valid values and relationships with other parameters. | Write it as an inequality, e.g. `≥ 2, < slow_window`. The Python constructor must raise an error when it's broken. |
| **Description** | One line in plain English. | |
| **Formula** | The Calculation Logic ID(s) that use this parameter. | Every parameter must appear in at least one formula. A parameter with no formula is a bug. |

### 4.2 Parameters vs fixed constants

- **Parameters** may be tuned. Changing a parameter's *value* in a run is a new run, not a new strategy version.
- **Fixed constants** (the second table) are never tuned: position size, loss limits, time buffers, fee and slippage rates. Changing one **is** a strategy change: bump `version` and `updated`.
- Costs are always fixed constants. Tuning costs would let the optimizer "find" an edge by assuming cheaper trading.

---

## 5. How each parameter is calculated (demo bot)

This section walks through every demo-bot parameter and constant: what it is, the formula, a worked example with numbers, what happens when it moves, and what it interacts with. Write the same level of detail into Calculation Logic for your own strategy.

**Worked-example setup** (used below): starting equity $100,000; SPY signal bar closes at `C(t) = 400.00`; `slippage_rate = fee_rate = 0.0005` per side.

### `fast_window` — fast SMA lookback (int, bars, default 10) — formula I1

```
SMA_fast(t) = ( C(t) + C(t-1) + … + C(t - fast_window + 1) ) / fast_window
```

- The average of the last `fast_window` closes, **including the current bar**. Undefined until `fast_window` bars exist.
- **Example:** with `fast_window = 3` and closes 399.50, 400.10, 400.60, `SMA_fast = (399.50 + 400.10 + 400.60) / 3 = 400.07`.
- **Raising it** makes the fast line smoother and slower: fewer crosses, fewer trades, later entries.
- **Interacts with** `slow_window`: only the *gap* between the two lookbacks creates crosses. Must be `≥ 2` and `< slow_window`.

### `slow_window` — slow SMA lookback (int, bars, default 30) — formula I1

```
SMA_slow(t) = ( C(t) + C(t-1) + … + C(t - slow_window + 1) ) / slow_window
```

- Same formula with a longer window. It defines the "trend" the fast line crosses.
- **Raising it** filters out more chop but enters later in each trend.
- **Warm-up:** the strategy can't trade until `slow_window` bars exist. `min_history_bars` in Target Dataset must be at least the largest `slow_window` any run or the Search Space can produce.

### `stop_loss` — stop distance (float, fraction of entry fill price, default 0.005) — formula X1

```
entry_price = C(t) × (1 + slippage_rate)             (C1)
stop_level  = entry_price × (1 − stop_loss)
triggered if  L(t) ≤ stop_level, from bar t+1 on
fill (before slippage) = min( O(t), stop_level )
```

- **Example:** `entry_price = 400.00 × 1.0005 = 400.20`; `stop_level = 400.20 × 0.995 = 398.199`. If a later bar opens at 398.50 and trades down to 398.10, the stop fills at 398.199 before slippage, then `398.199 × 0.9995 = 397.9999` after.
- The stop is measured from the **entry fill** (which already includes slippage), not from the signal bar's close.
- It is fixed at entry and never moves.
- **Raising it** gives trades more room: fewer stop-outs, bigger losses when stopped.

### `take_profit` — target distance (float, fraction of entry fill price, default 0.010) — formula X2

```
target_level = entry_price × (1 + take_profit)
triggered if  H(t) ≥ target_level, from bar t+1 on
fill (before slippage) = max( O(t), target_level )
```

- **Example:** `target_level = 400.20 × 1.01 = 404.202`.
- **Same-bar rule:** if a bar's low hits the stop *and* its high hits the target, the stop is assumed to fill first, because 1-minute OHLC can't show the order.
- **Net of costs**, a target hit nets about +0.8% and a stop hit about −0.7% at default costs (0.2% round trip).
- **Interacts with** `stop_loss`: the ratio `take_profit / stop_loss` is the reward-to-risk multiple (default 2.0). This is why the Search Space encodes it as a ratio (see [Derived parameters](#95-derived-parameters-and-constraints)).

### `volume_lookback` — volume filter window (int, bars, default 20) — formulas I2, E2

```
AvgVol(t) = ( V(t) + V(t-1) + … + V(t - volume_lookback + 1) ) / volume_lookback
vol_ok(t) = V(t) > AvgVol(t)          (strictly greater)
```

- **Example:** if the last 20 bars average 50,000 shares, the entry bar needs more than 50,000 shares.
- The current bar is included in its own average, so a spike bar raises the bar it has to beat.
- **Raising it** makes the average steadier and the filter less sensitive to short bursts.

### Fixed constants

| Constant | Calculation | Worked example |
|---|---|---|
| `position_pct` (0.10) — R1 | `shares = floor( position_pct × equity(t) / entry_price )`; skip the entry if 0 | `floor(0.10 × 100,000 / 400.20) = floor(24.99) = 24` shares |
| `fee_rate` (0.0005 per side) — C1 | `fee = fill price × shares × fee_rate`, on entry and exit | Entry fee `400.20 × 24 × 0.0005 = $4.80` |
| `slippage_rate` (0.0005 per side) — C1 | Buys fill at `ref × (1 + rate)`, sells at `ref × (1 − rate)` | Buy at 400.00 → 400.20 |
| `daily_loss_limit` (0.02) — R2 | Halt when `equity(t) − day_start_equity ≤ −0.02 × day_start_equity` at any bar close | Day starts at $100,000 → flatten and halt at $98,000 or below |
| `open_buffer_min`, `close_buffer_min` (15) — E3 | `session_open + 15 min ≤ ts(t) < session_close − 15 min` | Normal day: entries allowed 09:45–15:44 bars |

**Whole trade, both outcomes** (24 shares, entry fill 400.20):

| Outcome | Exit fill | P&L after both fees |
|---|---|---|
| Stop at 398.199 | 397.9999 | about −$62.38 |
| Target at 404.202 | 403.9999 | about +$81.55 |

---

## 6. Calculation Logic

Calculation Logic is the contract the Python class must reproduce exactly. Use these conventions:

- **Notation first.** Define bar timing (start or end timestamp, time zone), `O/H/L/C/V`, what `t-1` means across sessions, and when a value is **undefined** (any rule that needs an undefined value is false).
- **Calculated Values table.** List every value computed, with its formula ID and units.
- **Formula IDs** by prefix:

  | Prefix | Covers | Demo examples |
  |---|---|---|
  | `I` | Indicators | I1 SMAs, I2 volume average |
  | `E` | Entry conditions and entry fill | E1 cross, E2 volume, E3 time window, E4 signal and fill |
  | `X` | Exits | X1 stop, X2 target, X3 reverse cross, X4 end of session |
  | `C` | Costs | C1 slippage and fees |
  | `R` | Sizing and risk limits | R1 position size, R2 daily loss limit |

- **For every price, say which price.** Measured from which price, checked against which bar price, filled at what price, and what happens when two rules fire on the same bar.
- **Fills.** State the reference price (close, open, level) and apply C1 slippage to every fill.
- **Timing.** State when exits start being checked (the demo: from bar `t+1`) and whether re-entry needs a new signal.

---

## 7. Risk Rules, Target Dataset, Python Implementation, Backtest Results

- **Risk Rules** — a short bullet list restating position size, max positions, stop, target, daily loss limit and overnight policy, each with its formula ID. It's the summary a reviewer checks first.
- **Target Dataset** — a `yaml` block with `recommended_dataspec`, `symbols`, `frequency` and `min_history_bars`. `min_history_bars` must cover the **longest lookback anywhere in the Search Space**, not just the default (the demo's largest possible `slow_window` is 200, and `min_history_bars` is 200).
- **Python Implementation** — the class path and code. Constructor arguments match the Parameters table names exactly, the constructor raises on broken constraints, and comments cite formula IDs. The `simulate` method is the reference execution the pipeline must match trade for trade.
- **Backtest Results** — one row per version and parameter set, with the MLflow run ID. Leave `-ToDo` until a run exists.

---

## 8. Search Space

The optional **Search Space** section tells the MetaGauntlet genetic algorithm (GA) which parameters it may change and over which values. Without this section, the GA can't touch the strategy.

### 8.1 Rules

1. **The GA tunes parameters, never logic.** Everything listed under `locked` stays human-written.
2. **Every gene maps to a row in the Parameters table** (directly, or as a derived parameter). The Parameters table stays the canonical list.
3. **At most 4 free genes** (`max_free_genes`). Each extra free parameter is another way to overfit.
4. **Every value is on a finite grid.** The GA never produces an off-grid value, so "neighbour" and "same strategy" have exact meanings.
5. **Defaults must be on the grid**, so the strategy as written is always a member of the population.
6. **Changing the Search Space is a strategy change.** Bump `version`; past GA results are not comparable with the new space.

### 8.2 Layout

Put the section after Risk Rules as a `yaml` block:

````markdown
## Search Space

```yaml
search_space:
  version: 1
  max_free_genes: 4
  objective_profile: metagauntlet-default
  edge_penalty: true
  blocks:
    signal:
      fast_window:     {type: int,  scale: log,    range: [5, 40],       points: 7,   default: 10}
      slow_ratio:      {type: real, scale: linear, range: [1.5, 5.0],    step: 0.5,   default: 3.0}
    risk:
      stop_loss:       {type: real, scale: linear, range: [0.002, 0.010], step: 0.001, default: 0.005}
      reward_multiple: {type: real, scale: linear, range: [1.0, 4.0],    step: 0.5,   default: 2.0}
  derived:
    slow_window: round_half_up(fast_window * slow_ratio)
    take_profit: round(stop_loss * reward_multiple, 6)
  fixed:
    volume_lookback: 20
  locked: [hypothesis, entry_logic, exit_logic, filters, session_rules, costs, risk_limits]
```
````

### 8.3 Top-level fields

| Field | Meaning |
|---|---|
| `version` | Version of the Search Space schema used by this file. Currently `1`. |
| `max_free_genes` | Maximum number of genes that may be **active** in any genome. If a genome has more (because conditional genes switched on), the decoder turns off the lowest-`priority` toggles until it fits. |
| `objective_profile` | Which set of GA objectives and hard limits to use (defined in MetaGauntlet, not here). `metagauntlet-default` = median walk-forward CAGR, worst-fold Sharpe, downside deviation, 95th-percentile Monte Carlo drawdown, probability of a drawdown over 25%. |
| `edge_penalty` | If `true`, a genome with any gene at the very first or last grid point is penalized. Optima sitting on the edge of a range are fragile, and usually mean the range is wrong. |
| `blocks` | Genes grouped by function (`signal`, `filter`, `risk`, `session`). Crossover takes each block whole from one parent, so settings that work together stay together. |
| `derived` | Parameters calculated from genes instead of searched directly. This is how relationships such as `fast < slow` are built in (see [9.5](#95-derived-parameters-and-constraints)). |
| `fixed` | Parameters held at a set value during GA runs. Each must be a Parameters-table row. |
| `locked` | Parts of the strategy the GA can never change. Listed for reviewers and enforced by the GA config. |

### 8.4 Gene fields

| Field | Applies to | Meaning |
|---|---|---|
| `type` | all | `int`, `real`, `ordinal`, `choice` or `bool` (see the table below). |
| `scale` | `int`, `real` | `linear`: grid points are evenly spaced (step apart). `log`: grid points are evenly spaced in ratio, so each step multiplies the value by the same factor. Use `log` for lookbacks and multipliers whose effect depends on relative size: 10 → 20 bars matters far more than 110 → 120. |
| `range` | `int`, `real` | `[low, high]`, both included. Both must be on the grid. |
| `step` | `linear` scale | Distance between grid points, in the parameter's own units. `(high − low)` must be a whole number of steps. Choose the smallest change you'd believe actually matters. |
| `points` | `log` scale | Number of grid points from `low` to `high`, spaced by a constant ratio. For `int`, values are rounded and duplicates removed. |
| `values` | `ordinal`, `choice` | The allowed options. For `ordinal`, list them in order. |
| `default` | all | Starting value. Must be on the grid and match the Parameters table default. |
| `active_if` | any | Makes the gene **conditional**: it only affects the strategy when the condition holds, e.g. `active_if: use_vol_filter`. |
| `priority` | `bool` | Used by `max_free_genes`: lower-priority toggles are switched off first. |

**Gene types**

| Type | Use for | Grid | Example |
|---|---|---|---|
| `int` | Counts: bars, minutes, shares | `step` or `points`, rounded to whole numbers | `fast_window` |
| `real` | Fractions, multipliers, thresholds | `step` or `points` | `stop_loss`, `reward_multiple` |
| `ordinal` | Options with a natural order | The listed values, in order | `htf_trend: [D/50, D/100, D/200]` |
| `choice` | Options with no order | The listed values | `ma_type: [sma, ema]` |
| `bool` | Feature toggles that enable a parameter | `false`, `true` | `use_vol_filter` |

A toggle must switch a filter that Signal Logic already describes as optional. If flipping it changes what the strategy fundamentally does, it's logic, and belongs under `locked`.

### 8.5 The demo grid

| Gene | Grid | Points |
|---|---|---|
| `fast_window` (log) | 5, 7, 10, 14, 20, 28, 40 | 7 |
| `slow_ratio` | 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0 | 8 |
| `stop_loss` | 0.002, 0.003, … , 0.010 | 9 |
| `reward_multiple` | 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0 | 7 |

The defaults (10, 3.0, 0.005, 2.0) reproduce the Parameters defaults exactly: `slow_window = 10 × 3.0 = 30`, `take_profit = 0.005 × 2.0 = 0.010`. The whole space has `7 × 8 × 9 × 7 = 3,528` distinct strategies.

### 8.6 Search Space vs Sweep Range

- **Sweep Range** (Parameters table) is a short hand-picked list for manual sweeps.
- **Search Space** is the full grid the GA may explore.
- Every Sweep Range value should lie inside the Search Space range. With derived parameters it may not be exactly on the grid (the demo's `take_profit` sweep 0.008 is a 1.6 reward multiple, which isn't a grid point); that's fine, because manual sweeps and GA runs are logged separately.

---

## 9. Genetic algorithm encoding

This section explains how the GA turns a Search Space into a **genome** (the numbers it evolves) and back into a strategy (the **phenotype**). The design follows the MetaGauntlet research notes (*GA Strategy Encoding* in Notion).

### 9.1 Why this encoding

- **Real-coded, not bit strings.** Binary encoding has "Hamming cliffs": neighbouring values such as 7 and 8 (`0111`, `1000`) differ in every bit, so small moves are hard. Real-coded genes with simulated binary crossover (SBX) and polynomial mutation are the standard for numeric parameters.
- **Every gene on a finite grid**, so neighbours, duplicates and trial counts are exact.
- **Relationships built into the encoding** (ratios), so the GA can't produce invalid strategies.

### 9.2 The genome

A genome is a vector `u = (u₁, …, uₙ)` with one entry per gene, in block order:

| Gene type | Genome entry | Operators |
|---|---|---|
| `int`, `real` | real number in `[0, 1]` | SBX crossover, polynomial mutation |
| `ordinal` | real number in `[0, 1]` | SBX crossover, polynomial mutation (moves to nearby options) |
| `choice` | option index | uniform swap crossover, random-resample mutation |
| `bool` | `0` or `1` | uniform swap crossover, bit-flip mutation (low rate) |

Crossover first picks each **block** whole from one parent, then applies SBX inside the block.

### 9.3 Building each gene's grid

For a gene with `N` grid points, `grid[0]` … `grid[N−1]`:

```
linear:   grid[k] = low + k × step,                       k = 0 … N−1,  N = (high − low) / step + 1
log:      grid[k] = low × (high / low) ^ ( k / (points − 1) ),   k = 0 … points−1
int:      round each grid value half-up to a whole number, then remove duplicates
ordinal:  grid = values, in listed order
```

**Example (log):** `fast_window`, range [5, 40], 7 points. The ratio between points is `(40/5)^(1/6) = 8^(1/6) ≈ 1.414`, giving 5, 7.07, 10, 14.14, 20, 28.28, 40, which rounds to **5, 7, 10, 14, 20, 28, 40**.

### 9.4 Decoding a genome

For each `int`, `real` or `ordinal` gene:

```
index = round_half_up( u × (N − 1) )        # 0 … N−1
value = grid[index]
```

Then, in order:

1. **Derived parameters** are calculated from the decoded genes (`derived:`).
2. **Inactive conditional genes** (their `active_if` is false) are ignored by the strategy.
3. **`fixed:` values** and every remaining Parameters default are filled in, so the result is a complete parameter set for the Python constructor.
4. **Constraints** from the Parameters table are checked. Derived parameters should make this always pass; if it fails, the encoding is wrong. Fix the Search Space, don't repair silently.
5. **Canonicalize:** set inactive genes to their defaults and round reals to 6 decimal places.
6. **Genome ID:** the first 12 hex characters of the SHA-256 hash of the canonical JSON `{"params": {…}, "strategy": name, "version": version}`, with keys sorted and no spaces. Two genomes that trade identically always get the same ID, so they're backtested once and counted as one trial.

### 9.5 Derived parameters and constraints

Encode relationships instead of repairing broken genomes:

| Relationship | Instead of searching | Search | Derived |
|---|---|---|---|
| `fast_window < slow_window` | `slow_window` | `slow_ratio ≥ 1.5` | `slow_window = round_half_up(fast_window × slow_ratio)` |
| Reward-to-risk | `take_profit` | `reward_multiple` | `take_profit = stop_loss × reward_multiple` |
| Session window | start and end | start and `duration` | end = start + duration |

The GA then can't produce an invalid pair like fast 20 / slow 20, and it searches directly over the quantities that matter (trend gap, reward-to-risk).

### 9.6 Conditional genes

```yaml
filter:
  use_vol_filter: {type: bool, default: false, priority: 1}
  vol_lookback:   {type: int, scale: log, range: [5, 60], points: 6, default: 20, active_if: use_vol_filter}
```

- `vol_lookback` stays in the genome when the filter is off and keeps mutating silently, so if the filter switches back on later it starts from a sensible value.
- Only **active** genes count toward `max_free_genes`.
- Canonicalization (step 5 above) resets inactive genes to their defaults, so turning a filter off produces one genome ID, not one per hidden value.

### 9.7 Neighbourhoods

The **neighbours** of a genome are the genomes one grid point away on one gene: `index ± 1` for each active gene, staying inside the grid. Four free genes give up to 8 neighbours (9 strategies including the centre).

MetaGauntlet scores each genome on itself **and** its neighbours, keeping the worst or the average, so a setting that only works at one sharp value scores poorly. This is the playbook rule "prefer plateaus to peaks", built into the fitness. Because neighbours are grid points with their own genome IDs, their backtests are cached and reused.

### 9.8 Worked example

Genome `u = (0.62, 0.40, 0.31, 0.55)` for `(fast_window, slow_ratio, stop_loss, reward_multiple)`:

| Gene | N | index = round(u × (N − 1)) | Value |
|---|---|---|---|
| `fast_window` | 7 | round(0.62 × 6) = round(3.72) = 4 | 20 |
| `slow_ratio` | 8 | round(0.40 × 7) = round(2.80) = 3 | 3.0 |
| `stop_loss` | 9 | round(0.31 × 8) = round(2.48) = 2 | 0.004 |
| `reward_multiple` | 7 | round(0.55 × 6) = round(3.30) = 3 | 2.5 |

Derived: `slow_window = 20 × 3.0 = 60`; `take_profit = 0.004 × 2.5 = 0.010`. Fixed: `volume_lookback = 20`.

Canonical JSON and genome ID (demo-bot 1.1.0):

```
{"params":{"fast_window":20,"slow_window":60,"stop_loss":0.004,"take_profit":0.01,"volume_lookback":20},"strategy":"demo-bot","version":"1.1.0"}
genome_id = 9ffd8034cd7c
```

Neighbours change one index by 1, e.g. `fast_window` 14 or 28 (slow 42 or 84), `slow_ratio` 2.5 or 3.5, `stop_loss` 0.003 or 0.005, `reward_multiple` 2.0 or 3.0.

### 9.9 Where GA variants live

The naming convention allows **one strategy file per bot folder**, so GA variants are not committed as files:

- Every evaluated genome is a row in the Databricks experiments table: genome ID, parent IDs, generation, decoded parameters, scores and the strategy `version` it belongs to.
- Only a **promoted champion** becomes a change to the strategy file: update the Parameters defaults (and the Search Space defaults) in a PR, bump `version`, and record the genome ID in Backtest Results.

### 9.10 GA or full grid?

On a small grid, test everything. The demo space has 3,528 strategies. If the evaluation budget covers every grid point (including Monte Carlo paths), a full grid is simpler and exact, and every neighbourhood score comes for free. Use the GA when the grid is larger than the budget. Either way, every distinct genome ID evaluated counts toward the trial count.

---

## 10. Approval Checklist

At least one item (CI checks). Recommended items:

- [ ] Signal logic described in plain English
- [ ] All parameters documented with type, units, default, sweep range, constraint and formula ID
- [ ] Calculation logic defined for every parameter and rule (formula IDs)
- [ ] Risk rules defined
- [ ] Search Space (if present): every gene maps to a parameter, defaults are on the grid, ≤ 4 free genes, `min_history_bars` covers the largest lookback in the space
- [ ] Python implementation matches spec
- [ ] Backtest run and results recorded
- [ ] PR reviewed by one other team member
- [ ] `status` set to `approved`

---

## 11. Changing a strategy

| Change | New version? | What to do |
|---|---|---|
| Typo or wording, meaning unchanged | No | Edit in place |
| Try different parameter values | No | New run file with the values in **Parameters Used** |
| Change a default | Yes | Bump `version`, update `updated` and the filename date |
| Change a fixed constant, a formula, a rule or the Search Space | Yes | Bump `version`, update `updated` and the filename date; past results don't carry over |
| Promote a GA champion | Yes | Set its values as defaults, record its genome ID in Backtest Results |

The filename date and `updated` always change together, in the same commit. Git history keeps old versions; delete the old file rather than keeping two strategy files in the folder.

---

## 12. Common mistakes

- **Ambiguous units:** `stop_loss: 0.5` — is that 0.5%, 0.5 dollars or 50%? Say `fraction of entry fill price (0.005 = 0.5%)`.
- **A parameter with no formula ID,** or a formula that uses a value not in Parameters or the constants table.
- **Code and spec drift:** the Python uses `>=` where Calculation Logic says `>`. The spec wins; fix the code.
- **Warm-up too short:** `min_history_bars` covers the default lookback but not the largest one the Search Space allows.
- **Defaults off the grid,** so the strategy as written can't be part of the GA population.
- **Searching both sides of a relationship** (`fast_window` and `slow_window`) instead of a ratio, so half the genomes are invalid.
- **Putting logic in the Search Space,** e.g. a toggle that swaps the entry rule. Logic changes are new strategy versions, written by a person.
- **Tuning costs.** Fees and slippage are fixed constants, always.
