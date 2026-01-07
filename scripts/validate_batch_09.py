import json

# Validate the generated data
valid_folders = {"Work", "Personal", "Promotions", "Alerts"}
errors = []
total_lines = 0
ids_seen = set()
folders_count = {f: 0 for f in valid_folders}
priority_count = {i: 0 for i in range(1, 6)}

with open("E:/projects/notif/data/batch_09.jsonl", 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        total_lines += 1
        try:
            entry = json.loads(line)

            # Check required fields
            if "id" not in entry:
                errors.append(f"Line {line_num}: Missing 'id'")
            else:
                entry_id = entry["id"]
                if entry_id in ids_seen:
                    errors.append(f"Line {line_num}: Duplicate ID '{entry_id}'")
                ids_seen.add(entry_id)

            if "notification" not in entry:
                errors.append(f"Line {line_num}: Missing 'notification'")
            if "classification" not in entry:
                errors.append(f"Line {line_num}: Missing 'classification'")

            # Check notification structure
            notif = entry.get("notification", {})
            if "app" not in notif:
                errors.append(f"Line {line_num}: Missing 'notification.app'")
            if "app_display_name" not in notif:
                errors.append(f"Line {line_num}: Missing 'notification.app_display_name'")
            if "title" not in notif:
                errors.append(f"Line {line_num}: Missing 'notification.title'")
            if "body" not in notif:
                errors.append(f"Line {line_num}: Missing 'notification.body'")

            # Check classification structure
            classif = entry.get("classification", {})
            if "folder" not in classif:
                errors.append(f"Line {line_num}: Missing 'classification.folder'")
            else:
                folder = classif["folder"]
                if folder not in valid_folders:
                    errors.append(f"Line {line_num}: Invalid folder '{folder}'")
                else:
                    folders_count[folder] += 1

            if "priority" not in classif:
                errors.append(f"Line {line_num}: Missing 'classification.priority'")
            else:
                priority = classif["priority"]
                if not isinstance(priority, int) or priority < 1 or priority > 5:
                    errors.append(f"Line {line_num}: Invalid priority '{priority}'")
                else:
                    priority_count[priority] += 1

        except json.JSONDecodeError as e:
            errors.append(f"Line {line_num}: JSON parse error: {e}")

print(f"Validation Results:")
print(f"Total entries: {total_lines}")
print(f"Validation errors: {len(errors)}")
if errors:
    print("\nErrors found:")
    for error in errors[:20]:
        print(f"  {error}")
    if len(errors) > 20:
        print(f"  ... and {len(errors) - 20} more errors")
else:
    print("[OK] All entries are valid!")

print(f"\nFolder Distribution:")
for folder in sorted(folders_count.keys()):
    count = folders_count[folder]
    pct = (count / total_lines) * 100
    print(f"  {folder}: {count} ({pct:.1f}%)")

print(f"\nPriority Distribution:")
for p in range(1, 6):
    count = priority_count[p]
    pct = (count / total_lines) * 100
    print(f"  Priority {p}: {count} ({pct:.1f}%)")

print(f"\nUnique IDs: {len(ids_seen)}")
print(f"ID Range: {min(ids_seen)} to {max(ids_seen)}")
