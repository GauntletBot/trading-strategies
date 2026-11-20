#!/usr/bin/env python3
"""
Validates a {bot-name}-strategy (YYYY-MM-DD).md file.

Checks:
  - Frontmatter metadata block (yaml code fence) contains required fields
  - Required top-level sections are present
  - Metadata values are valid (status, version format)
  - strategy name in metadata matches the bot folder name
  - Approval checklist is present
"""

import os
import re
import sys


REQUIRED_METADATA_FIELDS = [
    "name",
    "version",
    "author",
    "status",
    "created",
    "updated",
]

VALID_STATUSES = {"draft", "review", "approved", "deprecated"}

REQUIRED_SECTIONS = [
    "## Description",
    "## Signal Logic",
    "### Entry Conditions",
    "### Exit Conditions",
    "## Parameters",
    "## Risk Rules",
    "## Python Implementation",
    "## Approval Checklist",
]

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE    = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_metadata_block(content: str) -> dict | None:
    """Extract the first ```yaml ... ``` block and parse it as key: value pairs."""
    match = re.search(r"```yaml\s*\n(.*?)```", content, re.DOTALL)
    if not match:
        return None
    meta = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


def validate_strategy(path: str, bot_name: str) -> list[str]:
    errors = []

    if not os.path.isfile(path):
        return [f"[{path}] File not found"]

    with open(path) as f:
        content = f.read()

    # ── Metadata block ────────────────────────────────────────────────────────
    meta = _parse_metadata_block(content)
    if meta is None:
        errors.append(f"[{path}] Missing metadata block — expected a ```yaml ... ``` block at the top")
        return errors  # Can't do further metadata checks

    for field in REQUIRED_METADATA_FIELDS:
        if field not in meta or not meta[field]:
            errors.append(f"[{path}] Metadata missing required field: '{field}'")

    if "name" in meta and meta["name"] != bot_name:
        errors.append(
            f"[{path}] Metadata 'name' ('{meta['name']}') does not match "
            f"bot folder name ('{bot_name}')"
        )

    if "status" in meta and meta["status"] not in VALID_STATUSES:
        errors.append(
            f"[{path}] Invalid status '{meta['status']}' — "
            f"must be one of: {', '.join(sorted(VALID_STATUSES))}"
        )

    if "version" in meta and meta["version"] and not VERSION_RE.match(meta["version"]):
        errors.append(
            f"[{path}] Version '{meta['version']}' must be semver format X.Y.Z"
        )

    for date_field in ("created", "updated"):
        if date_field in meta and meta[date_field] and not DATE_RE.match(meta[date_field]):
            errors.append(
                f"[{path}] '{date_field}' must be YYYY-MM-DD format, got: '{meta[date_field]}'"
            )

    # ── Required sections ─────────────────────────────────────────────────────
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"[{path}] Missing required section: '{section}'")

    # ── Approval checklist must have at least one item ────────────────────────
    if "## Approval Checklist" in content:
        checklist_part = content.split("## Approval Checklist", 1)[1]
        if "- [" not in checklist_part:
            errors.append(f"[{path}] Approval Checklist section is empty — add checklist items")

    # ── Parameters table must have at least one row ───────────────────────────
    if "## Parameters" in content:
        params_part = content.split("## Parameters", 1)[1].split("##")[0]
        rows = [l for l in params_part.splitlines() if l.strip().startswith("|") and "---|" not in l and "Parameter" not in l]
        if not rows:
            errors.append(f"[{path}] Parameters section has no rows — define at least one parameter")

    return errors


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    if len(sys.argv) < 3:
        print("Usage: validate_strategy.py <path> <bot-name>")
        sys.exit(1)
    errs = validate_strategy(sys.argv[1], sys.argv[2])
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
