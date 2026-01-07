#!/usr/bin/env python3
"""
Remap priorities from 5 levels to 3 levels.

Mapping strategy:
- Old Priority 1, 2 → New Priority 1 (Low/Mute)
- Old Priority 3 → New Priority 2 (Medium/Normal)
- Old Priority 4, 5 → New Priority 3 (High/Urgent)
"""

import json
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(__file__).parent.parent / "training_data.jsonl"
OUTPUT_FILE = Path(__file__).parent.parent / "training_data_3level.jsonl"

def remap_priority(old_priority):
    """Remap 5-level priority to 3-level priority."""
    if old_priority in [1, 2]:
        return 1  # Low
    elif old_priority == 3:
        return 2  # Medium
    elif old_priority in [4, 5]:
        return 3  # High
    else:
        raise ValueError(f"Invalid priority: {old_priority}")

def main():
    print("="*70)
    print("REMAP PRIORITIES: 5 LEVELS TO 3 LEVELS")
    print("="*70)
    print()

    # Read and remap
    examples = []
    old_priority_counts = Counter()
    new_priority_counts = Counter()

    print(f"Reading from: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            example = json.loads(line)
            old_priority = example["classification"]["priority"]
            old_priority_counts[old_priority] += 1

            # Remap priority
            new_priority = remap_priority(old_priority)
            example["classification"]["priority"] = new_priority
            new_priority_counts[new_priority] += 1

            examples.append(example)

    print(f"Total examples: {len(examples)}")
    print()

    # Show mapping
    print("OLD PRIORITY DISTRIBUTION (5 levels):")
    for priority in sorted(old_priority_counts.keys()):
        count = old_priority_counts[priority]
        pct = count / len(examples) * 100
        print(f"  Priority {priority}: {count:5} ({pct:5.1f}%)")

    print()
    print("NEW PRIORITY DISTRIBUTION (3 levels):")
    for priority in sorted(new_priority_counts.keys()):
        count = new_priority_counts[priority]
        pct = count / len(examples) * 100
        print(f"  Priority {priority}: {count:5} ({pct:5.1f}%)")

    print()
    print("MAPPING SUMMARY:")
    print(f"  Old 1+2 -> New 1: {old_priority_counts[1] + old_priority_counts[2]} examples")
    print(f"  Old 3   -> New 2: {old_priority_counts[3]} examples")
    print(f"  Old 4+5 -> New 3: {old_priority_counts[4] + old_priority_counts[5]} examples")

    # Save
    print()
    print(f"Saving to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print()
    print("="*70)
    print("REMAP COMPLETE")
    print("="*70)
    print(f"Remapped {len(examples)} examples")
    print(f"Saved to: {OUTPUT_FILE}")
    print()

if __name__ == "__main__":
    main()
