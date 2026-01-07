#!/usr/bin/env python3
"""Quick test of base Qwen3 on notification classification."""

import json
from pathlib import Path
from llama_cpp import Llama

# Load model
MODEL_PATH = Path("E:/projects/notif/models/Qwen3-0.6B-Q5_K_M.gguf")

print("Loading model...")
llm = Llama(
    model_path=str(MODEL_PATH),
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0,  # CPU only
    verbose=False
)
print("Model loaded!\n")

# Test on 10 examples
print("Testing on 10 notification examples...")
print("="*70)

with open("E:/projects/notif/training_data.jsonl", 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 10:
            break

        example = json.loads(line)
        notif = example["notification"]
        expected = example["classification"]

        # Build prompt - simpler format
        prompt = f"""Classify this notification into a folder.

Folders: Work, Personal, Promotions, Alerts

App: {notif['app_display_name']}
Title: {notif['title']}
Body: {notif['body']}

Output only JSON: {{"folder": "...", "priority": 1-5}}
JSON:"""

        # Run inference
        response = llm(prompt, max_tokens=30, temperature=0.0, stop=["\n", "}"])
        output = response["choices"][0]["text"]

        # Handle Unicode for Chinese text
        try:
            title_display = notif['title'][:50]
            app_display = notif['app_display_name']
        except:
            title_display = notif['title'][:50].encode('ascii', 'ignore').decode('ascii')
            app_display = notif['app_display_name'].encode('ascii', 'ignore').decode('ascii')

        print(f"\n[Example {i+1}]")
        print(f"App: {app_display}")
        print(f"Title: {title_display}")
        print(f"Expected: {expected['folder']} (P{expected['priority']})")
        print(f"Predicted: {output.strip()}")
        print("-"*70)

print("\n✓ Test complete")
