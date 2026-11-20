#!/usr/bin/env python3
"""
Validates a {bot-name}-dataspec.yaml file.

Checks:
  - Parses as valid YAML
  - All required fields are present and non-empty
  - Field values are within allowed sets
  - spec_id matches the bot folder name prefix
  - Date format is correct
"""

import os
import re
import sys

try:
    import yaml
except ImportError:
    print("pyyaml not installed — run: pip install pyyaml")
    sys.exit(1)


REQUIRED_FIELDS = [
    "spec_id",
    "symbols",
    "start",
    "end",
    "frequency",
    "source",
    "feed",
]

VALID_FREQUENCIES = {
    "tick", "quote",
    "1Min", "5Min", "15Min", "30Min",
    "1Hour", "4Hour",
    "1Day", "1Week", "1Month",
}

VALID_SOURCES = {"alpaca", "polygon", "yahoo", "tiingo"}
VALID_FEEDS   = {"sip", "iex", "stocks", "options", "crypto", "forex"}
VALID_DTYPES  = {"bars", "trades", "quotes"}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_dataspec(path: str, bot_name: str) -> list[str]:
    errors = []

    if not os.path.isfile(path):
        return [f"[{path}] File not found"]

    # ── Parse YAML ────────────────────────────────────────────────────────────
    with open(path) as f:
        raw = f.read()

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        return [f"[{path}] YAML parse error: {e}"]

    if not isinstance(data, dict):
        return [f"[{path}] YAML must be a mapping (key: value pairs) at the top level"]

    # ── Required fields ───────────────────────────────────────────────────────
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None or data[field] == "":
            errors.append(f"[{path}] Missing required field: '{field}'")

    # ── spec_id must start with bot_name ──────────────────────────────────────
    spec_id = data.get("spec_id", "")
    if spec_id and not str(spec_id).startswith(bot_name):
        errors.append(
            f"[{path}] 'spec_id' ('{spec_id}') must start with bot name '{bot_name}'"
        )

    # ── symbols must be a non-empty list ─────────────────────────────────────
    symbols = data.get("symbols")
    if symbols is not None:
        if not isinstance(symbols, list) or len(symbols) == 0:
            errors.append(f"[{path}] 'symbols' must be a non-empty list")
        else:
            for s in symbols:
                if not isinstance(s, str) or not s.strip():
                    errors.append(f"[{path}] Each symbol must be a non-empty string, got: {s!r}")

    # ── Date formats ──────────────────────────────────────────────────────────
    for date_field in ("start", "end"):
        val = str(data.get(date_field, ""))
        if val and val != "latest" and not DATE_RE.match(val):
            errors.append(
                f"[{path}] '{date_field}' must be YYYY-MM-DD format or 'latest', got: '{val}'"
            )

    start = str(data.get("start", ""))
    end   = str(data.get("end", ""))
    if start and end and end != "latest" and DATE_RE.match(start) and DATE_RE.match(end):
        if end < start:
            errors.append(f"[{path}] 'end' ({end}) must be on or after 'start' ({start})")

    # ── Frequency ─────────────────────────────────────────────────────────────
    freq = data.get("frequency")
    if freq and str(freq) not in VALID_FREQUENCIES:
        errors.append(
            f"[{path}] Invalid frequency '{freq}' — must be one of: "
            + ", ".join(sorted(VALID_FREQUENCIES))
        )

    # ── Source and feed ───────────────────────────────────────────────────────
    source = data.get("source")
    if source and str(source) not in VALID_SOURCES:
        errors.append(
            f"[{path}] Invalid source '{source}' — must be one of: "
            + ", ".join(sorted(VALID_SOURCES))
        )

    feed = data.get("feed")
    if feed and str(feed) not in VALID_FEEDS:
        errors.append(
            f"[{path}] Invalid feed '{feed}' — must be one of: "
            + ", ".join(sorted(VALID_FEEDS))
        )

    # ── data_type (optional) ──────────────────────────────────────────────────
    dtype = data.get("data_type")
    if dtype and str(dtype) not in VALID_DTYPES:
        errors.append(
            f"[{path}] Invalid data_type '{dtype}' — must be one of: "
            + ", ".join(sorted(VALID_DTYPES))
        )

    # ── Warn if .yml extension was used (should be .yaml) ─────────────────────
    if path.endswith(".yml"):
        errors.append(f"[{path}] Use '.yaml' extension, not '.yml'")

    return errors


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    if len(sys.argv) < 3:
        print("Usage: validate_dataspec.py <path> <bot-name>")
        sys.exit(1)
    errs = validate_dataspec(sys.argv[1], sys.argv[2])
    for e in errs:
        print(e)
    sys.exit(1 if errs else 0)
