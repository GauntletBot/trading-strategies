# Strategy: Demo Bot — SMA Crossover Baseline

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
name:        demo-bot
version:     1.1.0
author:      demo
status:      review
created:     2026-11-20
updated:     2026-11-20
env:         dev
tags:        [trend-following, intraday, equities, demo, sma-crossover]
```

---

## Description

A dual simple moving average (SMA) crossover strategy used as the canonical demo for the GauntletBot platform. Runs on SPY 1-minute bars for calendar year 2023 with realistic fees and slippage. Goes long when the fast SMA crosses above the slow SMA and exits on the reverse cross or a hard stop.

This strategy serves as the platform baseline — the simplest possible trend-following approach on liquid data with realistic costs, used to validate the full pipeline (data → backtest → metrics → TDD story) end-to-end before layering in complexity.

---

## Signal Logic

All rules are evaluated on completed bars. Formulas for every condition are in [Calculation Logic](#calculation-logic).

### Entry Conditions
- [ ] Fast SMA (default 10 bars) crosses above slow SMA (default 30 bars) — formula E1
- [ ] Cross must be fresh — fast was at or below slow on the prior bar — formula E1
- [ ] Not within the first 15 minutes of the regular session (09:30–09:45 ET) — formula E3
- [ ] Not within the last 15 minutes of the session (15:45–16:00 ET) — formula E3
- [ ] No position currently open and daily loss limit not hit — formulas E4, R2

### Exit Conditions
- [ ] Hard stop loss triggered — formula X1
- [ ] Take profit target hit — formula X2
- [ ] Fast SMA crosses below slow SMA (reverse cross) — formula X3
- [ ] Daily loss limit hit — formula R2
- [ ] End of session — always flat overnight — formula X4

If more than one exit fires on the same bar, the first one in this list wins.

### Filters
- [ ] Volume on entry bar above the `volume_lookback`-bar rolling average (confirms move) — formula E2

---

## Parameters

| Parameter | Type | Default | Sweep Range | Constraint | Description | Formula |
|---|---|---|---|---|---|---|
| `fast_window` | int | 10 | 5, 10, 20 | ≥ 2, < `slow_window` | Fast SMA lookback in bars | I1 |
| `slow_window` | int | 30 | 20, 30, 50 | > `fast_window` | Slow SMA lookback in bars | I1 |
| `stop_loss` | float | 0.005 | 0.003, 0.005, 0.008 | 0 < x < 1 | Stop distance below the entry fill price, as a fraction | X1 |
| `take_profit` | float | 0.010 | 0.008, 0.010, 0.015 | x > 0 | Target distance above the entry fill price, as a fraction | X2 |
| `volume_lookback` | int | 20 | 10, 20 | ≥ 1 | Lookback bars for the volume filter average | I2 |

**Sweep rule:** skip any combination where `fast_window >= slow_window` (for example fast 20 / slow 20). Those pairs can never cross.

**Fixed constants.** These are not swept. Changing one counts as a strategy change.

| Constant | Value | Used in |
|---|---|---|
| `position_pct` | 0.10 | R1 |
| `daily_loss_limit` | 0.02 | R2 |
| `open_buffer_min` | 15 | E3 |
| `close_buffer_min` | 15 | E3 |
| `fee_rate` | 0.0005 per side (0.1% round trip) | C1 |
| `slippage_rate` | 0.0005 per side (0.1% round trip) | C1 |

---

## Calculation Logic

### Notation

- Bars are 1-minute regular-session bars (09:30–16:00 ET) from the DataSpec. The timestamp `ts(t)` is the bar **start** time in `America/New_York`, so the session runs from the 09:30 bar to the 15:59 bar.
- `O(t)`, `H(t)`, `L(t)`, `C(t)`, `V(t)` are the open, high, low, close and volume of bar `t`.
- `t-1` is the previous bar in the series. Overnight is not a break: the 09:30 bar's previous bar is the prior session's 15:59 bar.
- A value is **undefined** until its full lookback window exists. A rule that needs an undefined value is false.

### Indicators

**I1 — Fast and slow SMA** (`fast_window`, `slow_window`)

```
SMA_fast(t) = ( C(t) + C(t-1) + … + C(t - fast_window + 1) ) / fast_window
SMA_slow(t) = ( C(t) + C(t-1) + … + C(t - slow_window + 1) ) / slow_window
```

- Simple arithmetic mean of closes. The current bar is included. Partial windows are not used.
- The windows run across session boundaries, so early bars each day still include the prior session's closes.

**I2 — Volume average** (`volume_lookback`)

```
AvgVol(t) = ( V(t) + V(t-1) + … + V(t - volume_lookback + 1) ) / volume_lookback
```

- The current bar is included, the same way as in I1.

### Entry

**E1 — Fresh bullish cross**

```
cross_up(t) = SMA_fast(t) > SMA_slow(t)  AND  SMA_fast(t-1) <= SMA_slow(t-1)
```

**E2 — Volume filter**

```
vol_ok(t) = V(t) > AvgVol(t)          (strictly greater)
```

**E3 — Entry time window**

```
time_ok(t) = session_open + open_buffer_min  <=  ts(t)  <  session_close - close_buffer_min
```

- `session_open` is the first bar of that day's session. `session_close` is the last bar's start time plus 1 minute.
- On a normal day the first allowed entry bar is 09:45 and the last is 15:44.
- On early-close days, such as 13:00 closes, the window ends 15 minutes before that day's actual close.

**E4 — Entry signal and fill**

```
enter(t) = cross_up(t) AND vol_ok(t) AND time_ok(t) AND flat(t) AND NOT halted(day)
```

- The entry fills at the close of the signal bar:

  ```
  entry_price = C(t) × (1 + slippage_rate)
  ```

- Holding periods start on bar `t+1`. Exits are not checked on the entry bar.
- Only one position may be open. A new entry needs a new fresh cross: after a stop or target exit, the strategy does not re-enter while fast stays above slow.

### Exits

All exit levels are fixed at entry and never move.

**X1 — Stop loss** (`stop_loss`)

```
stop_level = entry_price × (1 - stop_loss)
triggered if  L(t) <= stop_level
fill (before slippage) = min( O(t), stop_level )
```

- If the bar opens at or below the stop, the fill is the open.

**X2 — Take profit** (`take_profit`)

```
target_level = entry_price × (1 + take_profit)
triggered if  H(t) >= target_level
fill (before slippage) = max( O(t), target_level )
```

- If the bar opens at or above the target, the fill is the open.
- Example with default 0.010: entry fill 400.00 → target 404.00, stop 398.00.
- The target is measured on price, not on P&L after costs. At default costs (0.2% round trip) a target hit nets about +0.8%, and a stop hit about −0.7%.
- **Same-bar rule:** if both the stop and the target trigger on the same bar, the stop is assumed to fill first. 1-minute OHLC can't show which came first, so the conservative case is used.

**X3 — Reverse cross**

```
cross_down(t) = SMA_fast(t) < SMA_slow(t)  AND  SMA_fast(t-1) >= SMA_slow(t-1)
fill (before slippage) = C(t)
```

**X4 — End of session**

- Any open position is closed at `C(t)` of the session's last bar (15:59 on a normal day).

### Costs and sizing

**C1 — Slippage and fees on every fill**

```
buy fill  = reference price × (1 + slippage_rate)
sell fill = reference price × (1 - slippage_rate)
fee       = fill price × shares × fee_rate          (charged on entry and on exit)
```

**R1 — Position size**

```
shares = floor( position_pct × equity(t) / entry_price )
```

- `equity(t)` is cash plus open-position value at `C(t)`, on the entry bar.
- If `shares` is 0, the entry is skipped.

### Risk limits

**R2 — Daily loss limit** (`daily_loss_limit`)

```
day_start_equity = equity at C(t) of the prior session's last bar (or starting capital on day 1)
day_pnl(t)       = equity(t) - day_start_equity
halted(day)      = day_pnl(t) <= -daily_loss_limit × day_start_equity   at any bar close that day
```

- Equity includes unrealised P&L.
- When the limit is hit, any open position is closed at that bar's close, and there are no more entries for the rest of that session.
- The halt resets at the next session.

---

## Risk Rules

- **Max position size:** 10% of equity per trade, rounded down to whole shares (R1)
- **Max simultaneous positions:** 1 (single-symbol strategy) (E4)
- **Stop loss:** `stop_loss` × entry fill price below the entry fill, checked against each bar's low (X1)
- **Take profit:** `take_profit` × entry fill price above the entry fill, checked against each bar's high (X2)
- **Daily loss limit:** flatten and halt for the session if equity falls 2% below the prior session's closing equity (R2)
- **Overnight exposure:** none — close at the last bar of every session (X4)

---

## Target Dataset

```yaml
recommended_dataspec: demo-bot-dataspec.yaml
symbols:              [SPY]
frequency:            1Min
min_history_bars:     200
```

---

## Python Implementation

Class path: `models/demo_bot.py`

`generate_signals` returns the raw signal conditions. `simulate` is the reference bar-by-bar execution of every rule above. The backtest pipeline must reproduce its trades exactly. Comments cite the formula IDs.

```python
from models.base_strategy import BaseStrategy
import math
import numpy as np
import pandas as pd


class DemoBot(BaseStrategy):
    """SMA crossover baseline. Formula IDs (I1, E1, X1, ...) refer to the
    Calculation Logic section of demo-bot-strategy (2026-11-20).md."""

    name    = "demo-bot"
    version = "1.1.0"

    # Fixed constants (not swept)
    POSITION_PCT     = 0.10
    DAILY_LOSS_LIMIT = 0.02
    OPEN_BUFFER_MIN  = 15
    CLOSE_BUFFER_MIN = 15
    FEE_RATE         = 0.0005   # per side
    SLIPPAGE_RATE    = 0.0005   # per side

    def __init__(self, fast_window=10, slow_window=30,
                 stop_loss=0.005, take_profit=0.010, volume_lookback=20):
        if not 2 <= fast_window < slow_window:
            raise ValueError("require 2 <= fast_window < slow_window")
        if not 0 < stop_loss < 1 or take_profit <= 0 or volume_lookback < 1:
            raise ValueError("invalid stop_loss / take_profit / volume_lookback")
        self.fast_window     = fast_window
        self.slow_window     = slow_window
        self.stop_loss       = stop_loss
        self.take_profit     = take_profit
        self.volume_lookback = volume_lookback

    @property
    def default_params(self):
        return {
            "fast_window": 10, "slow_window": 30,
            "stop_loss": 0.005, "take_profit": 0.010,
            "volume_lookback": 20
        }

    def generate_signals(self, df: pd.DataFrame):
        """df: regular-session 1-min bars, DatetimeIndex = bar start time,
        columns open/high/low/close/volume. Returns (entries, exits) as
        boolean Series of signal conditions only (E1-E3, X3). Position,
        stop, target, end-of-session and daily-limit rules are applied
        in simulate()."""
        ts = df.index.tz_convert("America/New_York")

        # I1, I2 — full windows only (rolling default min_periods = window)
        fast    = df["close"].rolling(self.fast_window).mean()
        slow    = df["close"].rolling(self.slow_window).mean()
        avg_vol = df["volume"].rolling(self.volume_lookback).mean()

        # E1 / X3 — comparisons with NaN evaluate False (undefined -> false)
        cross_up   = (fast > slow) & (fast.shift(1) <= slow.shift(1))
        cross_down = (fast < slow) & (fast.shift(1) >= slow.shift(1))

        # E2
        vol_ok = df["volume"] > avg_vol

        # E3 — per-session window from that day's actual first/last bar
        day = pd.Series(ts.date, index=df.index)
        session_open  = pd.Series(ts, index=df.index).groupby(day).transform("min")
        session_close = (pd.Series(ts, index=df.index).groupby(day).transform("max")
                         + pd.Timedelta(minutes=1))
        ts_s = pd.Series(ts, index=df.index)
        time_ok = (
            (ts_s >= session_open + pd.Timedelta(minutes=self.OPEN_BUFFER_MIN)) &
            (ts_s <  session_close - pd.Timedelta(minutes=self.CLOSE_BUFFER_MIN))
        )

        entries = cross_up & vol_ok & time_ok
        exits   = cross_down
        return entries, exits

    def simulate(self, df: pd.DataFrame, init_cash: float = 100_000.0):
        """Reference bar-by-bar execution of E4, X1-X4, C1, R1, R2.
        Returns (trades DataFrame, equity Series)."""
        entries, exits = self.generate_signals(df)
        ts  = df.index.tz_convert("America/New_York")
        day = np.array(ts.date)
        last_bar_of_day = np.r_[day[1:] != day[:-1], True]

        o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
        ent, ext = entries.to_numpy(), exits.to_numpy()

        cash, shares = init_cash, 0
        entry_price = stop_level = target_level = 0.0
        entry_i = -1
        day_start_equity = init_cash
        halted = False
        trades, equity = [], np.empty(len(df))

        def sell(i, ref_price, reason):
            nonlocal cash, shares
            fill = ref_price * (1 - self.SLIPPAGE_RATE)                    # C1
            cash += fill * shares - fill * shares * self.FEE_RATE
            trades.append({
                "entry_time": df.index[entry_i], "exit_time": df.index[i],
                "shares": shares, "entry_price": entry_price, "exit_price": fill,
                "pnl": (fill - entry_price) * shares
                       - (entry_price + fill) * shares * self.FEE_RATE,
                "exit_reason": reason,
            })
            shares = 0

        for i in range(len(df)):
            if i > 0 and day[i] != day[i - 1]:                              # new session
                day_start_equity = cash + shares * c[i - 1]                 # R2
                halted = False

            if shares and i > entry_i:                                      # exits from t+1
                if l[i] <= stop_level:                                      # X1 (wins ties)
                    sell(i, min(o[i], stop_level), "stop_loss")
                elif h[i] >= target_level:                                  # X2
                    sell(i, max(o[i], target_level), "take_profit")
                elif ext[i]:                                                # X3
                    sell(i, c[i], "reverse_cross")

            eq = cash + shares * c[i]
            if not halted and eq - day_start_equity <= -self.DAILY_LOSS_LIMIT * day_start_equity:
                halted = True                                               # R2
                if shares:
                    sell(i, c[i], "daily_loss_limit")

            if shares and last_bar_of_day[i]:                               # X4
                sell(i, c[i], "end_of_session")

            if (ent[i] and not shares and not halted
                    and not last_bar_of_day[i]):                            # E4
                price = c[i] * (1 + self.SLIPPAGE_RATE)                     # C1
                eq = cash + shares * c[i]
                n = math.floor(self.POSITION_PCT * eq / price)              # R1
                if n > 0:
                    shares, entry_price, entry_i = n, price, i
                    cash -= price * n + price * n * self.FEE_RATE
                    stop_level   = entry_price * (1 - self.stop_loss)       # X1
                    target_level = entry_price * (1 + self.take_profit)     # X2

            equity[i] = cash + shares * c[i]

        return pd.DataFrame(trades), pd.Series(equity, index=df.index, name="equity")
```

---

## Backtest Results

| Version | DataSpec | fast | slow | Return | Sharpe | Max DD | Win Rate | MLflow |
|---|---|---|---|---|---|---|---|---|
| 1.0.0 | demo-bot-dataspec | 10 | 30 | 9.3% | 0.87 | 6.2% | 46.1% | abc123def456 |
| 1.1.0 | demo-bot-dataspec | 10 | 30 | -ToDo | -ToDo | -ToDo | -ToDo | -ToDo |

> The 1.0.0 result came from code that did not apply the stop loss, take profit, entry time window, end-of-session exit or daily loss limit. 1.1.0 needs a new run before it can be approved.

---

## Approval Checklist

- [x] Signal logic described in plain English
- [x] All parameters documented with types and sweep ranges
- [x] Calculation logic defined for every parameter and rule (formula IDs)
- [x] Risk rules defined
- [x] Python implementation matches spec
- [ ] Backtest run and results recorded (1.1.0)
- [ ] PR reviewed by one other team member
- [ ] `status` set to `approved`
