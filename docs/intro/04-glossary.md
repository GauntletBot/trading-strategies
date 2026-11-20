# 4. Glossary

[← 3. Getting Started](03-getting-started.md) · [Intro index](README.md)

---

Terms are grouped by topic, then listed alphabetically within each group.

**Jump to:** [Gauntlet process](#gauntlet-process) · [Repo and files](#repo-and-files) · [Trading basics](#trading-basics) · [Strategy mechanics](#strategy-mechanics) · [Metrics](#metrics) · [Validation and statistics](#validation-and-statistics) · [Tools and platforms](#tools-and-platforms)

---

## Gauntlet process

| Term | Meaning |
|---|---|
| **Burned vault** | A vault with no unopened holdback set left, so it can no longer give a clean test. Paper trading becomes the only clean test left for that idea. |
| **Candidate spec** | The output of Stage 1: the rules in plain language, parameter ranges, the hypothesis and the TradingView trade list. |
| **Development period** | The older part of price history (about 80%). All exploration and tuning happens here. |
| **Embargo gap** | A buffer of time before each holdback set, at least as long as the model's longest lookback. It stops information leaking from training data into the set being tested. |
| **Fine-tuning round** | Retraining a model after a holdback set has been opened, with that set added to the training data, then freezing a new version for the next set. Each round counts toward the trial count. |
| **Frozen model** | A model that can no longer change: a specific code version plus its config, parameters and cost assumptions. Only a frozen model may be tested on a holdback set. |
| **Gate** | A pass/fail check a strategy must clear before moving to the next stage. |
| **Gauntlet** | The whole system: a series of stages every trading idea must pass before risking real money. |
| **Holdback set** | One slice of the vault, such as H1 or H2. Sets are fixed before Stage 1, opened oldest first, and each tests one frozen model once. |
| **Hypothesis** | One sentence saying why an edge should exist and who is on the other side of the trade. |
| **Iteration** | One trip through the stages, ending in a Stage 4 decision. |
| **Paper trading** | Trading with fake money on live market data, through Alpaca's paper account. Runs for 1–3 months. |
| **Promote / revise / retire** | The Stage 4 decisions: move the model toward live trading, send it back to Stage 2 (which counts as new trials), or stop working on it. |
| **Scorecard** | The Stage 4 summary that puts results from each stage side by side, showing where the edge shrank. |
| **Stage 0 — Quick backtest** | Runs the idea exactly as written, with no tuning, on Alpaca data in Python. Its gate (still a proposal) is enough trades and positive expectancy after costs. |
| **Stage 1 — Discover** | Fast exploration in TradingView to find ideas worth building properly. |
| **Stage 2 — Port and tune** | Rebuild the idea in Python, check it matches TradingView, then tune it with walk-forward testing. |
| **Stage 3 — Vault test** | A single run of a frozen model on the next unopened holdback set. |
| **Stage 4 — Evaluate** | Review the scorecard and decide what happens next. |
| **Vault** | The newest 20% of price history, locked before any exploration. Either one holdback set or several, each opened once. |

## Repo and files

| Term | Meaning |
|---|---|
| **Acceptance criteria** | The numeric thresholds in a story that every run must meet for the story to pass. |
| **Actual results** | The metrics a backtest really produced, copied into the run file after it runs. |
| **Bot** | A strategy plus its data and runtime settings. In the repo, a bot is a folder. |
| **Bot folder** | The leaf folder that holds a bot's files. Its name is the prefix of every file inside it. |
| **Bot ops doc (`bot.md`)** | Required file describing how the bot runs: environment, execution mode, capital, Databricks job, monitoring, known issues and change log. |
| **Calculation logic** | The section of a strategy file that gives the exact formula for every indicator, signal, fill, cost and risk limit. |
| **Category folder** | A free-form folder between your username and a bot folder, such as `momentum-bots/`. Can be nested. |
| **CI (continuous integration)** | Automatic checks that run on every pull request. Here: the **Validate Bot Files** workflow. |
| **DataSpec (`dataspec.yaml`)** | Required file declaring the data a bot uses: symbols, dates, bar frequency, source and feed. |
| **Environment** | Where a bot sits in the repo: `dev/` (personal sandbox), `staging/` (team review) or `prod/` (paper and live). |
| **Expected results** | Numeric targets written in a run file *before* the backtest runs. |
| **Promotion** | Moving a bot folder from `dev/` to `staging/` to `prod/` with a pull request. |
| **Pull request (PR)** | A request to merge your branch into `main`. CI runs on it. |
| **Run file (`run.md`)** | Optional file recording one backtest: inputs, parameters, expected results, actual results and observations. Named `{bot}-run (YYYY-MM-DD-NNN).md`. |
| **Story (`story.md`)** | Optional file stating a hypothesis and its acceptance criteria, and linking the runs that test it. Status: `open`, `passing`, `failing` or `abandoned`. |
| **Strategy file (`strategy.md`)** | Required file specifying the strategy: description, signal logic, parameters, calculation logic, risk rules, Python class and approval checklist. The date in its filename is the last logic change. |
| **TDD (test-driven development)** | Writing the test first. Here: expected results are committed before the backtest runs. |
| **`-ToDo`** | Placeholder text in templates. CI fails if it remains in expected results, or in actual results once a run is `completed`. |

## Trading basics

| Term | Meaning |
|---|---|
| **Bar (candle)** | Price activity over a fixed interval, such as 1 minute or 1 day. |
| **Equity** | Account value: cash plus the current value of open positions. |
| **ETF** | Exchange-traded fund, such as SPY, which tracks the S&P 500. |
| **Fee (commission)** | What the broker or exchange charges per trade. |
| **Fill** | The price and quantity at which an order actually executed. |
| **Intraday** | Opening and closing positions within the same trading day. |
| **Long / short** | Long profits when price rises; short profits when price falls. |
| **OHLCV** | Open, high, low, close and volume: the five values in each bar. |
| **Position** | Shares currently held. |
| **Regular session** | The main US stock-market hours: 09:30–16:00 Eastern Time. |
| **Slippage** | The difference between the price you expected and the price you got. |
| **Symbol (ticker)** | The code for a tradable instrument, such as `SPY`. |

## Strategy mechanics

| Term | Meaning |
|---|---|
| **ATR (average true range)** | A measure of how much price typically moves per bar. Often used to size positions and set stops. |
| **Crossover** | When one line crosses another, such as a fast moving average crossing above a slow one. |
| **Daily loss limit** | A rule that stops trading for the day once losses reach a set percentage. |
| **Drawdown circuit breaker (kill switch)** | A rule that halts a bot when losses from its peak reach a set level. |
| **Entry / exit** | Opening and closing a position. |
| **Lookback** | How many past bars an indicator uses. |
| **Parameter** | A tunable setting, such as a moving-average length or a stop distance. |
| **Parameter sweep** | Running a backtest for each combination of parameter values in a range. |
| **Position sizing** | Deciding how many shares to buy, for example 10% of equity per trade. |
| **Regime filter** | A rule that only allows trades in certain market conditions, such as trending or high volatility. |
| **Signal** | The condition that tells a strategy to enter or exit. |
| **SMA (simple moving average)** | The average closing price over the last *n* bars. |
| **Stop loss** | An exit that limits the loss on a trade, placed a set distance below the entry price. |
| **Take profit** | An exit that locks in gains, placed a set distance above the entry price. |
| **Volume filter** | A rule that only allows entries when volume is above its recent average. |

## Metrics

| Term | Meaning |
|---|---|
| **CAGR** | Compound annual growth rate: the steady yearly return that would produce the same total result. |
| **Equity curve** | A chart of account equity over time. |
| **Expectancy** | Average profit or loss per trade. |
| **Max drawdown** | The largest fall from an equity peak to a later low, as a percentage. Gauntlet's gate allows at most 25%. |
| **Profit factor (PF)** | Gross profit divided by gross loss. Above 1 means the strategy made money. |
| **Sharpe ratio** | Return per unit of volatility. Higher is better; above about 1 is good for a single strategy. |
| **Total return** | The percentage change in equity from start to end. |
| **Trade count** | How many completed trades a backtest produced. Gauntlet wants at least 100; fewer than 30 proves nothing. |
| **Win rate** | The share of trades that made money. A low win rate can still be profitable if winners are much bigger than losers. |

## Validation and statistics

| Term | Meaning |
|---|---|
| **Backtest** | Simulating a strategy on historical data to see how it would have performed. |
| **Bootstrap confidence interval** | A range for a metric, found by resampling the trades many times. If a profit factor's lower bound is above 1, the edge is less likely to be luck. |
| **Deflated Sharpe ratio** | A Sharpe ratio adjusted for how many variants were tried. Gauntlet requires above 0.95. |
| **In-sample / out-of-sample** | Data used for tuning versus data held back for testing. |
| **Look-ahead bias** | Accidentally using information that wasn't available at the time, such as a bar's close before that bar finished. |
| **Monte Carlo drawdown** | The range of drawdowns found by reshuffling the trade order many times. Gauntlet uses the 95th percentile. |
| **Overfitting** | Tuning a strategy so closely to past data that it captures noise rather than a real edge. |
| **Parity check** | Confirming the Python version produces the same trades as the TradingView version. |
| **Plateau** | A range of neighbouring parameter values that all work. A sign of a real effect, unlike a single sharp peak. |
| **PBO (probability of backtest overfitting)** | An estimate of how likely the best-looking model is only the luckiest of many. |
| **Repainting** | When a TradingView indicator changes its past values after the fact, making backtests look better than reality. |
| **Stress test** | Rerunning with harsher assumptions: costs doubled, related symbols, a neighbouring bar size. |
| **Survivorship bias** | Testing only on assets that still exist today, which hides the ones that failed. |
| **Trial count** | How many variants were tried for an idea, across every stage. It raises the bar for the Deflated Sharpe gate. |
| **Walk-forward testing** | Tune on one window, test on the next, slide forward and repeat. Then judge the combined test windows. |
| **Walk-forward efficiency** | Test-period performance divided by tuning-period performance. Gauntlet requires at least 0.5. |

## Tools and platforms

| Term | Meaning |
|---|---|
| **Alpaca** | Broker and market-data provider. Supplies historical prices, paper trading and live trading. |
| **Catalog / schema** | Databricks folders for tables. Gauntlet uses catalog `gauntlet` and schema `gauntlet_bot_demo`. |
| **Databricks** | Cloud data platform that stores Gauntlet's market data and runs its backtest jobs. |
| **Delta table** | Databricks' table format for storing data such as price bars. |
| **Execution bridge** | A small service between a signal and the broker. It checks a shared secret, removes duplicate alerts, sizes from the live balance and logs every order. |
| **GitHub Actions** | GitHub's automation service. It runs the CI checks. |
| **IEX / SIP** | Data feeds. SIP covers all US exchanges. IEX is one exchange, and is what Alpaca's free plan streams live. |
| **MLflow** | Experiment tracker on Databricks. Stores each run's metrics, equity curve and trade log. |
| **Pine Script** | TradingView's programming language for indicators and strategies. |
| **TradingView** | Charting platform used for Stage 1 exploration. |
| **Unity Catalog** | Databricks' governance layer that organises catalogs, schemas and tables. |
| **vectorbt** | Python backtesting library used by the Databricks backtest job. |
| **Webhook** | A web request one system sends another when something happens, such as a TradingView alert firing. |

---

[← 3. Getting Started](03-getting-started.md) · [Intro index](README.md)
