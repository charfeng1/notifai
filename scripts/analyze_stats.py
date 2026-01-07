import json
import os
import re
import sys
from collections import Counter, defaultdict

# Set UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get all batch files
data_dir = r"E:\projects\notif\data"
batch_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.jsonl')])

print(f"Found {len(batch_files)} batch files\n")

# Initialize counters
total_entries = 0
folder_counts = Counter()
priority_counts = Counter()
app_counts = Counter()
chinese_count = 0
title_lengths = []
body_lengths = []

# CJK regex pattern
cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff]')

# Process each batch file
for batch_file in batch_files:
    filepath = os.path.join(data_dir, batch_file)

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
                total_entries += 1

                # Extract nested data
                notification = entry.get('notification', {})
                classification = entry.get('classification', {})

                # Folder distribution
                folder = classification.get('folder', 'Unknown')
                folder_counts[folder] += 1

                # Priority distribution
                priority = classification.get('priority', 'Unknown')
                priority_counts[priority] += 1

                # App distribution
                app = notification.get('app_display_name', notification.get('app', 'Unknown'))
                app_counts[app] += 1

                # Check for Chinese characters
                title = notification.get('title', '')
                body = notification.get('body', '')

                if cjk_pattern.search(title) or cjk_pattern.search(body):
                    chinese_count += 1

                # Title and body lengths
                title_lengths.append(len(title))
                body_lengths.append(len(body))

            except json.JSONDecodeError as e:
                print(f"Error in {batch_file} line {line_num}: {e}")

# Calculate statistics
print("=" * 80)
print("DATASET STATISTICS REPORT")
print("=" * 80)

print(f"\n1. TOTAL ENTRIES: {total_entries:,}")

# Folder distribution
print(f"\n2. FOLDER DISTRIBUTION:")
print("-" * 80)
folder_order = ['Work', 'Personal', 'Promotions', 'Alerts']
for folder in folder_order:
    count = folder_counts[folder]
    percentage = (count / total_entries * 100) if total_entries > 0 else 0
    print(f"  {folder:<15} {count:>6} ({percentage:>5.1f}%)")

# Add any other folders not in the expected list
other_folders = set(folder_counts.keys()) - set(folder_order)
if other_folders:
    print("\n  Other folders:")
    for folder in sorted(other_folders):
        count = folder_counts[folder]
        percentage = (count / total_entries * 100) if total_entries > 0 else 0
        print(f"  {folder:<15} {count:>6} ({percentage:>5.1f}%)")

# Priority distribution
print(f"\n3. PRIORITY DISTRIBUTION:")
print("-" * 80)
for priority in [1, 2, 3, 4, 5]:
    count = priority_counts[priority]
    percentage = (count / total_entries * 100) if total_entries > 0 else 0
    print(f"  P{priority}              {count:>6} ({percentage:>5.1f}%)")

# Check for unknown priorities
if 'Unknown' in priority_counts:
    count = priority_counts['Unknown']
    percentage = (count / total_entries * 100) if total_entries > 0 else 0
    print(f"  Unknown         {count:>6} ({percentage:>5.1f}%)")

# Top 10 apps
print(f"\n4. TOP 10 MOST FREQUENT APPS:")
print("-" * 80)
top_apps = app_counts.most_common(10)
for i, (app, count) in enumerate(top_apps, 1):
    percentage = (count / total_entries * 100) if total_entries > 0 else 0
    print(f"  {i:>2}. {app:<40} {count:>6} ({percentage:>5.1f}%)")

# Chinese content
print(f"\n5. CHINESE CHARACTER (CJK) CONTENT:")
print("-" * 80)
chinese_percentage = (chinese_count / total_entries * 100) if total_entries > 0 else 0
print(f"  Entries with Chinese: {chinese_count:>6} ({chinese_percentage:>5.1f}%)")
print(f"  Entries without:      {total_entries - chinese_count:>6} ({100 - chinese_percentage:>5.1f}%)")

# Average lengths
print(f"\n6. AVERAGE TITLE AND BODY LENGTHS:")
print("-" * 80)
avg_title = sum(title_lengths) / len(title_lengths) if title_lengths else 0
avg_body = sum(body_lengths) / len(body_lengths) if body_lengths else 0
print(f"  Average title length: {avg_title:.1f} characters")
print(f"  Average body length:  {avg_body:.1f} characters")

# Quality assessment
print("\n" + "=" * 80)
print("QUALITY ASSESSMENT vs TARGET DISTRIBUTIONS")
print("=" * 80)

# Folder targets
print("\nFOLDER DISTRIBUTION:")
work_pct = (folder_counts['Work'] / total_entries * 100) if total_entries > 0 else 0
personal_pct = (folder_counts['Personal'] / total_entries * 100) if total_entries > 0 else 0
promotions_pct = (folder_counts['Promotions'] / total_entries * 100) if total_entries > 0 else 0
alerts_pct = (folder_counts['Alerts'] / total_entries * 100) if total_entries > 0 else 0

issues = []

print(f"  Work:       {work_pct:>5.1f}% (Target: 35%)")
if abs(work_pct - 35) > 5:
    status = "IMBALANCED" if abs(work_pct - 35) > 10 else "SLIGHTLY OFF"
    print(f"    -> {status}: Deviation of {work_pct - 35:+.1f}%")
    issues.append(f"Work folder: {work_pct:.1f}% (target: 35%)")
else:
    print(f"    -> OK")

print(f"  Personal:   {personal_pct:>5.1f}% (Target: 30-35%)")
if personal_pct < 30 or personal_pct > 35:
    status = "IMBALANCED" if personal_pct < 25 or personal_pct > 40 else "SLIGHTLY OFF"
    print(f"    -> {status}")
    issues.append(f"Personal folder: {personal_pct:.1f}% (target: 30-35%)")
else:
    print(f"    -> OK")

print(f"  Promotions: {promotions_pct:>5.1f}% (Target: 15-20%)")
if promotions_pct < 15 or promotions_pct > 20:
    status = "IMBALANCED" if promotions_pct < 10 or promotions_pct > 25 else "SLIGHTLY OFF"
    print(f"    -> {status}")
    issues.append(f"Promotions folder: {promotions_pct:.1f}% (target: 15-20%)")
else:
    print(f"    -> OK")

print(f"  Alerts:     {alerts_pct:>5.1f}% (Target: 15%)")
if abs(alerts_pct - 15) > 5:
    status = "IMBALANCED" if abs(alerts_pct - 15) > 10 else "SLIGHTLY OFF"
    print(f"    -> {status}: Deviation of {alerts_pct - 15:+.1f}%")
    issues.append(f"Alerts folder: {alerts_pct:.1f}% (target: 15%)")
else:
    print(f"    -> OK")

# Priority targets
print("\nPRIORITY DISTRIBUTION:")
p2_pct = (priority_counts[2] / total_entries * 100) if total_entries > 0 else 0
p3_pct = (priority_counts[3] / total_entries * 100) if total_entries > 0 else 0
p5_pct = (priority_counts[5] / total_entries * 100) if total_entries > 0 else 0
p2_p3_combined = p2_pct + p3_pct

print(f"  P2+P3 combined: {p2_p3_combined:>5.1f}% (Should be majority)")
if p2_p3_combined < 50:
    print(f"    -> WARNING: P2+P3 should dominate the distribution")
    issues.append(f"P2+P3 combined only {p2_p3_combined:.1f}% (should be >50%)")
else:
    print(f"    -> OK")

print(f"  P5:             {p5_pct:>5.1f}% (Target: <15%)")
if p5_pct >= 15:
    print(f"    -> WARNING: Too many P5 entries")
    issues.append(f"P5 priority: {p5_pct:.1f}% (target: <15%)")
else:
    print(f"    -> OK")

# Chinese content targets
print("\nCHINESE CONTENT:")
print(f"  CJK content:    {chinese_percentage:>5.1f}% (Target: 30-40%)")
if chinese_percentage < 30 or chinese_percentage > 40:
    status = "IMBALANCED" if chinese_percentage < 20 or chinese_percentage > 50 else "SLIGHTLY OFF"
    print(f"    -> {status}")
    issues.append(f"Chinese content: {chinese_percentage:.1f}% (target: 30-40%)")
else:
    print(f"    -> OK")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if issues:
    print(f"\nFound {len(issues)} distribution issues:\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("\nAll distributions are within target ranges!")

print("\n" + "=" * 80)
