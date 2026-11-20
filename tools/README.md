# Tools

Shared tools for Stages 0 and 1 of the gauntlet. See [docs/QUICKSTART.md](../docs/QUICKSTART.md) for how to use them.

| File | What it is | Where it runs |
|---|---|---|
| [`harness.pine`](harness.pine) | TradingView strategy harness (currently v2): vault lock, test windows, risk-based sizing, run card | TradingView: paste into the Pine Editor, save as a private script |
| [`analyze_trades.py`](analyze_trades.py) | Grades a TradingView trade list: bootstrap, Monte Carlo drawdown, Deflated Sharpe, gate checklist, experiment log. Full guide: [analyze_trades.md](analyze_trades.md) | Your laptop, as the `gat` command ([setup](analyze_trades.md#install-as-a-terminal-command-on-a-mac)) |

## Versioning

- The plain file name is **always the latest version**: `harness.pine`, `analyze_trades.py`.
- When a tool changes in a way that alters results, copy the current file to `archive/` with its version number first, then update the plain file and bump the version in its header comment.
  - `archive/harness_v1.pine`, `archive/harness_v2.pine`, …
  - `archive/analyze_trades_v1.py`, `archive/analyze_trades_v2.py`, …
- Record the version you used in each run's label or run card, so old results can be reproduced with the matching archived file.

| Tool | Latest | Archived |
|---|---|---|
| harness.pine | v2 (adds the vault lock) | [v1](archive/harness_v1.pine) |
| analyze_trades.py | v1 | — |
