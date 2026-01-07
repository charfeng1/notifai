#!/usr/bin/env python3
"""
Test Qwen3-0.6B base model on notification classification.
Uses transformers library with GPU acceleration (same as functiongemma-finetune).
"""

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import json
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configuration
BASE_MODEL = str(Path(__file__).parent.parent / "models" / "qwen3-0.6b")  # Use Qwen3 0.6B (same as functiongemma project)
DATASET_PATH = Path(__file__).parent.parent / "training_data.jsonl"
SAMPLE_SIZE = 100

def build_messages(app_name, title, body):
    """Build chat messages for classification."""
    system_prompt = """You classify notifications into folders.

Folders:
[Work]: Professional messages from work apps like Slack, Jira, Teams, work email, Feishu, DingTalk
[Personal]: Messages from friends and family via WhatsApp, WeChat, Telegram, Douyin, RedNote
[Promotions]: Marketing, deals, spam, promotional content from shopping and service apps
[Alerts]: Banking, security, system notifications, delivery updates, transactional messages

Output JSON only: {"folder": "...", "priority": 1-5}
Priority: 1=ignore, 2=low, 3=normal, 4=important, 5=urgent
/no_think"""

    user_message = f"""App: {app_name}
Title: {title}
Body: {body}"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

def parse_response(text):
    """Extract folder and priority from response."""
    try:
        # Find JSON in response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = text[start:end]
            data = json.loads(json_str)
            return data.get("folder"), data.get("priority")
    except:
        pass
    return None, None

def main():
    print("="*70)
    print("BASELINE TEST: Qwen3-0.6B Base Model (NO FINE-TUNING)")
    print("="*70)
    print()

    # Load model
    print(f"Loading model: {BASE_MODEL}")
    print("This will download ~1GB if not cached...")
    print()

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto"  # Automatic GPU usage!
    )
    model.eval()

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    print(f"Model loaded on: {model.device}")
    print(f"Memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    print()

    # Load dataset
    print(f"Loading {SAMPLE_SIZE} examples from {DATASET_PATH}...")
    examples = []
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= SAMPLE_SIZE:
                break
            examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples")
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

        # Build messages
        messages = build_messages(
            notif["app_display_name"],
            notif["title"],
            notif["body"]
        )

        # Generate
        chat_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False  # Disable thinking mode for clean output
        )

        inputs = tokenizer([chat_text], return_tensors="pt", padding=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        response = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        # Parse
        predicted_folder, predicted_priority = parse_response(response)

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

    # Show sample errors
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
                print(f"\n[{err['example']}] (Unicode error in output)")
                continue

    print()
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    print()

    if correct_folder / total >= 0.80:
        print("[OK] Base model achieves >80% folder accuracy!")
        print("     Phase 1 baseline is viable without fine-tuning.")
    else:
        print("[NEEDS WORK] Base model accuracy below 80%")
        print("             Consider fine-tuning or better prompting")

    if parse_failures / total > 0.10:
        print()
        print("[WARNING] High parse failure rate (>10%)")
        print("          GBNF grammar will be critical")
    else:
        print()
        print("[OK] Low parse failure rate (<10%)")
        print("     Model generates valid JSON consistently")

    print()
    print("="*70)

    # Save results
    results = {
        "model": BASE_MODEL,
        "total": total,
        "folder_accuracy": correct_folder / total,
        "priority_accuracy": correct_priority / total,
        "parse_failure_rate": parse_failures / total,
        "errors": errors[:20]  # Save first 20 errors
    }

    output_path = Path(__file__).parent.parent / "baseline_test_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()
