# Story: {story-name}

> A story is a named hypothesis about a strategy's behaviour.
> It links one or more run documents and declares pass/fail criteria
> before any run executes — the TDD contract.
>
> Filename: `{bot-name}-story-{story-name}.md`
> Lives in the same bot folder as the run documents it references.

---

## Metadata
```yaml
story_id:    {bot-name}-story-{story-name}
bot:         {bot-name}
author:      {github-username}
created:     {YYYY-MM-DD}
status:      open        # open | passing | failing | abandoned
hypothesis:  >
  One sentence: "I expect this strategy to..."
```

---

## Hypothesis

State the specific, falsifiable claim this story tests.

> Example: "SMA crossover with fast=10/slow=30 on SPY 1-min 2023 data
> will produce a Sharpe ratio above 1.0 and stay within a 5% max drawdown."

-ToDo

---

## Acceptance Criteria

These must ALL pass for the story to be marked `passing`.

- [ ] -ToDo
- [ ] -ToDo

---

## Runs

List every run document that contributes evidence to this story.

| Run file | Date | Status | Notes |
|---|---|---|---|
| -ToDo | -ToDo | -ToDo | -ToDo |

---

## Result

**Story status:** -ToDo — PASSING / FAILING / OPEN

**Summary:** -ToDo

---

## What We Learned

-ToDo
