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

print(f"Analyzing {len(batch_files)} batch files...\n")

# Initialize counters
total_entries = 0
folder_counts = Counter()
priority_counts = Counter()
app_counts = Counter()
chinese_count = 0
title_lengths = []
body_lengths = []
errors = []
batch_stats = {}

# CJK regex pattern
cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff]')

# Process each batch file
for batch_file in batch_files:
    filepath = os.path.join(data_dir, batch_file)
    batch_count = 0
    batch_errors = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
                total_entries += 1
                batch_count += 1

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
                batch_errors += 1
                errors.append(f"{batch_file} line {line_num}: {str(e)[:100]}")

    batch_stats[batch_file] = {'count': batch_count, 'errors': batch_errors}

# Print detailed report
print("=" * 100)
print("COMPREHENSIVE DATASET ANALYSIS REPORT")
print("=" * 100)

print(f"\n1. DATASET OVERVIEW")
print("-" * 100)
print(f"  Total batch files:     {len(batch_files)}")
print(f"  Total entries:         {total_entries:,}")
print(f"  Parsing errors:        {len(errors)}")
print(f"  Average per batch:     {total_entries / len(batch_files):.1f}")

# Show batch-by-batch breakdown
print(f"\n  Batch-by-batch breakdown:")
for batch_file in sorted(batch_stats.keys()):
    stats = batch_stats[batch_file]
    status = " [ERRORS]" if stats['errors'] > 0 else ""
    print(f"    {batch_file}: {stats['count']:>4} entries{status}")

print(f"\n2. FOLDER DISTRIBUTION")
print("-" * 100)
folder_order = ['Work', 'Personal', 'Promotions', 'Alerts']
for folder in folder_order:
    count = folder_counts[folder]
    percentage = (count / total_entries * 100) if total_entries > 0 else 0
    target = ""
    if folder == 'Work':
        target = "(Target: 35%)"
    elif folder == 'Personal':
        target = "(Target: 30-35%)"
    elif folder == 'Promotions':
        target = "(Target: 15-20%)"
    elif folder == 'Alerts':
        target = "(Target: 15%)"
    print(f"  {folder:<15} {count:>6} ({percentage:>5.1f}%)  {target}")

print(f"\n3. PRIORITY DISTRIBUTION")
print("-" * 100)
for priority in [1, 2, 3, 4, 5]:
    count = priority_counts[priority]
    percentage = (count / total_entries * 100) if total_entries > 0 else 0
    bar = "#" * int(percentage / 2)
    print(f"  P{priority}  {count:>6} ({percentage:>5.1f}%)  {bar}")

p2_p3 = priority_counts[2] + priority_counts[3]
p2_p3_pct = (p2_p3 / total_entries * 100) if total_entries > 0 else 0
print(f"\n  P2+P3 combined: {p2_p3:>6} ({p2_p3_pct:>5.1f}%)  (Target: Majority, >50%)")

print(f"\n4. TOP 20 MOST FREQUENT APPS")
print("-" * 100)
top_apps = app_counts.most_common(20)
for i, (app, count) in enumerate(top_apps, 1):
    percentage = (count / total_entries * 100) if total_entries > 0 else 0
    bar = "=" * int(percentage * 2)
    print(f"  {i:>2}. {app:<35} {count:>5} ({percentage:>4.1f}%)  {bar}")

total_top20 = sum(count for _, count in top_apps)
top20_pct = (total_top20 / total_entries * 100) if total_entries > 0 else 0
print(f"\n  Top 20 apps account for: {total_top20:>6} ({top20_pct:.1f}%)")
print(f"  Unique apps total:       {len(app_counts)}")

print(f"\n5. LANGUAGE & CONTENT ANALYSIS")
print("-" * 100)
chinese_percentage = (chinese_count / total_entries * 100) if total_entries > 0 else 0
english_count = total_entries - chinese_count
english_percentage = 100 - chinese_percentage

print(f"  Entries with Chinese (CJK):  {chinese_count:>6} ({chinese_percentage:>5.1f}%)  (Target: 30-40%)")
print(f"  Entries without Chinese:     {english_count:>6} ({english_percentage:>5.1f}%)")

print(f"\n6. TEXT LENGTH STATISTICS")
print("-" * 100)
if title_lengths:
    avg_title = sum(title_lengths) / len(title_lengths)
    min_title = min(title_lengths)
    max_title = max(title_lengths)
    median_title = sorted(title_lengths)[len(title_lengths) // 2]
    print(f"  Title length:")
    print(f"    Average:  {avg_title:>6.1f} characters")
    print(f"    Median:   {median_title:>6} characters")
    print(f"    Range:    {min_title} - {max_title} characters")

if body_lengths:
    avg_body = sum(body_lengths) / len(body_lengths)
    min_body = min(body_lengths)
    max_body = max(body_lengths)
    median_body = sorted(body_lengths)[len(body_lengths) // 2]
    print(f"\n  Body length:")
    print(f"    Average:  {avg_body:>6.1f} characters")
    print(f"    Median:   {median_body:>6} characters")
    print(f"    Range:    {min_body} - {max_body} characters")

print(f"\n7. DATA QUALITY ISSUES")
print("-" * 100)
if errors:
    print(f"  Found {len(errors)} parsing error(s):\n")
    for error in errors:
        print(f"    - {error}")
else:
    print("  No parsing errors found - all entries are valid JSON!")

print("\n" + "=" * 100)
print("QUALITY ASSESSMENT vs TARGET DISTRIBUTIONS")
print("=" * 100)

issues = []
warnings = []

# Folder assessment
work_pct = (folder_counts['Work'] / total_entries * 100) if total_entries > 0 else 0
personal_pct = (folder_counts['Personal'] / total_entries * 100) if total_entries > 0 else 0
promotions_pct = (folder_counts['Promotions'] / total_entries * 100) if total_entries > 0 else 0
alerts_pct = (folder_counts['Alerts'] / total_entries * 100) if total_entries > 0 else 0

print("\nFOLDER BALANCE:")
if abs(work_pct - 35) > 10:
    issues.append(f"Work folder severely imbalanced: {work_pct:.1f}% (target: 35%, deviation: {work_pct - 35:+.1f}%)")
    print(f"  [!] Work: IMBALANCED")
elif abs(work_pct - 35) > 5:
    warnings.append(f"Work folder slightly off: {work_pct:.1f}% (target: 35%)")
    print(f"  [~] Work: SLIGHTLY OFF TARGET")
else:
    print(f"  [+] Work: OK ({work_pct:.1f}%)")

if personal_pct < 25 or personal_pct > 40:
    issues.append(f"Personal folder severely imbalanced: {personal_pct:.1f}% (target: 30-35%)")
    print(f"  [!] Personal: IMBALANCED")
elif personal_pct < 30 or personal_pct > 35:
    warnings.append(f"Personal folder slightly off: {personal_pct:.1f}% (target: 30-35%)")
    print(f"  [~] Personal: SLIGHTLY OFF TARGET")
else:
    print(f"  [+] Personal: OK ({personal_pct:.1f}%)")

if promotions_pct < 10 or promotions_pct > 25:
    issues.append(f"Promotions folder severely imbalanced: {promotions_pct:.1f}% (target: 15-20%)")
    print(f"  [!] Promotions: IMBALANCED")
elif promotions_pct < 15 or promotions_pct > 20:
    warnings.append(f"Promotions folder slightly off: {promotions_pct:.1f}% (target: 15-20%)")
    print(f"  [~] Promotions: SLIGHTLY OFF TARGET")
else:
    print(f"  [+] Promotions: OK ({promotions_pct:.1f}%)")

if abs(alerts_pct - 15) > 10:
    issues.append(f"Alerts folder severely imbalanced: {alerts_pct:.1f}% (target: 15%)")
    print(f"  [!] Alerts: IMBALANCED")
elif abs(alerts_pct - 15) > 5:
    warnings.append(f"Alerts folder slightly off: {alerts_pct:.1f}% (target: 15%)")
    print(f"  [~] Alerts: SLIGHTLY OFF TARGET")
else:
    print(f"  [+] Alerts: OK ({alerts_pct:.1f}%)")

# Priority assessment
print("\nPRIORITY BALANCE:")
p2_pct = (priority_counts[2] / total_entries * 100) if total_entries > 0 else 0
p3_pct = (priority_counts[3] / total_entries * 100) if total_entries > 0 else 0
p5_pct = (priority_counts[5] / total_entries * 100) if total_entries > 0 else 0
p2_p3_combined = p2_pct + p3_pct

if p2_p3_combined < 40:
    issues.append(f"P2+P3 too low: {p2_p3_combined:.1f}% (should be >50%)")
    print(f"  [!] P2+P3: TOO LOW ({p2_p3_combined:.1f}%)")
elif p2_p3_combined < 50:
    warnings.append(f"P2+P3 slightly low: {p2_p3_combined:.1f}% (should be >50%)")
    print(f"  [~] P2+P3: SLIGHTLY LOW ({p2_p3_combined:.1f}%)")
else:
    print(f"  [+] P2+P3: OK ({p2_p3_combined:.1f}%)")

if p5_pct >= 20:
    issues.append(f"Too many P5 entries: {p5_pct:.1f}% (target: <15%)")
    print(f"  [!] P5: TOO HIGH ({p5_pct:.1f}%)")
elif p5_pct >= 15:
    warnings.append(f"P5 slightly high: {p5_pct:.1f}% (target: <15%)")
    print(f"  [~] P5: SLIGHTLY HIGH ({p5_pct:.1f}%)")
else:
    print(f"  [+] P5: OK ({p5_pct:.1f}%)")

# Chinese content assessment
print("\nCONTENT DIVERSITY:")
if chinese_percentage < 20 or chinese_percentage > 50:
    issues.append(f"Chinese content severely imbalanced: {chinese_percentage:.1f}% (target: 30-40%)")
    print(f"  [!] Chinese content: IMBALANCED ({chinese_percentage:.1f}%)")
elif chinese_percentage < 30 or chinese_percentage > 40:
    warnings.append(f"Chinese content slightly off: {chinese_percentage:.1f}% (target: 30-40%)")
    print(f"  [~] Chinese content: SLIGHTLY OFF TARGET ({chinese_percentage:.1f}%)")
else:
    print(f"  [+] Chinese content: OK ({chinese_percentage:.1f}%)")

# Final summary
print("\n" + "=" * 100)
print("FINAL SUMMARY")
print("=" * 100)

if not issues and not warnings:
    print("\n  *** EXCELLENT! All distributions are within target ranges! ***")
elif not issues:
    print(f"\n  GOOD! No critical issues found. {len(warnings)} minor warning(s):")
    for i, warning in enumerate(warnings, 1):
        print(f"    {i}. {warning}")
else:
    print(f"\n  ATTENTION NEEDED! Found {len(issues)} critical issue(s) and {len(warnings)} warning(s):")
    print("\n  Critical Issues:")
    for i, issue in enumerate(issues, 1):
        print(f"    {i}. {issue}")
    if warnings:
        print("\n  Warnings:")
        for i, warning in enumerate(warnings, 1):
            print(f"    {i}. {warning}")

print("\n  Recommendations:")
if personal_pct < 30:
    print(f"    - Generate more Personal folder entries (need +{int((30 - personal_pct) * total_entries / 100)} entries)")
if chinese_percentage < 30:
    shortage = int((30 - chinese_percentage) * total_entries / 100)
    print(f"    - Add more Chinese language content (need +{shortage} entries with Chinese text)")
if work_pct > 40:
    print(f"    - Reduce Work folder entries in future batches")

print("\n" + "=" * 100)
