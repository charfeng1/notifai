#!/usr/bin/env python3
"""Validate synthetic notification data against schema."""

import json
import sys
from pathlib import Path

VALID_FOLDERS = {"Work", "Personal", "Promotions", "Alerts"}

SCHEMA = {
    "id": str,
    "notification": {
        "app": str,
        "app_display_name": str,
        "title": str,
        "body": str,
    },
    "classification": {
        "folder": str,
        "priority": int,
    },
}


def validate_entry(entry: dict, line_num: int) -> list[str]:
    """Validate a single entry. Returns list of errors."""
    errors = []

    # Check top-level fields
    for field in ["id", "notification", "classification"]:
        if field not in entry:
            errors.append(f"Line {line_num}: Missing required field '{field}'")

    if errors:
        return errors

    # Validate id
    if not isinstance(entry["id"], str) or not entry["id"].strip():
        errors.append(f"Line {line_num}: 'id' must be a non-empty string")

    # Validate notification
    notif = entry["notification"]
    for field in ["app", "app_display_name", "title", "body"]:
        if field not in notif:
            errors.append(f"Line {line_num}: Missing 'notification.{field}'")
        elif not isinstance(notif[field], str):
            errors.append(f"Line {line_num}: 'notification.{field}' must be a string")

    # Validate classification
    cls = entry["classification"]
    if "folder" not in cls:
        errors.append(f"Line {line_num}: Missing 'classification.folder'")
    elif cls["folder"] not in VALID_FOLDERS:
        errors.append(f"Line {line_num}: Invalid folder '{cls['folder']}'. Must be one of {VALID_FOLDERS}")

    if "priority" not in cls:
        errors.append(f"Line {line_num}: Missing 'classification.priority'")
    elif not isinstance(cls["priority"], int) or not 1 <= cls["priority"] <= 5:
        errors.append(f"Line {line_num}: 'priority' must be int 1-5, got {cls.get('priority')}")

    return errors


def validate_file(filepath: Path) -> tuple[int, int, list[str]]:
    """Validate a JSONL file. Returns (valid_count, total_count, errors)."""
    errors = []
    valid = 0
    total = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            total += 1

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON - {e}")
                continue

            entry_errors = validate_entry(entry, line_num)
            if entry_errors:
                errors.extend(entry_errors)
            else:
                valid += 1

    return valid, total, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_data.py <file.jsonl> [file2.jsonl ...]")
        sys.exit(1)

    total_valid = 0
    total_entries = 0
    all_errors = []

    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if not path.exists():
            print(f"File not found: {filepath}")
            continue

        valid, total, errors = validate_file(path)
        total_valid += valid
        total_entries += total
        all_errors.extend(errors)

        status = "OK" if not errors else "ERRORS"
        print(f"{filepath}: {valid}/{total} valid [{status}]")

    if all_errors:
        print(f"\n{len(all_errors)} error(s) found:")
        for err in all_errors[:20]:  # Show first 20
            print(f"  {err}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")
        sys.exit(1)
    else:
        print(f"\nAll {total_valid} entries valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
