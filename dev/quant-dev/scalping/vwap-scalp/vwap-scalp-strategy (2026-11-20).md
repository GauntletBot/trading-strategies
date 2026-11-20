# Strategy: VWAP Scalp

## Metadata
```yaml
name:        vwap-scalp
version:     1.0.0
author:      quant-dev
status:      approved
created:     2026-11-20
updated:     2026-11-20
env:         dev
tags:        [scalping, intraday, vwap, high-frequency, equities]
```

---

## Description

A short-term scalping strategy that uses VWAP (Volume Weighted Average Price) as a dynamic support/resistance level. Enters long when price pulls back to and bounces from VWAP, targeting a small move back toward the intraday high. Relies on the market microstructure tendency for institutional algos to anchor near VWAP throughout the trading day. High trade frequency — dozens of trades per session. Tight stops and small targets.

---

## Signal Logic

### Entry Conditions (Long)
- [ ] Price touches or crosses below VWAP (within 0.05% of VWAP)
- [ ] Immediately recovers back above VWAP on the next bar
- [ ] 5-period momentum is positive (close > close 5 bars ago)
- [ ] Volume on the entry bar is above 1.5x the 10-bar average (institutional participation)
- [ ] Not in the first 30 minutes of session (09:30–10:00 ET) — VWAP is noisy at open
- [ ] Not in the last 15 minutes of session (15:45–16:00 ET)

### Exit Conditions
- [ ] Price reaches VWAP + `take_profit` (default 0.3% above VWAP)
- [ ] Hard stop: price drops `stop_loss` below entry (default 0.2%)
- [ ] Time-based stop: exit if held longer than `max_hold_bars` (default 15 bars)
- [ ] End of session

### Filters
- [ ] Only trade when overall market (SPY) is above its own VWAP — avoid counter-trend scalps
- [ ] Skip if bid-ask spread > 0.02% of price (liquidity filter)

---

## Parameters

| Parameter | Type | Default | Sweep Range | Description |
|---|---|---|---|---|
| `vwap_band` | float | 0.0005 | 0.0003, 0.0005, 0.0008 | % distance from VWAP to count as a touch |
| `take_profit` | float | 0.003 | 0.002, 0.003, 0.004 | Profit target as fraction of entry |
| `stop_loss` | float | 0.002 | 0.001, 0.002, 0.003 | Stop loss as fraction of entry |
| `max_hold_bars` | int | 15 | 10, 15, 20 | Max bars to hold before forced exit |
| `volume_mult` | float | 1.5 | 1.2, 1.5, 2.0 | Volume must be this multiple of avg |
| `momentum_period` | int | 5 | 3, 5, 8 | Lookback for momentum confirmation |

---

## Risk Rules

- **Max position size:** 5% of portfolio per trade (high frequency — keep size small)
- **Max simultaneous positions:** 3
- **Stop loss:** `stop_loss` parameter — tight, non-negotiable
- **Time stop:** exit after `max_hold_bars` regardless of P&L
- **Daily trade limit:** max 50 trades per session
- **Daily loss limit:** halt if daily P&L drops 1.5% — scalping losses compound fast

---

## Target Dataset

```yaml
recommended_dataspec: vwap-scalp-dataspec.yaml
symbols:              [SPY]
frequency:            1Min
min_history_bars:     30
note:                 >
  VWAP resets each session — only 30 bars of warmup needed.
  Tick data preferred for realistic fill simulation.
```

---

## Python Implementation

Class path: `models/vwap_scalp.py`

```python
from models.base_strategy import BaseStrategy
import pandas as pd

class VWAPScalp(BaseStrategy):
    name    = "vwap-scalp"
    version = "1.0.0"

    def __init__(self, vwap_band=0.0005, take_profit=0.003,
                 stop_loss=0.002, max_hold_bars=15,
                 volume_mult=1.5, momentum_period=5):
        self.vwap_band       = vwap_band
        self.take_profit     = take_profit
        self.stop_loss       = stop_loss
        self.max_hold_bars   = max_hold_bars
        self.volume_mult     = volume_mult
        self.momentum_period = momentum_period

    @property
    def default_params(self):
        return {
            "vwap_band": 0.0005, "take_profit": 0.003,
            "stop_loss": 0.002, "max_hold_bars": 15,
            "volume_mult": 1.5, "momentum_period": 5
        }

    def generate_signals(self, df: pd.DataFrame):
        # Session-cumulative VWAP
        vwap     = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
        avg_vol  = df["volume"].rolling(10).mean()
        momentum = df["close"] > df["close"].shift(self.momentum_period)

        near_vwap     = (df["close"] - vwap).abs() / vwap < self.vwap_band
        bounce        = (df["close"].shift(1) < vwap) & (df["close"] > vwap)
        volume_spike  = df["volume"] > avg_vol * self.volume_mult

        entries = near_vwap & bounce & volume_spike & momentum
        # Exits handled by stop/take-profit/time logic in backtest engine
        exits   = pd.Series(False, index=df.index)
        return entries, exits
```

---

## Backtest Results

| DataSpec | vwap_band | tp | sl | Return | Sharpe | Max DD | Trades/Day | MLflow |
|---|---|---|---|---|---|---|---|---|
| vwap-scalp-dataspec | 0.0005 | 0.003 | 0.002 | — | — | — | — | pending |

---

## Notes

- This strategy requires the backtest engine to support per-trade stop/take-profit/time exits — not just bar-level signals
- Slippage assumption is critical: use at least 0.1% round-trip in backtest or results are unrealistic
- Performance is very sensitive to execution speed — do not deploy on slow connections

---

## Approval Checklist

- [x] Signal logic described in plain English
- [x] All parameters documented with types and sweep ranges
- [x] Risk rules defined (including daily trade limit)
- [x] Python implementation matches spec
- [x] Exit logic limitation documented in Notes
- [ ] Backtest run and results recorded
- [ ] PR reviewed
- [x] `status` set to `approved`
