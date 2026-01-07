#!/usr/bin/env python3
"""
Convert notification dataset to official FunctionGemma format.
Uses apply_chat_template with tools parameter as per Google's documentation.

This version uses 3-level priority system:
- Priority 1: Low (can ignore/check later)
- Priority 2: Medium (normal daily notifications)
- Priority 3: High (requires immediate attention)
"""

import json
from pathlib import Path

def classify_notification(app_name: str, title: str, body: str, folder: str = None, priority: int = None):
    """
    Classify a notification into a folder and priority level.

    Args:
        app_name: The name of the app that sent the notification
        title: The notification title
        body: The notification body/content
        folder: One of: Work, Personal, Promotions, Alerts
        priority: Priority level from 1 (low) to 3 (high)

    Returns:
        A dictionary with folder and priority
    """
    return {"folder": folder, "priority": priority}

# Tool definition for FunctionGemma
TOOLS = [classify_notification]

def convert_example(example):
    """Convert a notification example to FunctionGemma format."""
    notif = example["notification"]
    classification = example["classification"]

    # Get app name (handle typo in data: app_disable_name -> app_display_name)
    app_name = notif.get('app_display_name') or notif.get('app_disable_name') or notif.get('app', 'Unknown')

    # User message
    user_content = f"""App: {app_name}
Title: {notif['title']}
Body: {notif['body']}"""

    # Expected function call
    function_call = f"call:classify_notification{{app_name:<escape>{app_name}<escape>,title:<escape>{notif['title']}<escape>,body:<escape>{notif['body']}<escape>,folder:<escape>{classification['folder']}<escape>,priority:<escape>{classification['priority']}<escape>}}"

    # Message format for training
    messages = [
        {"role": "user", "content": user_content},
        {"role": "model", "content": f"<start_function_call>{function_call}<end_function_call>"}
    ]

    return {
        "messages": messages
        # Note: tools will be passed during training via apply_chat_template, not stored in JSONL
    }

def main():
    # Load training data (3-level priority remapped)
    input_file = Path(__file__).parent.parent / "training_data_3level.jsonl"
    train_file = Path(__file__).parent.parent / "functiongemma_train_3level.jsonl"
    test_file = Path(__file__).parent.parent / "functiongemma_test_3level.jsonl"

    print("="*70)
    print("CONVERT TO FUNCTIONGEMMA FORMAT (3-LEVEL PRIORITY)")
    print("="*70)
    print()

    print(f"Loading data from {input_file}...")

    examples = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples")

    # Split: 8000 for training, rest for testing
    train_count = 8000
    train_examples = examples[:train_count]
    test_examples = examples[train_count:]

    print(f"Training set: {len(train_examples)} examples")
    print(f"Test set: {len(test_examples)} examples")

    # Convert training set
    print()
    print("Converting training set...")
    train_converted = []
    for i, example in enumerate(train_examples):
        if i % 1000 == 0 and i > 0:
            print(f"  Processed {i}/{len(train_examples)}...")
        try:
            train_converted.append(convert_example(example))
        except Exception as e:
            print(f"Error on example {i}: {e}")
            print(f"Example: {example}")
            raise

    # Convert test set
    print("Converting test set...")
    test_converted = []
    for i, example in enumerate(test_examples):
        try:
            test_converted.append(convert_example(example))
        except Exception as e:
            print(f"Error on example {i}: {e}")
            raise

    # Save training set
    print()
    print(f"Saving training set to {train_file}...")
    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_converted:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    # Save test set
    print(f"Saving test set to {test_file}...")
    with open(test_file, 'w', encoding='utf-8') as f:
        for item in test_converted:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print()
    print("="*70)
    print("[OK] CONVERSION COMPLETE")
    print("="*70)
    print(f"Training: {len(train_converted)} examples -> {train_file}")
    print(f"Test:     {len(test_converted)} examples -> {test_file}")
    print()
    print("Example output:")
    print(json.dumps(train_converted[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
