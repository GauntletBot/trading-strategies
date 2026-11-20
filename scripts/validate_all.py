#!/usr/bin/env python3
"""
Entry point: reads a JSON list of changed bot folders and runs all
three validators against each one. Exits non-zero if any check fails.
"""

import json
import sys
import os

from validate_strategy import validate_strategy
from validate_dataspec import validate_dataspec
from validate_bot import validate_bot
from validate_run import validate_run
from validate_folder import validate_folder_completeness


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_all.py <changed_folders.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        folders = json.load(f)

    if not folders:
        print("No bot folders changed — nothing to validate.")
        sys.exit(0)

    errors = []

    for folder in folders:
        if not os.path.isdir(folder):
            # Folder was deleted — skip validation
            print(f"SKIP  {folder}  (deleted)")
            continue

        print(f"\n{'='*60}")
        print(f"Validating: {folder}")
        print(f"{'='*60}")

        # 1. Check all three files are present
        folder_errors = validate_folder_completeness(folder)
        if folder_errors:
            errors.extend(folder_errors)
            print(f"  FAIL  folder completeness")
            for e in folder_errors:
                print(f"        {e}")
            # Can't validate individual files if they're missing — skip
            continue

        bot_name = os.path.basename(folder)

        # 2. Validate strategy file
        import glob
        strategy_files = glob.glob(f"{folder}/{bot_name}-strategy (*).md")
        if strategy_files:
            strategy_errors = validate_strategy(strategy_files[0], bot_name)
            if strategy_errors:
                errors.extend(strategy_errors)
                print(f"  FAIL  strategy")
                for e in strategy_errors:
                    print(f"        {e}")
            else:
                print(f"  PASS  strategy")

        # 3. Validate dataspec file
        dataspec_path = f"{folder}/{bot_name}-dataspec.yaml"
        dataspec_errors = validate_dataspec(dataspec_path, bot_name)
        if dataspec_errors:
            errors.extend(dataspec_errors)
            print(f"  FAIL  dataspec")
            for e in dataspec_errors:
                print(f"        {e}")
        else:
            print(f"  PASS  dataspec")

        # 4. Validate bot file
        bot_path = f"{folder}/{bot_name}-bot.md"
        bot_errors = validate_bot(bot_path, bot_name)
        if bot_errors:
            errors.extend(bot_errors)
            print(f"  FAIL  bot.md")
            for e in bot_errors:
                print(f"        {e}")
        else:
            print(f"  PASS  bot.md")

        # 5. Validate any run files present in this folder
        import glob
        run_files = glob.glob(f"{folder}/{bot_name}-run (*).md")
        for run_file in sorted(run_files):
            run_errors = validate_run(run_file, bot_name)
            label = os.path.basename(run_file)
            if run_errors:
                errors.extend(run_errors)
                print(f"  FAIL  {label}")
                for e in run_errors:
                    print(f"        {e}")
            else:
                print(f"  PASS  {label}")

    print(f"\n{'='*60}")
    if errors:
        print(f"FAILED — {len(errors)} error(s) found:\n")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print(f"All {len(folders)} bot folder(s) passed validation.")
        sys.exit(0)


if __name__ == "__main__":
    # Allow importing sibling scripts
    sys.path.insert(0, os.path.dirname(__file__))
    main()
