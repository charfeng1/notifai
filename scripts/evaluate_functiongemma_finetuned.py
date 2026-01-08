#!/usr/bin/env python3
"""
Evaluate fine-tuned FunctionGemma on test set.
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import json
import re
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

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
    print("EVALUATE FINE-TUNED FUNCTIONGEMMA")
    print("="*70)
    print()

    # Load model
    print(f"Loading base model from {BASE_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(FINETUNED_MODEL)

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    print(f"Loading LoRA adapters from {FINETUNED_MODEL}...")
    model = PeftModel.from_pretrained(base_model, FINETUNED_MODEL)
    model.eval()

    print(f"Model loaded on: {model.device}")
    print()

    # Load test data
    print(f"Loading test data from {TEST_FILE}...")
    examples = []
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 6000:  # Skip training data
                examples.append(json.loads(line))
            if len(examples) >= TEST_SIZE:
                break

    print(f"Testing on {len(examples)} examples")
    print()
    print("="*70)
    print("RUNNING INFERENCE")
    print("="*70)
    print()

    # Test
    correct_folder = 0
    correct_priority = 0
    parse_failures = 0
    errors = []

    for i, example in enumerate(examples, 1):
        notif = example["notification"]
        expected = example["classification"]

        # Build user message
        user_content = f"""App: {notif['app_display_name']}
Title: {notif['title']}
Body: {notif['body']}"""

        messages = [
            {"role": "user", "content": user_content}
        ]

        # Apply chat template with tools
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

        # Parse
        predicted_folder, predicted_priority = parse_function_call(response)

        if not predicted_folder:
            parse_failures += 1
            errors.append({
                "example": i,
                "app": notif["app_display_name"],
                "title": notif["title"][:50],
                "expected": expected,
                "output": response[:100],
                "error": "Parse failure"
            })
        else:
            if predicted_folder == expected["folder"]:
                correct_folder += 1
            else:
                errors.append({
                    "example": i,
                    "app": notif["app_display_name"],
                    "title": notif["title"][:50],
                    "expected_folder": expected["folder"],
                    "predicted_folder": predicted_folder
                })

            if predicted_priority == expected["priority"]:
                correct_priority += 1

        # Progress
        if i % 10 == 0:
            print(f"Progress: {i}/{len(examples)} ({i/len(examples)*100:.0f}%)")

    # Results
    total = len(examples)
    print()
    print("="*70)
    print("RESULTS")
    print("="*70)
    print()
    print(f"Total examples:     {total}")
    print(f"Folder accuracy:    {correct_folder}/{total} ({correct_folder/total*100:.1f}%)")
    print(f"Priority accuracy:  {correct_priority}/{total} ({correct_priority/total*100:.1f}%)")
    print(f"Parse failures:     {parse_failures}/{total} ({parse_failures/total*100:.1f}%)")
    print()

    # Show errors
    if errors:
        print("Sample Errors (first 10):")
        print("-"*70)
        for err in errors[:10]:
            try:
                if "error" in err:
                    print(f"\n[{err['example']}] {err['app']} - {err['title']}")
                    print(f"  Error: {err['error']}")
                    print(f"  Output: {err['output']}")
                else:
                    print(f"\n[{err['example']}] {err['app']} - {err['title']}")
                    print(f"  Expected: {err['expected_folder']}")
                    print(f"  Predicted: {err['predicted_folder']}")
            except UnicodeEncodeError:
                print(f"\n[{err['example']}] (Unicode error)")
                continue

    print()
    print("="*70)
    print("COMPARISON")
    print("="*70)
    print()
    print("Baseline (before fine-tuning):  35% folder accuracy")
    print(f"Fine-tuned (after training):    {correct_folder/total*100:.1f}% folder accuracy")
    print(f"Improvement:                    +{(correct_folder/total*100 - 35):.1f} percentage points")
    print()

    # Save results
    results = {
        "model": FINETUNED_MODEL,
        "total": total,
        "folder_accuracy": correct_folder / total,
        "priority_accuracy": correct_priority / total,
        "parse_failure_rate": parse_failures / total,
        "errors": errors[:20]
    }

    output_path = Path(__file__).parent.parent / "functiongemma_finetuned_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")
    print()
    print("="*70)

if __name__ == "__main__":
    main()
