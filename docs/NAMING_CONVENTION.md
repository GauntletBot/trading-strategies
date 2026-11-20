# Naming Convention

## Docs

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Folder hierarchy, file roles, TDD workflow, promotion path, CI checks |
| [NAMING_CONVENTION.md](NAMING_CONVENTION.md) | This file — naming rules, valid/invalid examples, update guidance |
| [RUN_TEMPLATE.md](RUN_TEMPLATE.md) | Copy-paste template for a new run file |
| [STORY_TEMPLATE.md](STORY_TEMPLATE.md) | Copy-paste template for a new story file |

---

## Rules at a Glance

| Element | Convention | Example |
|---|---|---|
| Username folder | Exact GitHub username, lowercase | `alok-m` |
| Category folder | lowercase, hyphens, descriptive noun | `momentum-bots`, `mean-reversion` |
| Bot folder | lowercase, hyphens, strategy name | `sma-crossover`, `rsi-reversion` |
| Strategy file | `{bot-name}-strategy (YYYY-MM-DD).md` | `sma-crossover-strategy (2026-11-20).md` |
| DataSpec file | `{bot-name}-dataspec.yaml` | `sma-crossover-dataspec.yaml` |
| Bot file | `{bot-name}-bot.md` | `sma-crossover-bot.md` |
| Run file | `{bot-name}-run (YYYY-MM-DD-NNN).md` | `sma-crossover-run (2026-11-20-001).md` |
| Story file | `{bot-name}-story-{story-name}.md` | `sma-crossover-story-baseline-2023.md` |

**Required:** strategy, dataspec, bot — every bot folder must have all three.  
**Optional, repeatable:** run, story — added as backtesting progresses; no limit on how many.

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
- The bot folder name becomes the **prefix** for all five file types inside it

---

## File Rules

### Strategy File
```
{bot-name}-strategy (YYYY-MM-DD).md
```
- The date is the **last-updated date** of the strategy logic
- Update the date in the filename whenever signal logic or parameters change
- Cosmetic edits (typos, formatting) do not require a date bump
- **One per bot folder** — do not keep old dated versions alongside the current one; git history preserves them

**Valid:** `sma-crossover-strategy (2026-11-20).md`  
**Invalid:** `sma-crossover-strategy.md` — missing date  
**Invalid:** `sma-crossover-strategy (November 2026).md` — wrong date format  
**Invalid:** `SMA-Crossover-Strategy (2026-11-20).md` — not lowercase  
**Invalid:** two strategy files in the same folder — delete the old one

### DataSpec File
```
{bot-name}-dataspec.yaml
```
- No date in the filename — versioned via the `version:` field inside the file
- Must use `.yaml` extension (not `.yml`)
- **One per bot folder**

**Valid:** `sma-crossover-dataspec.yaml`  
**Invalid:** `sma-crossover-dataspec.yml` — wrong extension  
**Invalid:** `dataspec.yaml` — missing bot-name prefix

### Bot File
```
{bot-name}-bot.md
```
- Bot Operations Document — runtime config, monitoring, incident log
- No date in the filename — updated in-place; git history tracks changes
- **One per bot folder**

**Valid:** `sma-crossover-bot.md`  
**Invalid:** `sma-crossover-operations.md` — wrong suffix  
**Invalid:** `bot.md` — missing bot-name prefix

### Run File
```
{bot-name}-run (YYYY-MM-DD-NNN).md
```
Template: [RUN_TEMPLATE.md](RUN_TEMPLATE.md)

- Records one backtest execution: inputs, expected results (written **before** running), and actual results (filled after)
- `YYYY-MM-DD` is the date the run was created, not the date of the data
- `NNN` is a zero-padded sequence for multiple runs on the same day: `001`, `002`, `003`
- **Write Expected Results before executing** — this is the TDD contract; CI enforces it
- Status lifecycle: `expected` → `completed` or `failed`
- **Many per bot folder** — runs accumulate over time; never delete them

**Valid:** `sma-crossover-run (2026-11-20-001).md`  
**Valid:** `sma-crossover-run (2026-11-20-002).md` — second run on the same day  
**Invalid:** `sma-crossover-run-2026-11-20.md` — wrong format, missing parens and sequence  
**Invalid:** `sma-crossover-run (2026-11-20).md` — missing sequence number  
**Invalid:** `sma-crossover-run (20261120-001).md` — date must be hyphenated YYYY-MM-DD

### Story File
```
{bot-name}-story-{story-name}.md
```
Template: [STORY_TEMPLATE.md](STORY_TEMPLATE.md)

- A named hypothesis linking one or more run documents
- Declares a falsifiable claim and acceptance criteria **before** any run executes
- `{story-name}` is lowercase-hyphen: `baseline-2023`, `high-vol-regime`, `param-sweep-fast-window`
- Status lifecycle: `open` → `passing` or `failing`
- **Many per bot folder** — a bot may have multiple active and historical stories

**Valid:** `sma-crossover-story-baseline-2023.md`  
**Valid:** `sma-crossover-story-high-vol-regime.md`  
**Invalid:** `sma-crossover-story.md` — missing story name  
**Invalid:** `sma-crossover-story-Baseline_2023.md` — not lowercase, uses underscore

---

## What Not to Do

| Bad | Why | Good |
|---|---|---|
| `SMA_Crossover/` | Uppercase + underscores in folder name | `sma-crossover/` |
| `my-strategy.md` | Missing bot-name prefix and date | `sma-crossover-strategy (2026-11-20).md` |
| `dataspec.yml` | Wrong extension, missing prefix | `sma-crossover-dataspec.yaml` |
| `bot-folder/sub-bot/` | Bot folders are leaf nodes | Move sub-bot to its own category folder |
| `dev/Jane/` | Must match GitHub username exactly | `dev/trader-jane/` |
| Two strategy files in one bot folder | Causes ambiguity | Delete the old one; git preserves history |
| `sma-crossover-run-2026-11-20.md` | Run file missing parens and sequence | `sma-crossover-run (2026-11-20-001).md` |
| `sma-crossover-run (2026-11-20).md` | Run file missing sequence number | `sma-crossover-run (2026-11-20-001).md` |
| `sma-crossover-story.md` | Story file missing story name | `sma-crossover-story-baseline-2023.md` |
| Deleting old run files | Runs are the evidence record | Keep all runs; mark status `failed` if needed |

---

## Updating Each File Type

### Updating a Strategy
When signal logic or parameters change:
1. Edit `{bot-name}-strategy (OLD-DATE).md`
2. Rename to `{bot-name}-strategy (NEW-DATE).md`
3. Update the `updated:` field in the metadata block inside the file
4. Commit both changes in one commit — the rename appears clearly in the PR diff

### Updating a DataSpec
When symbols, date range, or frequency change:
1. Edit the YAML file in-place
2. Bump the `version:` field inside the file (semver)
3. Any existing run files referencing the old spec remain valid — they captured their inputs at run time

### Updating a Bot File
Update in-place at any time — no rename needed. Add an entry to the Change Log section for significant changes.

### Adding a New Run
1. Copy `docs/RUN_TEMPLATE.md` → `{bot-name}-run (YYYY-MM-DD-NNN).md` in the bot folder
2. Fill in the Inputs and Parameters Used sections
3. **Fill in Expected Results** with numeric targets before committing
4. Commit and open a PR — CI validates that expected values are set
5. Execute the backtest, then fill Actual Results and set `status: completed`

### Adding a New Story
1. Copy `docs/STORY_TEMPLATE.md` → `{bot-name}-story-{name}.md` in the bot folder
2. Write the hypothesis and acceptance criteria **before** creating any run files for it
3. Add run file references to the Runs table as you execute
4. Update `status:` to `passing` or `failing` once runs are complete
