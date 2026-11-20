#!/usr/bin/env python3
"""
Walks the entire dev/, staging/, prod/ tree and enforces naming conventions:
  - All folder names are lowercase with hyphens only
  - Every leaf folder (bot folder) has exactly the three required files
  - No bot folder is nested inside another bot folder

Run with no arguments — scans the repo from the current working directory.
"""

import os
import re
import sys
import glob


FOLDER_NAME_RE  = re.compile(r"^[a-z0-9][a-z0-9\-]*$")
ENV_ROOTS       = ["dev", "staging", "prod"]
# A folder is a bot folder if it directly contains a *-dataspec.yaml file
BOT_MARKER_GLOB = "*-dataspec.yaml"


def is_bot_folder(path: str) -> bool:
    return bool(glob.glob(os.path.join(path, BOT_MARKER_GLOB)))


def walk_env(root: str) -> list[str]:
    errors = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        rel = os.path.relpath(dirpath, ".")
        depth = rel.count(os.sep)   # 0 = env root, 1 = username, 2+ = category/bot

        folder_name = os.path.basename(dirpath)

        # ── Folder name must be lowercase-hyphen ──────────────────────────────
        if depth > 0 and not FOLDER_NAME_RE.match(folder_name):
            errors.append(
                f"[{rel}] Folder name '{folder_name}' must be lowercase letters, "
                f"numbers, and hyphens only (no spaces, underscores, or uppercase)"
            )

        # ── If this is a bot folder, check its children ───────────────────────
        if is_bot_folder(dirpath):
            bot_name = folder_name

            # Bot folders must not contain sub-folders
            sub_dirs = [d for d in dirnames if not d.startswith(".")]
            for sub in sub_dirs:
                errors.append(
                    f"[{rel}/{sub}] Bot folders are leaf nodes — "
                    f"sub-folder '{sub}' found inside bot folder '{bot_name}'"
                )
            # Prevent os.walk from descending into sub-folders of bot folders
            dirnames.clear()

            # Check the three required files
            strategy_files = glob.glob(os.path.join(dirpath, f"{bot_name}-strategy (*).md"))
            dataspec_path  = os.path.join(dirpath, f"{bot_name}-dataspec.yaml")
            bot_path       = os.path.join(dirpath, f"{bot_name}-bot.md")

            if not strategy_files:
                errors.append(
                    f"[{rel}] Missing '{bot_name}-strategy (YYYY-MM-DD).md'"
                )
            elif len(strategy_files) > 1:
                names = [os.path.basename(f) for f in strategy_files]
                errors.append(
                    f"[{rel}] Multiple strategy files found: {names} — only one allowed"
                )
            else:
                fname = os.path.basename(strategy_files[0])
                if not re.search(r'\(\d{4}-\d{2}-\d{2}\)', fname):
                    errors.append(
                        f"[{rel}] Strategy filename date must be (YYYY-MM-DD) format: '{fname}'"
                    )

            if not os.path.isfile(dataspec_path):
                errors.append(f"[{rel}] Missing '{bot_name}-dataspec.yaml'")

            if not os.path.isfile(bot_path):
                errors.append(f"[{rel}] Missing '{bot_name}-bot.md'")

            # Check for unexpected extra files
            expected = {
                f"{bot_name}-dataspec.yaml",
                f"{bot_name}-bot.md",
            }
            if strategy_files:
                expected.add(os.path.basename(strategy_files[0]))

            run_re   = re.compile(rf"^{re.escape(bot_name)}-run \(\d{{4}}-\d{{2}}-\d{{2}}-\d{{3}}\)\.md$")
            story_re = re.compile(rf"^{re.escape(bot_name)}-story-.+\.md$")

            for fname in filenames:
                if (
                    fname not in expected
                    and not fname.startswith(".")
                    and not run_re.match(fname)
                    and not story_re.match(fname)
                ):
                    errors.append(
                        f"[{rel}] Unexpected file '{fname}' in bot folder '{bot_name}'"
                    )

    return errors


def main():
    errors = []

    for env in ENV_ROOTS:
        if os.path.isdir(env):
            errors.extend(walk_env(env))

    if errors:
        print(f"\nNaming convention violations ({len(errors)}):\n")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print("Naming conventions OK — no violations found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
