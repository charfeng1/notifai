#!/usr/bin/env python3
"""Merge all batch files into a single training dataset."""

import json
from pathlib import Path

def merge_batches(data_dir: Path, output_file: Path):
    """Merge all batch_*.jsonl files into a single output file."""
    batch_files = sorted(data_dir.glob("batch_*.jsonl"))

    if not batch_files:
        print(f"No batch files found in {data_dir}")
        return 0

    total_entries = 0
    seen_ids = set()
    duplicates = 0

    with open(output_file, "w", encoding="utf-8") as out:
        for batch_file in batch_files:
            print(f"Processing {batch_file.name}...")
            with open(batch_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        entry_id = entry.get("id")

                        # Check for duplicate IDs
                        if entry_id in seen_ids:
                            duplicates += 1
                            print(f"  Warning: Duplicate ID {entry_id} in {batch_file.name}")
                            continue

                        seen_ids.add(entry_id)
                        out.write(line + "\n")
                        total_entries += 1
                    except json.JSONDecodeError as e:
                        print(f"  Error parsing line in {batch_file.name}: {e}")

    print(f"\nMerged {total_entries} entries from {len(batch_files)} batch files")
    if duplicates:
        print(f"Skipped {duplicates} duplicate entries")

    return total_entries

if __name__ == "__main__":
    data_dir = Path("data")
    output_file = Path("training_data.jsonl")

    if not data_dir.exists():
        print(f"Data directory {data_dir} does not exist")
        exit(1)

    count = merge_batches(data_dir, output_file)
    print(f"\nOutput written to: {output_file}")
    print(f"Total entries: {count}")
