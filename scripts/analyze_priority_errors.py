#!/usr/bin/env python3
"""
Analyze priority prediction errors.
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import json
import re
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from collections import Counter

# Configuration
BASE_MODEL = str(Path(__file__).parent.parent / "models" / "functiongemma-270m")
FINETUNED_MODEL = str(Path(__file__).parent.parent / "functiongemma-finetuned-notif")
TEST_FILE = Path(__file__).parent.parent / "training_data.jsonl"
TEST_SIZE = 100

# Tool definition
def classify_notification(app_name: str, title: str, body: str, folder: str = None, priority: int = None):
    """
    Classify a notification into a folder and priority level.

    Args:
        app_name: The name of the app that sent the notification
        title: The notification title
        body: The notification body/content
        folder: One of: Work, Personal, Promotions, Alerts
        priority: Priority level from 1 (ignore) to 5 (urgent)

    Returns:
        A dictionary with folder and priority
    """
    return {"folder": folder, "priority": priority}

TOOLS = [classify_notification]

def parse_function_call(text):
    """Parse function call from model output."""
    try:
        # Look for <start_function_call>...<end_function_call>
        if "<start_function_call>" not in text:
            return None, None

        start = text.find("<start_function_call>")
        end = text.find("<end_function_call>")
        if start < 0 or end < 0:
            return None, None

        call_text = text[start:end]

        # Extract folder
        folder_match = re.search(r'folder:<escape>([^<]+)<escape>', call_text)
        folder = folder_match.group(1) if folder_match else None

        # Extract priority
        priority_match = re.search(r'priority:<escape>(\d+)<escape>', call_text)
        priority = int(priority_match.group(1)) if priority_match else None

        return folder, priority
    except Exception as e:
        return None, None

def main():
    print("="*70)
    print("PRIORITY ANALYSIS")
    print("="*70)
    print()

    # Load model
    print(f"Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(FINETUNED_MODEL)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    model = PeftModel.from_pretrained(base_model, FINETUNED_MODEL)
    model.eval()

    # Load test data
    examples = []
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 6000:  # Skip training data
                examples.append(json.loads(line))
            if len(examples) >= TEST_SIZE:
                break

    print(f"Testing on {len(examples)} examples\n")

    # Analyze
    expected_priorities = []
    predicted_priorities = []
    priority_errors = []

    for i, example in enumerate(examples, 1):
        notif = example["notification"]
        expected = example["classification"]
        expected_priorities.append(expected["priority"])

        # Build user message
        user_content = f"""App: {notif['app_display_name']}
Title: {notif['title']}
Body: {notif['body']}"""

        messages = [{"role": "user", "content": user_content}]
        text = tokenizer.apply_chat_template(
            messages,
            tools=TOOLS,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=False)
        predicted_folder, predicted_priority = parse_function_call(response)

        if predicted_priority:
            predicted_priorities.append(predicted_priority)
        else:
            predicted_priorities.append(None)

        # Track errors
        if predicted_priority != expected["priority"]:
            priority_errors.append({
                "app": notif["app_display_name"],
                "title": notif["title"][:50],
                "expected": expected["priority"],
                "predicted": predicted_priority,
                "folder_correct": predicted_folder == expected["folder"]
            })

        if i % 10 == 0:
            print(f"Progress: {i}/{len(examples)}")

    # Analysis
    print("\n" + "="*70)
    print("PRIORITY DISTRIBUTION")
    print("="*70)

    expected_counts = Counter(expected_priorities)
    predicted_counts = Counter([p for p in predicted_priorities if p is not None])

    print("\nExpected priorities in test set:")
    for priority in sorted(expected_counts.keys()):
        print(f"  Priority {priority}: {expected_counts[priority]} examples")

    print("\nPredicted priorities:")
    for priority in sorted(predicted_counts.keys()):
        print(f"  Priority {priority}: {predicted_counts[priority]} predictions")

    print(f"\nNone/Parse failures: {predicted_priorities.count(None)}")

    # Error breakdown
    print("\n" + "="*70)
    print("ERROR ANALYSIS")
    print("="*70)
    print(f"\nTotal priority errors: {len(priority_errors)}")

    # Group by expected priority
    print("\nErrors by expected priority:")
    for priority in sorted(expected_counts.keys()):
        errors_for_priority = [e for e in priority_errors if e["expected"] == priority]
        if errors_for_priority:
            print(f"\n  Expected Priority {priority} ({len(errors_for_priority)} errors):")
            pred_counter = Counter([e["predicted"] for e in errors_for_priority])
            for pred, count in pred_counter.most_common():
                print(f"    Predicted as {pred}: {count} times")

    # Show sample errors
    print("\n" + "="*70)
    print("SAMPLE PRIORITY ERRORS")
    print("="*70)
    for i, err in enumerate(priority_errors[:15], 1):
        print(f"\n{i}. {err['app']} - {err['title']}")
        print(f"   Expected: {err['expected']}, Predicted: {err['predicted']}")
        print(f"   Folder correct: {err['folder_correct']}")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()
