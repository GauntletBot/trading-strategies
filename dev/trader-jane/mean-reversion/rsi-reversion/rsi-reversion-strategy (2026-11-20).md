# Strategy: RSI Reversion

## Metadata
```yaml
name:        rsi-reversion
version:     1.0.0
author:      trader-jane
status:      approved
created:     2026-11-20
updated:     2026-11-20
env:         dev
tags:        [mean-reversion, intraday, equities, oscillator]
```

---

## Description

An intraday mean-reversion strategy using the Relative Strength Index (RSI) to identify short-term overbought and oversold conditions on liquid ETFs. Enters long when RSI dips into oversold territory and prices are likely to snap back toward the mean. Pairs well with a VWAP anchor to avoid trading against the dominant intraday trend.

---

## Signal Logic

### Entry Conditions
- [ ] RSI (14-period) falls below oversold threshold (default 30)
- [ ] Close price is above VWAP — only trade in the direction of the intraday trend
- [ ] Not in the first or last 15 minutes of the trading session

### Exit Conditions
- [ ] RSI rises above exit threshold (default 55) — mean reversion complete
- [ ] Hard stop loss triggered
- [ ] End of session — flatten all positions

### Filters
- [ ] Avoid entries if the 1-hour RSI is also below 30 (deeply oversold may continue lower)

---

## Parameters

| Parameter | Type | Default | Sweep Range | Description |
|---|---|---|---|---|
| `rsi_period` | int | 14 | 9, 14, 21 | RSI lookback in bars |
| `oversold_threshold` | float | 30 | 25, 30, 35 | RSI level to trigger entry |
| `exit_threshold` | float | 55 | 50, 55, 60 | RSI level to trigger exit |
| `stop_loss` | float | 0.006 | 0.004, 0.006, 0.010 | Stop loss fraction of entry |
| `vwap_filter` | bool | true | true, false | Only enter when price > VWAP |

---

## Risk Rules

- **Max position size:** 8% of portfolio per trade
- **Max simultaneous positions:** 2
- **Stop loss:** `stop_loss` parameter below entry
- **Daily loss limit:** halt if daily P&L drops 2.5%
- **Overnight exposure:** none

---

## Target Dataset

```yaml
recommended_dataspec: rsi-reversion-dataspec.yaml
symbols:              [QQQ]
frequency:            1Min
min_history_bars:     250
```

---

## Python Implementation

Class path: `models/rsi_reversion.py`

```python
from models.base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class RSIReversion(BaseStrategy):
    name    = "rsi-reversion"
    version = "1.0.0"

    def __init__(self, rsi_period=14, oversold_threshold=30,
                 exit_threshold=55, stop_loss=0.006, vwap_filter=True):
        self.rsi_period          = rsi_period
        self.oversold_threshold  = oversold_threshold
        self.exit_threshold      = exit_threshold
        self.stop_loss           = stop_loss
        self.vwap_filter         = vwap_filter

    @property
    def default_params(self):
        return {
            "rsi_period": 14, "oversold_threshold": 30,
            "exit_threshold": 55, "stop_loss": 0.006, "vwap_filter": True
        }

    def _rsi(self, close: pd.Series) -> pd.Series:
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(self.rsi_period).mean()
        loss  = (-delta.clip(upper=0)).rolling(self.rsi_period).mean()
        rs    = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signals(self, df: pd.DataFrame):
        rsi  = self._rsi(df["close"])
        vwap = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()

        entries = rsi < self.oversold_threshold
        if self.vwap_filter:
            entries = entries & (df["close"] > vwap)

        exits = rsi > self.exit_threshold
        return entries, exits
```

---

## Backtest Results

| DataSpec | rsi_period | oversold | exit | Return | Sharpe | Max DD | MLflow |
|---|---|---|---|---|---|---|---|
| rsi-reversion-dataspec | 14 | 30 | 55 | — | — | — | pending |

---

## Approval Checklist

- [x] Signal logic described in plain English
- [x] All parameters documented with types and sweep ranges
- [x] Risk rules defined
- [x] Python implementation matches spec
- [ ] Backtest run and results recorded
- [ ] PR reviewed
- [x] `status` set to `approved`
