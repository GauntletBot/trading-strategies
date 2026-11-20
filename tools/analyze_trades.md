# analyze_trades.py

Grades a backtest. TradingView tells you **what happened**; `analyze_trades.py` tells you **whether it is likely to be a real edge or just luck**. It also keeps a log of every variant you try, so you can't quietly forget how many attempts it took.

- **Latest version:** [`analyze_trades.py`](analyze_trades.py) (v1). Earlier versions, when there are any, live in [`archive/`](archive/) as `analyze_trades_vN.py`.
- **Used in:** Stage 0 (benchmark) and Stage 1 (Discover) on your laptop, and as the Evaluator step in the Stage 2 backtest job on Databricks. See [QUICKSTART.md](../docs/QUICKSTART.md).
- **Requires:** Python 3.11+ and `pip install pandas numpy openpyxl tabulate`.

It only reads, calculates and reports. It never changes your trade file or places orders.

---

## Quick usage

```bash
# Grade one run and log it as an in-sample trial
python analyze_trades.py is.csv --log experiments.csv --window IS --label "don=20 htf=D/50 stop=2ATR"

# One-shot out-of-sample check against the in-sample result (doesn't add a trial)
python analyze_trades.py oos.csv --compare is.csv --log experiments.csv --window OOS --out oos-report.md

# Just look at a file, no log
python analyze_trades.py trades.csv --capital 10000
```

---

## Install as a terminal command on a Mac

These steps let you type `analyze-trades` from any folder instead of `python path/to/analyze_trades.py`. The command runs the script straight from your clone of this repo, so `git pull` keeps it on the latest version.

**1. Check Python.** You need Python 3.11 or newer:

```bash
python3 --version
```

If it's missing or older, install it with [Homebrew](https://brew.sh): `brew install python`.

**2. Clone the repo** (skip if you already have it), and note where it lives:

```bash
git clone https://github.com/GauntletBot/trading-strategies.git ~/code/trading-strategies
```

**3. Create a private Python environment** for the script's libraries, so they don't clash with anything else on your Mac:

```bash
python3 -m venv ~/.venvs/gauntlet
~/.venvs/gauntlet/bin/pip install pandas numpy openpyxl tabulate
```

**4. Create the command.** This writes a tiny launcher that runs the repo's script with that environment:

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/analyze-trades <<'EOF'
#!/bin/zsh
exec "$HOME/.venvs/gauntlet/bin/python" "$HOME/code/trading-strategies/tools/analyze_trades.py" "$@"
EOF
chmod +x ~/.local/bin/analyze-trades
```

If you cloned the repo somewhere other than `~/code/trading-strategies`, change that path in the launcher.

**5. Put the command on your PATH** (zsh is the default shell on macOS):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**6. Check it works:**

```bash
analyze-trades --help
```

You should see the usage text. From now on, run it from any folder:

```bash
cd ~/gauntlet/my-bot
analyze-trades is.csv --log experiments.csv --window IS --label "don=20 htf=D/50"
```

**7. Optional: a short alias, `at`.** To type `at` instead of `analyze-trades`:

```bash
echo "alias at='analyze-trades'" >> ~/.zshrc
source ~/.zshrc
```

Then:

```bash
at is.csv --log experiments.csv --window IS --label "don=20 htf=D/50"
```

If you skipped steps 4 and 5, point the alias at the script directly instead:

```bash
echo "alias at='\$HOME/.venvs/gauntlet/bin/python \$HOME/code/trading-strategies/tools/analyze_trades.py'" >> ~/.zshrc
source ~/.zshrc
```

> **Note:** macOS already has a built-in command called `at`, for scheduling jobs. It's off by default and rarely used, and the alias only hides it in your own terminal. If you ever need the original, run `command at` or `/usr/bin/at`. If you'd rather avoid the clash entirely, pick another short name such as `atr`.

To remove the alias, delete the `alias at=…` line from `~/.zshrc` and open a new terminal.

**Updating:** `git -C ~/code/trading-strategies pull`. The command picks up the new version automatically.

**Removing:** `rm ~/.local/bin/analyze-trades` and `rm -rf ~/.venvs/gauntlet`.

**Troubleshooting**

| Message | Fix |
|---|---|
| `command not found: analyze-trades` (or `at` does something else) | Open a new terminal window, or run `source ~/.zshrc` |
| `permission denied` | Run `chmod +x ~/.local/bin/analyze-trades` |
| `No such file or directory` pointing at `analyze_trades.py` | The repo path in the launcher is wrong; edit `~/.local/bin/analyze-trades` |
| `ModuleNotFoundError: pandas` | Re-run step 3's `pip install` |

---

## Inputs

### Required: a trade list

TradingView **Strategy Tester → List of Trades → Download**, as CSV or XLSX.

The script finds the columns it needs by name (trade number, type, date, and net P&L or profit in currency), so it works with older and newer export formats. It pairs each entry row with its exit row and drops any trade that's still open.

### Options

| Option | What it sets | Default |
|---|---|---|
| `--capital` | Starting equity, used to turn dollar profits into returns | `10000` |
| `--log` | Experiment log CSV; reads the trial count from it and appends this run | none |
| `--label` | Short description of the settings, saved in the log | blank |
| `--window` | `IS`, `OOS` or `WF-k`. In-sample and walk-forward runs add a trial; `OOS` runs don't | blank (counts as a trial) |
| `--compare` | An in-sample trade list; treats the main file as out-of-sample and compares the two | none |
| `--trials` | Overrides the trial count by hand | from `--log`, else 1 |
| `--dd-limit` | The largest drawdown you could live with, in % | `25` |
| `--iters` | Resampling rounds for bootstrap and Monte Carlo | `5000` |
| `--seed` | Random seed, so results repeat exactly | `7` |
| `--out` | Also save the report as a markdown file | prints only |

---

## Analysis, in five steps

### 1. Core statistics

It replays the trades against the starting capital to build an equity curve, then computes:

- number of trades, years covered, trades per year
- win rate, profit factor, expectancy per trade, average win and average loss
- total return, CAGR and maximum drawdown in the actual trade order
- Sharpe ratio per trade and annualised
- a t-statistic and one-sided p-value for "is the average trade really above zero?"

### 2. Bootstrap confidence ranges

It resamples your trades with replacement (5,000 times by default) to get:

- a 90% confidence range for expectancy
- a 90% confidence range for profit factor
- the probability that the true expectancy is zero or less

A profit factor of 1.6 sounds good; a range of 0.9 to 2.3 tells you it might not be.

### 3. Monte Carlo drawdown

It reshuffles the **order** of your trades (up to 3,000 times) and records the worst drawdown each time. You get the drawdown at the 50th, 90th, 95th and 99th percentiles, plus the probability of exceeding your `--dd-limit`. The single drawdown in your backtest is just one lucky or unlucky ordering; this shows the range to plan for.

### 4. Deflated Sharpe

It reads how many variants you've tried from the log and works out how high a Sharpe ratio you'd expect from **luck alone** after that many tries. Your actual Sharpe is judged against that bar, with an adjustment for skewed or fat-tailed returns (Bailey and López de Prado, 2014).

The result is a probability from 0 to 1. You want it **above 0.95**. The more variants you try, the higher the bar, which is why every run must be logged.

### 5. Stability and the out-of-sample check

- **By year:** trades, profit and win rate for each calendar year.
- **With `--compare`:** in-sample and out-of-sample results side by side, plus **walk-forward efficiency**, which is out-of-sample CAGR divided by in-sample CAGR. 0.5 or higher is respectable; below 0 means the edge vanished.

---

## Outputs

### 1. The report

Printed to the screen, and saved as markdown with `--out`. Its sections:

| Section | What it shows |
|---|---|
| **Core** | The statistics table from step 1 |
| **Is the edge real?** | Bootstrap ranges, the trial count, the luck bar and the Deflated Sharpe |
| **Monte Carlo drawdown** | The percentile table and the chance of exceeding your limit |
| **By year** | Trades, profit and win rate per year |
| **In-sample vs out-of-sample** | Only with `--compare` |
| **Verdict checklist** | Each gate ticked or not, then "N of M passed" |

The verdict ends with **"Candidate for forward (paper) testing"** if every gate passes, or **"Not yet deployable"** otherwise.

**The gates:**

- [ ] At least **100 trades** (fewer than 30 is anecdote)
- [ ] Expectancy **significant at 5%**
- [ ] Profit factor **90% lower bound above 1**
- [ ] **Deflated Sharpe above 0.95**, given the trial count
- [ ] **95th-percentile Monte Carlo drawdown** under your limit
- [ ] At least **60% of years profitable**
- [ ] Out-of-sample keeps at least **50% of in-sample CAGR** (only with `--compare`)

### 2. One new row in the experiment log

With `--log`, each run appends one row to the CSV:

| Column | Meaning |
|---|---|
| `timestamp` | When the run was graded |
| `label`, `window`, `file` | What you ran, on which window, from which export |
| `trades`, `win_rate`, `profit_factor` | Core results |
| `cagr_pct`, `max_dd_pct` | Return and drawdown |
| `sharpe_trade`, `sharpe_ann` | Sharpe per trade and annualised |
| `p_value`, `dsr` | Significance and Deflated Sharpe |
| `trials_at_time` | The trial count this run was graded against |

The log is the record of everything you tried, and it's what makes the next run's Deflated Sharpe honest. Keep it with the idea's evidence and carry it into Stage 2.

---

## Common mistakes

- **Not logging a run.** Every skipped log makes the next result look more significant than it is.
- **Logging an out-of-sample run as `IS`.** It adds a trial that shouldn't count. Use `--window OOS`.
- **Tweaking after the out-of-sample check.** The out-of-sample period is now in-sample. Say so in the label.
- **Wrong `--capital`.** Returns, CAGR and drawdown are computed against it. Match the harness's initial capital.
- **Exporting from the chart with Deep Backtesting on.** Those trades only appear in the report; export from there.
