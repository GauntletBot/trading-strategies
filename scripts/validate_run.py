#!/usr/bin/env python3
"""
Validates a {bot-name}-run (YYYY-MM-DD-NNN).md file.

Checks:
  - Metadata block has required fields
  - run_id matches the filename pattern
  - bot name in metadata matches the bot folder
  - status is a valid value
  - Required sections present
  - Expected Results table has at least one row
  - Actual Results table present (may still be -ToDo)
  - If status is 'completed', Actual Results must have no -ToDo values
"""

import os
import re
import sys


REQUIRED_METADATA_FIELDS = [
    "run_id",
    "bot",
    "strategy_file",
    "dataspec_file",
    "run_date",
    "run_number",
    "author",
    "status",
]

VALID_STATUSES = {"expected", "completed", "failed"}

REQUIRED_SECTIONS = [
    "## Inputs",
    "## Parameters Used",
    "## Expected Results",
    "## Actual Results",
    "## Observations",
    "## Next Actions",
]

RUN_FILENAME_RE = re.compile(
    r"^(.+)-run \((\d{4}-\d{2}-\d{2})-(\d{3})\)\.md$"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_metadata_block(content: str) -> dict | None:
    match = re.search(r"```yaml\s*\n(.*?)```", content, re.DOTALL)
    if not match:
        return None
    meta = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("#") and not line.startswith(">"):
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


def validate_run(path: str, bot_name: str) -> list[str]:
    errors = []

    if not os.path.isfile(path):
        return [f"[{path}] File not found"]

    filename = os.path.basename(path)
    fname_match = RUN_FILENAME_RE.match(filename)

    # ── Filename format ───────────────────────────────────────────────────────
    if not fname_match:
        errors.append(
            f"[{path}] Run filename must match pattern: "
            f"'{{bot-name}}-run (YYYY-MM-DD-NNN).md', got: '{filename}'"
        )
    else:
        fname_bot  = fname_match.group(1)
        fname_date = fname_match.group(2)
        fname_seq  = fname_match.group(3)

        if fname_bot != bot_name:
            errors.append(
                f"[{path}] Filename bot prefix '{fname_bot}' does not match "
                f"bot folder name '{bot_name}'"
            )

    with open(path) as f:
        content = f.read()

    # ── Metadata block ────────────────────────────────────────────────────────
    meta = _parse_metadata_block(content)
    if meta is None:
        errors.append(f"[{path}] Missing metadata block — expected a ```yaml ... ``` block")
        return errors

    for field in REQUIRED_METADATA_FIELDS:
        if field not in meta or not meta[field] or meta[field] == "~":
            if field == "mlflow_run_id":
                continue  # optional until completed
            errors.append(f"[{path}] Metadata missing required field: '{field}'")

    if "bot" in meta and meta["bot"] != bot_name:
        errors.append(
            f"[{path}] Metadata 'bot' ('{meta['bot']}') does not match "
            f"bot folder name ('{bot_name}')"
        )

    if "status" in meta and meta["status"] not in VALID_STATUSES:
        errors.append(
            f"[{path}] Invalid status '{meta['status']}' — "
            f"must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )

    if "run_date" in meta and meta["run_date"] and not DATE_RE.match(meta["run_date"]):
        errors.append(
            f"[{path}] 'run_date' must be YYYY-MM-DD format, got: '{meta['run_date']}'"
        )

    # Strategy and dataspec filenames must reference this bot
    for ref_field in ("strategy_file", "dataspec_file"):
        val = meta.get(ref_field, "")
        if val and not val.startswith(bot_name):
            errors.append(
                f"[{path}] '{ref_field}' ('{val}') must start with bot name '{bot_name}'"
            )

    # ── Required sections ─────────────────────────────────────────────────────
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"[{path}] Missing required section: '{section}'")

    # ── Expected Results must have at least one non-header row ────────────────
    if "## Expected Results" in content:
        exp_part = content.split("## Expected Results", 1)[1].split("## Actual")[0]
        rows = [
            l for l in exp_part.splitlines()
            if l.strip().startswith("|")
            and "---|" not in l
            and "Metric" not in l
        ]
        if not rows:
            errors.append(
                f"[{path}] Expected Results table has no rows — "
                f"define at least one metric before running"
            )
        # Every expected row must have a numeric expected value (not -ToDo)
        for row in rows:
            cols = [c.strip() for c in row.split("|") if c.strip()]
            if len(cols) >= 2 and cols[1] == "-ToDo":
                errors.append(
                    f"[{path}] Expected Results row '{cols[0]}' has no expected value — "
                    f"set the target before running (TDD: write expectations first)"
                )

    # ── If status is completed, Actual Results must be filled in ─────────────
    status = meta.get("status", "")
    if status == "completed" and "## Actual Results" in content:
        act_part = content.split("## Actual Results", 1)[1].split("##")[0]
        if "-ToDo" in act_part:
            errors.append(
                f"[{path}] Status is 'completed' but Actual Results still contain "
                f"'-ToDo' — fill in all actual metric values"
            )

    return errors


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    if len(sys.argv) < 3:
        print("Usage: validate_run.py <path> <bot-name>")
        sys.exit(1)
    errs = validate_run(sys.argv[1], sys.argv[2])
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
