#!/usr/bin/env python3
"""
Checks that a bot folder contains all three required files and that
their names all share the same bot-name prefix.
"""

import os
import glob
import re


def validate_folder_completeness(folder: str) -> list[str]:
    errors = []
    bot_name = os.path.basename(folder)

    # 1. Strategy file: {bot-name}-strategy (YYYY-MM-DD).md
    strategy_pattern = f"{folder}/{bot_name}-strategy (*).md"
    strategy_files = glob.glob(strategy_pattern)

    if not strategy_files:
        errors.append(
            f"[{folder}] Missing strategy file: "
            f"expected '{bot_name}-strategy (YYYY-MM-DD).md'"
        )
    elif len(strategy_files) > 1:
        errors.append(
            f"[{folder}] Multiple strategy files found — only one allowed: "
            + ", ".join(os.path.basename(f) for f in strategy_files)
        )
    else:
        fname = os.path.basename(strategy_files[0])
        date_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', fname)
        if not date_match:
            errors.append(
                f"[{folder}] Strategy filename date must be YYYY-MM-DD format: '{fname}'"
            )

    # 2. DataSpec file: {bot-name}-dataspec.yaml
    dataspec_path = f"{folder}/{bot_name}-dataspec.yaml"
    if not os.path.isfile(dataspec_path):
        errors.append(
            f"[{folder}] Missing dataspec file: "
            f"expected '{bot_name}-dataspec.yaml'"
        )

    # 3. Bot file: {bot-name}-bot.md
    bot_path = f"{folder}/{bot_name}-bot.md"
    if not os.path.isfile(bot_path):
        errors.append(
            f"[{folder}] Missing bot file: "
            f"expected '{bot_name}-bot.md'"
        )

    # 4. No unexpected files or sub-folders (bot folders are leaf nodes)
    all_entries = os.listdir(folder)
    expected = {
        f"{bot_name}-dataspec.yaml",
        f"{bot_name}-bot.md",
    }
    if strategy_files:
        expected.add(os.path.basename(strategy_files[0]))

    for entry in all_entries:
        full_path = os.path.join(folder, entry)
        if os.path.isdir(full_path):
            errors.append(
                f"[{folder}] Bot folders must be leaf nodes — "
                f"unexpected sub-folder: '{entry}'"
            )
        elif entry not in expected and not entry.startswith("."):
            errors.append(
                f"[{folder}] Unexpected file '{entry}' — "
                f"bot folders should only contain the three required files"
            )

    return errors


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    if len(sys.argv) < 2:
        print("Usage: validate_folder.py <bot-folder>")
        sys.exit(1)
    errs = validate_folder_completeness(sys.argv[1])
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
