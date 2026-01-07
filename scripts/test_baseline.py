#!/usr/bin/env python3
"""Test base Qwen3-0.6B on notification classification - save results to JSON."""

import json
from pathlib import Path
from llama_cpp import Llama

# Load model
MODEL_PATH = Path("E:/projects/notif/models/Qwen3-0.6B-Q5_K_M.gguf")

print("Loading Qwen3-0.6B Q5_K_M model...")
llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0,
    verbose=False
)
print("Model loaded!\n")

# Test on 50 examples
SAMPLE_SIZE = 50
results = []

print(f"Testing on {SAMPLE_SIZE} notification examples...")

with open("E:/projects/notif/training_data.jsonl", 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= SAMPLE_SIZE:
            break

        example = json.loads(line)
        notif = example["notification"]
        expected = example["classification"]

        # Build prompt with proper Qwen3 chat template
        prompt = f"""<|im_start|>system
You are a helpful assistant that classifies notifications into folders.

Available folders:
- Work: Professional messages from work apps like Slack, Teams, email
- Personal: Messages from friends and family via WeChat, WhatsApp, Telegram
- Promotions: Marketing, deals, sales, promotional content
- Alerts: Banking, security, delivery updates, transactional messages

Output format: {{"folder": "Work|Personal|Promotions|Alerts", "priority": 1-5}}
Priority: 1=ignore, 2=low, 3=normal, 4=important, 5=urgent

Respond with ONLY the JSON object, nothing else.<|im_end|>
<|im_start|>user
App: {notif['app_display_name']}
Title: {notif['title']}
Body: {notif['body']}<|im_end|>
<|im_start|>assistant
"""

        # Run inference
        response = llm(prompt, max_tokens=40, temperature=0.0, stop=["}"])
        output = response["choices"][0]["text"] + "}"  # Add closing brace

        # Parse
        try:
            parsed = json.loads(output.strip())
            predicted_folder = parsed.get("folder", "Unknown")
            predicted_priority = parsed.get("priority", 0)
            parse_ok = True
        except:
            predicted_folder = "ParseError"
            predicted_priority = 0
            parse_ok = False

        # Check correctness
        folder_correct = (predicted_folder == expected["folder"])
        priority_correct = (predicted_priority == expected["priority"])

        results.append({
            "example_id": i + 1,
            "app": notif["app_display_name"],
            "title": notif["title"][:80],
            "expected_folder": expected["folder"],
            "predicted_folder": predicted_folder,
            "expected_priority": expected["priority"],
            "predicted_priority": predicted_priority,
            "folder_correct": folder_correct,
            "priority_correct": priority_correct,
            "parse_ok": parse_ok,
            "raw_output": output.strip()[:100]
        })

        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{SAMPLE_SIZE}")

# Calculate stats
total = len(results)
folder_correct = sum(1 for r in results if r["folder_correct"])
priority_correct = sum(1 for r in results if r["priority_correct"])
parse_ok = sum(1 for r in results if r["parse_ok"])

summary = {
    "model": "Qwen3-0.6B-Q5_K_M (base, no fine-tuning)",
    "total_examples": total,
    "folder_accuracy": f"{folder_correct/total*100:.1f}%",
    "priority_accuracy": f"{priority_correct/total*100:.1f}%",
    "parse_success_rate": f"{parse_ok/total*100:.1f}%",
    "folder_correct_count": folder_correct,
    "priority_correct_count": priority_correct,
    "parse_failures": total - parse_ok,
    "results": results
}

# Save to file
output_file = Path("E:/projects/notif/baseline_test_results.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"\n{'='*70}")
print("RESULTS")
print(f"{'='*70}")
print(f"Total examples: {total}")
print(f"Folder accuracy: {folder_correct}/{total} ({folder_correct/total*100:.1f}%)")
print(f"Priority accuracy: {priority_correct}/{total} ({priority_correct/total*100:.1f}%)")
print(f"Parse success: {parse_ok}/{total} ({parse_ok/total*100:.1f}%)")
print(f"\nResults saved to: {output_file}")
print(f"{'='*70}")
