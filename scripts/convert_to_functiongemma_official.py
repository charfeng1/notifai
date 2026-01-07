#!/usr/bin/env python3
"""
Convert notification dataset to official FunctionGemma format.
Uses apply_chat_template with tools parameter as per Google's documentation.
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
        priority: Priority level from 1 (ignore) to 5 (urgent)

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
    # Load training data
    input_file = Path(__file__).parent.parent / "training_data.jsonl"
    output_file = Path(__file__).parent.parent / "functiongemma_train.jsonl"

    print(f"Loading data from {input_file}...")

    examples = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples")

    # Limit to 6000 for testing
    examples = examples[:6000]
    print(f"Using first 6000 examples for training")

    # Convert
    print("Converting to FunctionGemma format...")
    converted = []
    for i, example in enumerate(examples):
        if i % 1000 == 0:
            print(f"  Processed {i}/{len(examples)}...")
        try:
            converted.append(convert_example(example))
        except Exception as e:
            print(f"Error on example {i}: {e}")
            print(f"Example: {example}")
            raise

    # Save
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"[OK] Saved {len(converted)} examples")
    print()
    print("Example output:")
    print(json.dumps(converted[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
