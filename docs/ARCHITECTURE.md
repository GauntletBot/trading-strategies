# Information Architecture

## Docs

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | This file — folder hierarchy, file roles, TDD workflow, promotion path, CI checks |
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | Naming rules, valid/invalid examples, and update guidance for all 5 file types |
| [RUN_TEMPLATE.md](RUN_TEMPLATE.md) | Copy-paste template for a new run file |
| [STORY_TEMPLATE.md](STORY_TEMPLATE.md) | Copy-paste template for a new story file |

---

## Design Principles

1. **User-owned trees** — each user owns their subtree under `dev/{username}/`. No one else merges into it.
2. **Bot as a folder** — a bot is a folder containing the three required files plus any run and story files accumulated over time.
3. **Three required, two optional** — every bot must have strategy, dataspec, and bot. Run and story files are added as backtesting progresses. CI enforces the required three.
4. **Date in the strategy filename** — carries the last-updated date, making the current version visible in a directory listing without opening the file.
5. **Date and sequence in run filenames** — `(YYYY-MM-DD-NNN)` makes runs sortable and allows multiple runs per day.
6. **Free-form category tree** — users can nest category folders as deeply as needed between their username folder and the bot folder. The bot folder is always a leaf node.
7. **TDD via run and story files** — expected results are written before execution. CI enforces this. Stories link runs into named hypotheses with explicit pass/fail criteria.
8. **Env promotion via PRs** — moving a bot from `dev/` → `staging/` → `prod/` is a PR. Reviewers see the diff; approvals are logged.

---

## Folder Hierarchy

```
{env}/
└── {username}/                       # GitHub username — lowercase
    └── {category}/                   # Free-form — can be nested N levels deep
        └── {category}/               # e.g. momentum-bots/large-cap/
            └── {bot-name}/           # Leaf node — contains all 5 file types
                ├── {bot-name}-strategy (YYYY-MM-DD).md    ← required
                ├── {bot-name}-dataspec.yaml                ← required
                ├── {bot-name}-bot.md                       ← required
                ├── {bot-name}-run (YYYY-MM-DD-NNN).md     ← optional, repeatable
                └── {bot-name}-story-{name}.md              ← optional, repeatable
```

**Bot folder** is always a leaf — no bot folders inside other bot folders.  
**Category folders** are free-form — users design their own taxonomy.  
**Run and story files** accumulate over time in the same bot folder — there is no limit on how many a bot can have.

### Example Tree (mature bot)

```
dev/
└── alok-m/
    └── momentum-bots/
        └── sma-crossover/
            ├── sma-crossover-strategy (2026-11-20).md       ← current strategy
            ├── sma-crossover-dataspec.yaml                   ← dataset definition
            ├── sma-crossover-bot.md                          ← ops document
            ├── sma-crossover-run (2026-11-20-001).md        ← baseline run
            ├── sma-crossover-run (2026-11-20-002).md        ← param sweep run
            ├── sma-crossover-run (2026-11-25-001).md        ← after strategy tweak
            └── sma-crossover-story-baseline-2023.md         ← baseline hypothesis
```

### Example Tree (multiple users)

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

### `{bot-name}-strategy (YYYY-MM-DD).md` — Required

The **specification** for the trading strategy. Human-readable, PR-reviewable.  
Contains: signal logic in plain English, parameters with types and sweep ranges, risk rules, entry/exit conditions, Python class reference, backtest results table, and an approval checklist.  
The date in the filename is updated on every logic change — rename the file and update the `updated:` field inside together in one commit.

### `{bot-name}-dataspec.yaml` — Required

The **dataset definition** for running this bot. Machine-parseable YAML.  
Contains: symbols, date range, frequency, data feed (SIP/IEX/Polygon), and data quality rules.  
Used by the ingestion pipeline to fetch and register historical data in Databricks Delta Lake. Versioned via the `version:` field inside the file — not the filename.

### `{bot-name}-bot.md` — Required

The **Bot Operations Document**. Runtime-focused.  
Contains: deployment environment, execution mode, scheduler config, capital allocation, monitoring and alerting setup, known issues, and incident log.  
Tells the ops team how to run, monitor, and troubleshoot this bot. Updated in-place; git history tracks changes.

### `{bot-name}-run (YYYY-MM-DD-NNN).md` — Optional, Repeatable

The **backtest execution record** for a single run of this bot.  
Links to the specific strategy file and dataspec used. Contains two result tables: **Expected Results** (written before executing — the TDD contract) and **Actual Results** (filled after executing).  
`NNN` is a zero-padded sequence: `001`, `002`, … — allows multiple runs on the same day.  
Status lifecycle: `expected` → `completed` or `failed`.

### `{bot-name}-story-{name}.md` — Optional, Repeatable

The **named hypothesis** linking one or more run documents.  
Declares a falsifiable claim and acceptance criteria before any run executes. References run files by name. Tracks whether the hypothesis is supported by the evidence across runs.  
Status lifecycle: `open` → `passing` or `failing`.  
Story name is lowercase-hyphen: `baseline-2023`, `high-vol-regime`, `param-sweep-fast-window`.

---

## TDD Workflow

Run and story files together enforce test-driven development of backtests:

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. Write story                                                      │
│     Define hypothesis + acceptance criteria                          │
│     status: open                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. Create run file                                                  │
│     Fill Expected Results — numeric targets for each metric         │
│     status: expected                                                 │
│     CI enforces: no -ToDo values in Expected Results                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. Execute backtest on Databricks                                   │
│     Triggered by GitHub Actions on merge                             │
│     Results logged to MLflow                                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. Fill Actual Results                                              │
│     Update run file with real metrics                                │
│     Set status: completed or failed                                  │
│     CI enforces: no -ToDo remaining when status = completed          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. Update story                                                     │
│     Check actual results against acceptance criteria                 │
│     Set status: passing or failing                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Promotion Path

```
dev/{user}/{category}/{bot}/   →   staging/{user}/{category}/{bot}/   →   prod/{user}/{category}/{bot}/
        ↑                                      ↑                                       ↑
  Author self-merges               1 team approval required              2 approvals + CI pass required
  CI validates files               Databricks backtest must pass         Paper trade results attached
  Run + story files travel         Story must be passing                 All stories must be passing
  with the bot on promotion
```

Run and story files move with the bot when it is promoted — they are part of the bot's evidence record.

---

## CI Checks (run on every PR)

### Per changed bot folder
- All three required files present (`strategy`, `dataspec`, `bot`)
- Strategy filename matches `{bot-name}-strategy (YYYY-MM-DD).md` pattern with valid date
- DataSpec YAML parses cleanly and all required fields are present and valid
- `bot.md` contains all required sections and a change log entry
- Bot folder name matches the prefix in all five file types
- No sub-folders inside a bot folder

### Per run file (if present)
- Filename matches `{bot-name}-run (YYYY-MM-DD-NNN).md` pattern
- Metadata block present with all required fields
- Expected Results table has at least one row with numeric targets (no `-ToDo`)
- If `status: completed` — Actual Results contains no `-ToDo` values

### Repo-wide naming check
- All folder names are lowercase letters, numbers, and hyphens only
- Every leaf folder (bot folder) has the three required files
- Run and story filenames follow the correct patterns
- No bot folder nested inside another bot folder
