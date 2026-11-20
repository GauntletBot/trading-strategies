# Information Architecture

## Design Principles

1. **User-owned trees** — each user owns their subtree under `dev/{username}/`. No one else merges into it.
2. **Bot as a folder** — a bot is not a single file; it is a folder containing the three required files plus any supporting assets.
3. **Three files, one bot** — every bot must have all three: strategy, dataspec, and bod. CI enforces this.
4. **Date in the strategy filename** — the strategy filename carries the last-updated date, making the most recent version visible in a directory listing without opening the file.
5. **Free-form category tree** — users can create as many nested category folders as they need between their username folder and the bot folder. The bot folder is always a leaf node.
6. **Env promotion via PRs** — moving a bot from `dev/` → `staging/` → `prod/` is a PR. Reviewers see the diff; approvals are logged.

---

## Folder Hierarchy

```
{env}/
└── {username}/                     # GitHub username — lowercase
    └── {category}/                 # Free-form — can be nested N levels deep
        └── {category}/             # e.g. momentum-bots/large-cap/
            └── {bot-name}/         # Leaf node — always contains the 3 files
                ├── {bot-name}-strategy (YYYY-MM-DD).md
                ├── {bot-name}-dataspec.yaml
                └── {bot-name}-bod.md
```

**Bot folder** is always a leaf — no bot folders inside other bot folders.  
**Category folders** are free-form — users design their own taxonomy.

### Example Trees

```
dev/
├── alok-m/
│   ├── momentum-bots/
│   │   ├── large-cap/
│   │   │   └── sma-crossover/        ← bot
│   │   └── small-cap/
│   │       └── breakout-momentum/    ← bot
│   └── options/
│       └── covered-call-wheel/       ← bot
│
├── trader-jane/
│   └── mean-reversion/
│       ├── rsi-reversion/            ← bot
│       └── bollinger-squeeze/        ← bot
│
└── quant-dev/
    ├── scalping/
    │   └── vwap-scalp/               ← bot
    └── arbitrage/
        └── etf-arb/                  ← bot
```

---

## File Roles

### `{bot-name}-strategy (YYYY-MM-DD).md`

The **specification** for the trading strategy. Human-readable, PR-reviewable.  
Contains: signal logic, parameters with ranges, risk rules, entry/exit conditions, Python class reference, and an approval checklist.  
The date in the filename is updated on every logic change, making the last-modified date visible at a glance.

### `{bot-name}-dataspec.yaml`

The **dataset definition** for running this bot. Machine-parseable YAML.  
Contains: symbols, date range, frequency, data feed (SIP/IEX/Polygon), quality rules.  
Used by the ingestion pipeline to fetch and register historical data in Databricks Delta Lake.

### `{bot-name}-bod.md`

The **Bot Operations Document**. Runtime-focused.  
Contains: deployment environment, scheduler config, capital allocation, monitoring/alerting setup, known issues, incident log.  
Tells the ops team how to run, monitor, and troubleshoot this bot.

---

## Promotion Path

```
dev/{user}/{category}/{bot}/   →   staging/{user}/{category}/{bot}/   →   prod/{user}/{category}/{bot}/
        ↑                                      ↑                                       ↑
  Author self-merges               1 team approval required              2 approvals + CI pass required
  CI validates files               Databricks backtest must pass         Paper trade results attached
```

---

## CI Checks (run on every PR)

- All three files present in every bot folder
- Strategy filename matches `{bot-name}-strategy (YYYY-MM-DD).md` pattern
- DataSpec YAML parses cleanly and contains all required fields
- BOD contains the required sections
- Bot folder name matches the prefix in all three filenames
