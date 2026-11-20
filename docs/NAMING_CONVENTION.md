# Naming Convention

## Rules at a Glance

| Element | Convention | Example |
|---|---|---|
| Username folder | Exact GitHub username, lowercase | `alok-m` |
| Category folder | lowercase, hyphens, descriptive noun | `momentum-bots`, `mean-reversion` |
| Bot folder | lowercase, hyphens, strategy name | `sma-crossover`, `rsi-reversion` |
| Strategy file | `{bot-name}-strategy (YYYY-MM-DD).md` | `sma-crossover-strategy (2026-11-20).md` |
| DataSpec file | `{bot-name}-dataspec.yaml` | `sma-crossover-dataspec.yaml` |
| Bot file | `{bot-name}-bot.md` | `sma-crossover-bot.md` |

---

## Naming Rules

### Username Folder
- Must exactly match the contributor's GitHub username
- Lowercase by convention (GitHub usernames are case-insensitive)
- Never rename someone else's folder

### Category Folders
- Lowercase letters, numbers, hyphens only — no spaces, underscores, or dots
- Descriptive noun phrases: `momentum-bots`, `mean-reversion`, `options`, `scalping`, `arbitrage`
- Nest freely: `momentum-bots/large-cap/nyse-only/` is valid
- Keep names short — 2–4 words max

### Bot Folder
- Must be the leaf node of the tree (no folders inside a bot folder)
- Same naming rules as category folders
- Should describe the strategy concisely: `sma-crossover`, `rsi-reversion`, `vwap-scalp`
- The bot folder name becomes the **prefix** for all three files inside it

### Strategy File
```
{bot-name}-strategy (YYYY-MM-DD).md
```
- The date is the **last-updated date** of the strategy logic
- Update the date in the filename whenever the signal logic or parameters change
- Cosmetic edits (typos, formatting) do not require a date bump
- One strategy file per bot folder — do not keep old dated versions in the folder (git history preserves them)

**Valid:** `sma-crossover-strategy (2026-11-20).md`  
**Invalid:** `sma-crossover-strategy.md` (missing date)  
**Invalid:** `sma-crossover-strategy (November 2026).md` (wrong date format)  
**Invalid:** `SMA-Crossover-Strategy (2026-11-20).md` (not lowercase)

### DataSpec File
```
{bot-name}-dataspec.yaml
```
- No date in the filename — the spec is versioned via the `version:` field inside the file
- Must use `.yaml` extension (not `.yml`)

### Bot File
```
{bot-name}-bot.md
```
- Bot Operations Document — runtime config, monitoring, incident log
- No date in the filename — updated in-place, git history tracks changes

---

## What Not to Do

| Bad | Why | Good |
|---|---|---|
| `SMA_Crossover/` | Uppercase + underscores | `sma-crossover/` |
| `my-strategy.md` | Missing bot-name prefix and date | `sma-crossover-strategy (2026-11-20).md` |
| `dataspec.yml` | Wrong extension, missing prefix | `sma-crossover-dataspec.yaml` |
| `bot-folder/sub-bot/` | Bot folders are leaf nodes | Move sub-bot to its own category folder |
| `dev/Jane/` | Wrong — must match GitHub username exactly | `dev/trader-jane/` |
| Two strategy files in one bot folder | Causes ambiguity | Delete the old one; git preserves history |

---

## Updating a Strategy

When you change signal logic or parameters:

1. Edit `{bot-name}-strategy (OLD-DATE).md`
2. Rename the file to `{bot-name}-strategy (NEW-DATE).md`
3. Update the `updated:` field in the metadata block inside the file
4. Commit both changes in one commit

The rename shows up clearly in the PR diff and git log.
