# Strategy: SMA Crossover

## Metadata
```yaml
name:        sma-crossover
version:     1.0.0
author:      alok-m
status:      approved
created:     2026-11-20
updated:     2026-11-20
env:         dev
tags:        [trend-following, intraday, equities, momentum]
```

---

## Description

A dual simple moving average crossover strategy targeting intraday trends on liquid large-cap ETFs. Goes long when a fast SMA crosses above a slow SMA indicating the start of an uptrend, and exits when the relationship reverses. Designed as a baseline trend-following benchmark — simple enough to validate the pipeline end-to-end before layering in complexity.

---

## Signal Logic

### Entry Conditions
- [ ] Fast SMA (default 10 bars) crosses above slow SMA (default 30 bars)
- [ ] Cross must be a fresh event — fast was at or below slow on the prior bar
- [ ] Not within the first 15 minutes of the regular trading session (09:30–09:45 ET)
- [ ] Not within the last 15 minutes of the session (15:45–16:00 ET)

### Exit Conditions
- [ ] Fast SMA crosses below slow SMA
- [ ] Hard stop loss triggered (see Parameters)
- [ ] End of session — always flat overnight

### Filters
- [ ] Volume on entry bar must be above the 20-bar average volume (confirms move)

---

## Parameters

| Parameter | Type | Default | Sweep Range | Description |
|---|---|---|---|---|
| `fast_window` | int | 10 | 5, 10, 20 | Fast SMA lookback in bars |
| `slow_window` | int | 30 | 20, 30, 50 | Slow SMA lookback in bars |
| `stop_loss` | float | 0.005 | 0.003, 0.005, 0.008 | Stop loss as fraction of entry price |
| `take_profit` | float | 0.010 | 0.008, 0.010, 0.015 | Take profit as fraction of entry price |
| `volume_lookback` | int | 20 | 10, 20 | Lookback for volume filter |

---

## Risk Rules

- **Max position size:** 10% of portfolio per trade
- **Max simultaneous positions:** 1 (single-symbol strategy)
- **Stop loss:** `stop_loss` parameter below entry price
- **Take profit:** `take_profit` parameter above entry price
- **Daily loss limit:** halt if P&L drops more than 2% of starting daily capital
- **Overnight exposure:** none — flatten all positions before session close

---

## Target Dataset

```yaml
recommended_dataspec: sma-crossover-dataspec.yaml
symbols:              [SPY]
frequency:            1Min
min_history_bars:     200
```

---

## Python Implementation

Class path: `models/sma_crossover.py`

```python
from models.base_strategy import BaseStrategy
import pandas as pd

class SMACrossover(BaseStrategy):
    name    = "sma-crossover"
    version = "1.0.0"

    def __init__(self, fast_window=10, slow_window=30,
                 stop_loss=0.005, take_profit=0.010, volume_lookback=20):
        self.fast_window    = fast_window
        self.slow_window    = slow_window
        self.stop_loss      = stop_loss
        self.take_profit    = take_profit
        self.volume_lookback = volume_lookback

    @property
    def default_params(self):
        return {
            "fast_window": 10, "slow_window": 30,
            "stop_loss": 0.005, "take_profit": 0.010,
            "volume_lookback": 20
        }

    def generate_signals(self, df: pd.DataFrame):
        fast = df["close"].rolling(self.fast_window).mean()
        slow = df["close"].rolling(self.slow_window).mean()
        avg_vol = df["volume"].rolling(self.volume_lookback).mean()

        entries = (
            (fast > slow) &
            (fast.shift(1) <= slow.shift(1)) &
            (df["volume"] > avg_vol)
        )
        exits = (fast < slow) & (fast.shift(1) >= slow.shift(1))
        return entries, exits
```

---

## Backtest Results

| DataSpec | fast | slow | Return | Sharpe | Max DD | Win Rate | MLflow |
|---|---|---|---|---|---|---|---|
| sma-crossover-dataspec | 10 | 30 | — | — | — | — | pending |

---

## Approval Checklist

- [x] Signal logic described in plain English
- [x] All parameters documented with types and sweep ranges
- [x] Risk rules defined
- [x] Python implementation matches spec
- [ ] Backtest run and results recorded
- [ ] PR reviewed by one other team member
- [x] `status` set to `approved`
