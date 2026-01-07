import json
import os
import re
import sys
from collections import Counter

# Set UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get all batch files
data_dir = r"E:\projects\notif\data"
batch_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.jsonl')])

# Initialize counters
total_entries = 0
folder_counts = Counter()
priority_counts = Counter()
cjk_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff]')
chinese_count = 0

# Process files
for batch_file in batch_files:
    filepath = os.path.join(data_dir, batch_file)
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                total_entries += 1

                notification = entry.get('notification', {})
                classification = entry.get('classification', {})

                folder_counts[classification.get('folder', 'Unknown')] += 1
                priority_counts[classification.get('priority', 'Unknown')] += 1

                title = notification.get('title', '')
                body = notification.get('body', '')
                if cjk_pattern.search(title) or cjk_pattern.search(body):
                    chinese_count += 1

            except:
                pass

def create_bar(percentage, width=50, target_min=None, target_max=None):
    """Create a visual bar chart with target indicators"""
    filled = int(percentage / 100 * width)
    bar = '█' * filled + '░' * (width - filled)

    # Add target indicator
    indicator = ""
    if target_min is not None and target_max is not None:
        if percentage < target_min:
            indicator = " ⬇ BELOW TARGET"
        elif percentage > target_max:
            indicator = " ⬆ ABOVE TARGET"
        else:
            indicator = " ✓ ON TARGET"

    return f"{bar} {percentage:5.1f}%{indicator}"

print("=" * 100)
print("VISUAL DISTRIBUTION ANALYSIS")
print("=" * 100)

# Folder Distribution
print("\n1. FOLDER DISTRIBUTION")
print("-" * 100)
folders = [
    ('Work', 35, 35, 'Work'),
    ('Personal', 30, 35, 'Personal'),
    ('Promotions', 15, 20, 'Promotions'),
    ('Alerts', 15, 15, 'Alerts')
]

for name, target_min, target_max, key in folders:
    count = folder_counts[key]
    pct = (count / total_entries * 100) if total_entries > 0 else 0
    print(f"\n  {name:<12} ({count:>5} entries)")
    print(f"  {create_bar(pct, 50, target_min, target_max)}")
    print(f"  Target: {target_min}{'%' if target_min == target_max else f'-{target_max}%'}")

# Priority Distribution
print("\n\n2. PRIORITY DISTRIBUTION")
print("-" * 100)
for priority in [1, 2, 3, 4, 5]:
    count = priority_counts[priority]
    pct = (count / total_entries * 100) if total_entries > 0 else 0
    print(f"\n  Priority {priority}  ({count:>5} entries)")
    print(f"  {create_bar(pct, 50)}")

# P2+P3 combined
p2_p3_count = priority_counts[2] + priority_counts[3]
p2_p3_pct = (p2_p3_count / total_entries * 100) if total_entries > 0 else 0
print(f"\n  P2+P3 Combined  ({p2_p3_count:>5} entries)")
print(f"  {create_bar(p2_p3_pct, 50, 50, 100)}")
print(f"  Target: >50%")

# Language Distribution
print("\n\n3. LANGUAGE DISTRIBUTION")
print("-" * 100)
chinese_pct = (chinese_count / total_entries * 100) if total_entries > 0 else 0
english_pct = 100 - chinese_pct

print(f"\n  Chinese (CJK)  ({chinese_count:>5} entries)")
print(f"  {create_bar(chinese_pct, 50, 30, 40)}")
print(f"  Target: 30-40%")

print(f"\n  English/Other  ({total_entries - chinese_count:>5} entries)")
print(f"  {create_bar(english_pct, 50)}")

# Summary comparison
print("\n\n4. TARGET COMPLIANCE SUMMARY")
print("-" * 100)
print("\n  Metric                    Actual    Target      Status")
print("  " + "-" * 70)

work_pct = (folder_counts['Work'] / total_entries * 100) if total_entries > 0 else 0
personal_pct = (folder_counts['Personal'] / total_entries * 100) if total_entries > 0 else 0
promotions_pct = (folder_counts['Promotions'] / total_entries * 100) if total_entries > 0 else 0
alerts_pct = (folder_counts['Alerts'] / total_entries * 100) if total_entries > 0 else 0

def status(actual, target_min, target_max):
    if actual < target_min - 10 or actual > target_max + 10:
        return "⚠ IMBALANCED"
    elif actual < target_min or actual > target_max:
        return "~ Slightly Off"
    else:
        return "✓ Good"

print(f"  Work Folder            {work_pct:6.1f}%    35.0%       {status(work_pct, 30, 40)}")
print(f"  Personal Folder        {personal_pct:6.1f}%    30-35%      {status(personal_pct, 30, 35)}")
print(f"  Promotions Folder      {promotions_pct:6.1f}%    15-20%      {status(promotions_pct, 15, 20)}")
print(f"  Alerts Folder          {alerts_pct:6.1f}%    15.0%       {status(alerts_pct, 10, 20)}")
print(f"  P2+P3 Priority         {p2_p3_pct:6.1f}%    >50%        {status(p2_p3_pct, 50, 100)}")

p5_pct = (priority_counts[5] / total_entries * 100) if total_entries > 0 else 0
print(f"  P5 Priority            {p5_pct:6.1f}%    <15%        {status(p5_pct, 0, 15)}")
print(f"  Chinese Content        {chinese_pct:6.1f}%    30-40%      {status(chinese_pct, 30, 40)}")

print("\n" + "=" * 100)
print("END OF REPORT")
print("=" * 100)
