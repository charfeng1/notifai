#!/usr/bin/env python3
"""
Analyze FunctionGemma baseline results for hallucinations.
"""

import json
from pathlib import Path

# Valid values
VALID_FOLDERS = {"Work", "Personal", "Promotions", "Alerts"}
VALID_PRIORITIES = {1, 2, 3, 4, 5}

# Load results
results_path = Path(__file__).parent.parent / "functiongemma_baseline_results.json"
with open(results_path, encoding='utf-8') as f:
    data = json.load(f)

print("="*70)
print("FUNCTIONGEMMA HALLUCINATION ANALYSIS")
print("="*70)
print()

hallucinated_folders = []
hallucinated_priorities = []

for err in data['errors']:
    if 'predicted_folder' in err:
        folder = err['predicted_folder']
        if folder not in VALID_FOLDERS:
            hallucinated_folders.append(err)

    if 'predicted_priority' in err:
        priority = err['predicted_priority']
        if priority not in VALID_PRIORITIES:
            hallucinated_priorities.append(err)

print(f"Checked {len(data['errors'])} errors...")
print()
print("="*70)
print("RESULTS")
print("="*70)
print()

if hallucinated_folders:
    print(f"[CRITICAL] Found {len(hallucinated_folders)} hallucinated folders!")
    print()
    for h in hallucinated_folders[:15]:
        try:
            print(f"  [{h['example']}] {h['app']} - {h['title']}")
            print(f"      Predicted: '{h['predicted_folder']}' (NOT IN VALID SET)")
            print(f"      Expected: '{h.get('expected_folder', 'N/A')}'")
            print()
        except UnicodeEncodeError:
            print(f"  [{h['example']}] (Unicode error)")
            continue
else:
    print("[OK] No hallucinated folders detected")

print()
print("="*70)
print("CONCLUSION")
print("="*70)
print()

if hallucinated_folders:
    print(f"[CRITICAL ISSUE] FunctionGemma-270M hallucinates folders!")
    print()
    print(f"  - Hallucination rate: {len(hallucinated_folders)}/{len(data['errors'])} errors contain hallucinations")
    print(f"  - These are folders NOT in {VALID_FOLDERS}")
    print()
    print("This means:")
    print("  - Model ignores the enum constraint in function declaration")
    print("  - Production deployment would break on invalid folder names")
    print("  - Needs GBNF grammar enforcement OR fine-tuning")
else:
    print("[OK] No hallucinations - model respects enum constraints")

print()
print("="*70)
