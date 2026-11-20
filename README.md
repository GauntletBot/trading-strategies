# GauntletBot — Trading Strategy Repository

This repository is the source of truth for all trading bot strategies and historical data specifications managed under the GauntletBot organization.

## Quick Start

1. Create a folder under `dev/` with your GitHub username
2. Add a subfolder for each strategy category you work on
3. For each bot, create a folder containing the three required files
4. Open a PR — CI validates all files before merge

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full information architecture.  
See [docs/NAMING_CONVENTION.md](docs/NAMING_CONVENTION.md) for file and folder naming rules.

---

## Environments

| Folder | Purpose | Who merges |
|---|---|---|
| `dev/` | Individual development — personal sandboxes | Author self-merges |
| `staging/` | Shared review — strategies under team evaluation | Requires 1 approval |
| `prod/` | Live strategies running on paper/live accounts | Requires 2 approvals + CI pass |

---

## Three Required Files per Bot

| File | Purpose |
|---|---|
| `{bot-name}-strategy (YYYY-MM-DD).md` | Signal logic, parameters, risk rules, approval checklist |
| `{bot-name}-dataspec.yaml` | Historical dataset definition — symbols, period, frequency, feed |
| `{bot-name}-bod.md` | Bot Operations Document — runtime config, deployment notes, known issues |

---

## Repository Structure

```
trading-strategies/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   └── NAMING_CONVENTION.md
│
├── dev/                            ← individual development sandboxes
│   └── {username}/
│       └── {category}/
│           └── {bot-name}/
│               ├── {bot-name}-strategy (YYYY-MM-DD).md
│               ├── {bot-name}-dataspec.yaml
│               └── {bot-name}-bod.md
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
