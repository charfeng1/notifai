#!/usr/bin/env python3
"""Test Qwen3-0.6B base model on notification classification dataset."""

import json
import sys
from pathlib import Path

try:
    from llama_cpp import Llama
except ImportError:
    print("Error: llama-cpp-python not installed")
    print("Install with: pip install llama-cpp-python")
    sys.exit(1)

# Load model
MODEL_PATH = Path("../models/Qwen3-0.6B-Q5_K_M.gguf")
if not MODEL_PATH.exists():
    print(f"Error: Model not found at {MODEL_PATH}")
    sys.exit(1)

print(f"Loading model from {MODEL_PATH}...")
print("This may take 10-30 seconds...")

llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0,  # CPU only
    verbose=False
)

print("Model loaded!\n")

# Test on sample of dataset
DATASET_PATH = Path("../training_data.jsonl")
SAMPLE_SIZE = 100

def build_prompt(app_name, title, body):
    """Build classification prompt."""
    return f"""<|im_start|>system
You classify notifications into folders.

Folders:
[Work]: Professional messages from work apps like Slack, Jira, Teams, work email, Feishu, DingTalk
[Personal]: Messages from friends and family via WhatsApp, WeChat, Telegram, Douyin, RedNote
[Promotions]: Marketing, deals, spam, promotional content from shopping and service apps
[Alerts]: Banking, security, system notifications, delivery updates, transactional messages

Output JSON only: {{"folder": "...", "priority": 1-5}}
Priority: 1=ignore, 2=low, 3=normal, 4=important, 5=urgent<|im_end|>
<|im_start|>user
App: {app_name}
Title: {title}
Body: {body}<|im_end|>
<|im_start|>assistant
"""

def extract_json(response):
    """Extract JSON from model response."""
    start = response.find("{")
    end = response.rfind("}") + 1
    if start >= 0 and end > start:
        return response[start:end]
    return None

def parse_classification(json_str):
    """Parse classification JSON."""
    try:
        data = json.loads(json_str)
        return data.get("folder"), data.get("priority")
    except:
        return None, None

# Load sample from dataset
print(f"Loading {SAMPLE_SIZE} examples from dataset...")
examples = []
with open(DATASET_PATH, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= SAMPLE_SIZE:
            break
        examples.append(json.loads(line))

print(f"Loaded {len(examples)} examples\n")
print("="*70)
print("TESTING BASE MODEL (NO FINE-TUNING)")
print("="*70)

# Test each example
correct_folder = 0
correct_priority = 0
parse_failures = 0
total = len(examples)

errors = []

for i, example in enumerate(examples, 1):
    notif = example["notification"]
    expected = example["classification"]

    # Build prompt
    prompt = build_prompt(
        notif["app_display_name"],
        notif["title"],
        notif["body"]
    )

    # Run inference
    response = llm(
        prompt,
        max_tokens=100,
        temperature=0.0,  # Greedy for deterministic output
        stop=["<|im_end|>"]
    )

    output = response["choices"][0]["text"]

    # Parse result
    json_str = extract_json(output)
    if not json_str:
        parse_failures += 1
        errors.append({
            "example": i,
            "expected": expected,
            "output": output,
            "error": "Failed to extract JSON"
        })
        continue

    predicted_folder, predicted_priority = parse_classification(json_str)

    if not predicted_folder:
        parse_failures += 1
        errors.append({
            "example": i,
            "expected": expected,
            "output": json_str,
            "error": "Failed to parse JSON"
        })
        continue

    # Check accuracy
    if predicted_folder == expected["folder"]:
        correct_folder += 1
    else:
        errors.append({
            "example": i,
            "app": notif["app_display_name"],
            "title": notif["title"][:50],
            "expected": expected["folder"],
            "predicted": predicted_folder
        })

    if predicted_priority == expected["priority"]:
        correct_priority += 1

    # Progress
    if i % 10 == 0:
        print(f"Progress: {i}/{total} ({i/total*100:.0f}%)")

# Results
print("\n" + "="*70)
print("RESULTS")
print("="*70)
print(f"\nTotal examples tested: {total}")
print(f"\nFolder Accuracy:   {correct_folder}/{total} ({correct_folder/total*100:.1f}%)")
print(f"Priority Accuracy: {correct_priority}/{total} ({correct_priority/total*100:.1f}%)")
print(f"Parse Failures:    {parse_failures}/{total} ({parse_failures/total*100:.1f}%)")

# Show errors
if errors:
    print(f"\n\nFirst 10 Errors:")
    print("-"*70)
    for err in errors[:10]:
        if "error" in err:
            print(f"\nExample {err['example']}: {err['error']}")
            print(f"  Expected: {err['expected']}")
            print(f"  Output: {err['output'][:100]}...")
        else:
            print(f"\nExample {err['example']}: {err['app']} - {err['title']}")
            print(f"  Expected: {err['expected']}")
            print(f"  Predicted: {err['predicted']}")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)

if correct_folder / total >= 0.80:
    print("\n✓ Base model achieves >80% accuracy!")
    print("  Phase 1 baseline is viable without fine-tuning.")
else:
    print("\n⚠ Base model accuracy is below 80%")
    print("  Consider: fine-tuning, better prompting, or GBNF constraints")

if parse_failures / total > 0.10:
    print("\n⚠ High parse failure rate (>10%)")
    print("  GBNF grammar will be critical for Phase 2")
else:
    print("\n✓ Low parse failure rate")
    print("  Model generates valid JSON consistently")

print("\n" + "="*70)
