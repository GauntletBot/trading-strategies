#!/usr/bin/env python3
"""
Validates a {bot-name}-bot.md file.

Checks:
  - Required sections are present
  - Identity table contains required rows
  - Runtime configuration block is present
  - Known Issues and Change Log sections exist
"""

import os
import re
import sys


REQUIRED_SECTIONS = [
    "## Identity",
    "## Runtime Configuration",
    "## Monitoring & Alerts",
    "## Known Issues",
    "## Change Log",
]

REQUIRED_IDENTITY_ROWS = [
    "Bot name",
    "Owner",
    "Environment",
    "Status",
]

VALID_ENVIRONMENTS = {"dev", "staging", "prod"}
VALID_STATUSES     = {
    "inactive — backtesting only",
    "paper trading",
    "live",
    "deprecated",
    "paused",
}


def _extract_section(content: str, heading: str) -> str:
    """Return the content between `heading` and the next ## heading."""
    if heading not in content:
        return ""
    after = content.split(heading, 1)[1]
    next_heading = re.search(r"\n## ", after)
    return after[:next_heading.start()] if next_heading else after


def validate_bot(path: str, bot_name: str) -> list[str]:
    errors = []

    if not os.path.isfile(path):
        return [f"[{path}] File not found"]

    with open(path) as f:
        content = f.read()

    # ── H1 title must reference the bot ───────────────────────────────────────
    if not content.startswith("# "):
        errors.append(f"[{path}] File must start with an H1 title (# ...)")

    # ── Required sections ─────────────────────────────────────────────────────
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"[{path}] Missing required section: '{section}'")

    # ── Identity table rows ───────────────────────────────────────────────────
    identity_section = _extract_section(content, "## Identity")
    for row in REQUIRED_IDENTITY_ROWS:
        if row not in identity_section:
            errors.append(f"[{path}] Identity table missing row: '{row}'")

    # ── Bot name in identity must match folder ────────────────────────────────
    bot_name_match = re.search(r"\|\s*Bot name\s*\|\s*(.+?)\s*\|", identity_section)
    if bot_name_match:
        declared = bot_name_match.group(1).strip()
        if declared != bot_name:
            errors.append(
                f"[{path}] Identity 'Bot name' ('{declared}') does not match "
                f"bot folder name ('{bot_name}')"
            )

    # ── Environment must be valid ─────────────────────────────────────────────
    env_match = re.search(r"\|\s*Environment\s*\|\s*(.+?)\s*\|", identity_section)
    if env_match:
        env = env_match.group(1).strip()
        if env not in VALID_ENVIRONMENTS:
            errors.append(
                f"[{path}] Identity 'Environment' ('{env}') must be one of: "
                + ", ".join(sorted(VALID_ENVIRONMENTS))
            )

    # ── Runtime config block must have execution_mode ────────────────────────
    runtime_section = _extract_section(content, "## Runtime Configuration")
    if runtime_section and "execution_mode" not in runtime_section:
        errors.append(
            f"[{path}] Runtime Configuration block must include 'execution_mode'"
        )

    # ── Change Log must have at least one entry ───────────────────────────────
    changelog_section = _extract_section(content, "## Change Log")
    rows = [
        l for l in changelog_section.splitlines()
        if l.strip().startswith("|") and "---|" not in l and "Date" not in l
    ]
    if not rows:
        errors.append(f"[{path}] Change Log has no entries — add at least one row")

    return errors


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    if len(sys.argv) < 3:
        print("Usage: validate_bot.py <path> <bot-name>")
        sys.exit(1)
    errs = validate_bot(sys.argv[1], sys.argv[2])
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
