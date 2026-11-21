# GauntletBot — Trading Strategy Repository

This repository is the source of truth for all trading bot strategies and historical data specifications managed under the GauntletBot organization.

## Quick Start

**First idea?** Follow **[docs/QUICKSTART.md](docs/QUICKSTART.md)**: test it in TradingView (Stage 0 benchmark, then Stage 1 Discover) and hand off a candidate, in an afternoon.

Then, for each bot:

1. Create a folder under `dev/` with your GitHub username
2. Add a subfolder for each strategy category you work on
3. For each bot, create a folder with the three required files
4. Add run and story files as you backtest and iterate
5. Open a PR — CI validates all files before merge

See the [Docs](#docs) section below for links to all reference documents.

New here? Start with the **[Gauntlet — Introduction for Beginners slide deck](https://drive.google.com/drive/folders/1LKs8QqLk9bggxP_k-VIWt-hlOmJST0SS)** in the shared Gauntlet folder on Google Drive (anyone with the link can view).

---

## Environments

| Folder | Purpose | Who merges |
|---|---|---|
| `dev/` | Individual development — personal sandboxes | Author self-merges |
| `staging/` | Shared review — strategies under team evaluation | Requires 1 approval |
| `prod/` | Live strategies running on paper/live accounts | Requires 2 approvals + CI pass |

---

## Five File Types per Bot

### Required (every bot must have all three)

| File | Purpose |
|---|---|
| `{bot-name}-strategy (YYYY-MM-DD).md` | Signal logic, parameters, risk rules, approval checklist. Date in filename updates on every logic change. |
| `{bot-name}-dataspec.yaml` | Historical dataset definition — symbols, period, frequency, feed. |
| `{bot-name}-bot.md` | Bot Operations Document — runtime config, deployment notes, monitoring, incident log. |

### Optional (added as you run and iterate)

| File | Purpose |
|---|---|
| `{bot-name}-run (YYYY-MM-DD-NNN).md` | Records one backtest execution. Write expected results **before** running (TDD contract), fill actuals after. `NNN` sequences multiple runs per day: `001`, `002`, … |
| `{bot-name}-story-{name}.md` | A named hypothesis linking one or more run documents. Declares acceptance criteria before any run executes. Status: `open` → `passing` or `failing`. |

### TDD Workflow

```
1. Write story — state your hypothesis and acceptance criteria
         ↓
2. Create a run file — set Expected Results before executing
         ↓
3. CI validates: expected values must be filled (not -ToDo)
         ↓
4. Execute the backtest on Databricks
         ↓
5. Fill Actual Results, set status: completed
         ↓
6. CI validates: no -ToDo remaining in actuals
         ↓
7. Update story status: passing or failing
```

---

## Docs

| Document | Purpose |
|---|---|
| [Intro slide deck (Google Drive)](https://drive.google.com/drive/folders/1LKs8QqLk9bggxP_k-VIWt-hlOmJST0SS) | The same intro as slides. The newest copy is named `Gauntlet — Introduction for Beginners last (YYYY-MM-DD)`; older copies are numbered 0, 1, 2… |
| [QUICKSTART.md](docs/QUICKSTART.md) | From idea to candidate in TradingView: Stage 0 benchmark, Stage 1 Discover, hand-off to Stage 2 |
| [Intro for beginners](docs/intro/README.md) | Start here: overview, architecture and data flows, getting started step by step, glossary |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Folder hierarchy, file roles, TDD workflow, promotion path, CI checks |
| [NAMING_CONVENTION.md](docs/NAMING_CONVENTION.md) | Naming rules, valid/invalid examples, and update guidance for all 5 file types |
| [STRATEGY_GUIDE.md](docs/STRATEGY_GUIDE.md) | Every section of a strategy file, how each parameter is calculated, the Search Space section and its genetic-algorithm encoding |
| [RUN_TEMPLATE.md](docs/RUN_TEMPLATE.md) | Copy-paste template for a new run file |
| [STORY_TEMPLATE.md](docs/STORY_TEMPLATE.md) | Copy-paste template for a new story file |

---

## Repository Structure

```
trading-strategies/
├── README.md
├── docs/
│   ├── QUICKSTART.md               ← idea to candidate in TradingView
│   ├── ARCHITECTURE.md             ← folder hierarchy, file roles, TDD workflow
│   ├── NAMING_CONVENTION.md        ← naming rules for all 5 file types
│   ├── STRATEGY_GUIDE.md           ← strategy file reference, Search Space, GA encoding
│   ├── RUN_TEMPLATE.md             ← template for run files
│   └── STORY_TEMPLATE.md           ← template for story files
│
├── scripts/                        ← CI validation scripts
├── tools/                          ← harness.pine, analyze_trades.py (latest; older in tools/archive/)
│
├── dev/                            ← individual development sandboxes
│   └── {username}/
│       └── {category}/
│           └── {bot-name}/
│               ├── {bot-name}-strategy (YYYY-MM-DD).md   ← required
│               ├── {bot-name}-dataspec.yaml               ← required
│               ├── {bot-name}-bot.md                      ← required
│               ├── {bot-name}-run (YYYY-MM-DD-NNN).md    ← optional, repeatable
│               └── {bot-name}-story-{name}.md             ← optional, repeatable
│
├── staging/                        ← shared team review
│   └── {username}/
│       └── {category}/
│           └── {bot-name}/
│
└── prod/                           ← live / paper trading
    └── {username}/
        └── {category}/
            └── {bot-name}/
```
