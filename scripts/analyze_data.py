#!/usr/bin/env python3
"""Analyze the quality and distribution of synthetic notification data."""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

def analyze_dataset(filepath: Path):
    """Analyze the dataset for quality metrics."""

    folder_counts = Counter()
    priority_counts = Counter()
    app_counts = Counter()
    folder_priority = defaultdict(lambda: Counter())

    total = 0
    title_lengths = []
    body_lengths = []
    has_cjk = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
                total += 1

                # Extract fields
                folder = entry["classification"]["folder"]
                priority = entry["classification"]["priority"]
                app = entry["notification"]["app"]
                title = entry["notification"]["title"]
                body = entry["notification"]["body"]

                # Count distributions
                folder_counts[folder] += 1
                priority_counts[priority] += 1
                app_counts[app] += 1
                folder_priority[folder][priority] += 1

                # Analyze text
                title_lengths.append(len(title))
                body_lengths.append(len(body))

                # Check for CJK characters
                if any('\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff' for c in title + body):
                    has_cjk += 1

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error on line {line_num}: {e}")

    # Print analysis
    print("=" * 60)
    print("DATASET ANALYSIS")
    print("=" * 60)
    print(f"\nTotal entries: {total}")

    print(f"\n--- Folder Distribution ---")
    for folder, count in folder_counts.most_common():
        pct = (count / total) * 100
        print(f"{folder:15} {count:6} ({pct:5.1f}%)")

    print(f"\n--- Priority Distribution ---")
    for priority in sorted(priority_counts.keys()):
        count = priority_counts[priority]
        pct = (count / total) * 100
        print(f"Priority {priority}:     {count:6} ({pct:5.1f}%)")

    print(f"\n--- Top 15 Apps ---")
    for app, count in app_counts.most_common(15):
        pct = (count / total) * 100
        print(f"{app:20} {count:6} ({pct:5.1f}%)")

    print(f"\n--- Priority by Folder ---")
    for folder in sorted(folder_counts.keys()):
        print(f"\n{folder}:")
        for priority in sorted(folder_priority[folder].keys()):
            count = folder_priority[folder][priority]
            pct = (count / folder_counts[folder]) * 100
            print(f"  Priority {priority}: {count:4} ({pct:5.1f}%)")

    print(f"\n--- Text Statistics ---")
    if title_lengths:
        avg_title = sum(title_lengths) / len(title_lengths)
        print(f"Avg title length: {avg_title:.1f} chars")
        print(f"Min title length: {min(title_lengths)} chars")
        print(f"Max title length: {max(title_lengths)} chars")

    if body_lengths:
        avg_body = sum(body_lengths) / len(body_lengths)
        print(f"Avg body length:  {avg_body:.1f} chars")
        print(f"Min body length:  {min(body_lengths)} chars")
        print(f"Max body length:  {max(body_lengths)} chars")

    cjk_pct = (has_cjk / total) * 100 if total > 0 else 0
    print(f"\nEntries with CJK: {has_cjk} ({cjk_pct:.1f}%)")

    # Quality checks
    print(f"\n--- Quality Checks ---")
    issues = []

    # Check folder balance
    expected_per_folder = total / 4
    for folder, count in folder_counts.items():
        pct_diff = abs(count - expected_per_folder) / expected_per_folder * 100
        if pct_diff > 30:  # More than 30% off from expected
            issues.append(f"Folder '{folder}' is imbalanced ({pct_diff:.0f}% off from expected)")

    # Check priority distribution (should be more 2-3, less 5)
    priority_5_pct = (priority_counts[5] / total) * 100 if total > 0 else 0
    if priority_5_pct > 20:
        issues.append(f"Too many priority 5 entries ({priority_5_pct:.1f}%)")

    # Check language diversity
    if cjk_pct < 10:
        issues.append(f"Low CJK language diversity ({cjk_pct:.1f}%)")

    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ No major quality issues detected")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_data.py <file.jsonl>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    analyze_dataset(filepath)
