#!/usr/bin/env python3
"""Quick GPU test."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

print("="*70)
print("GPU TEST")
print("="*70)
print()

print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print()

    print("Loading small model to test GPU...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen2.5-0.5B-Instruct",
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    print(f"Model device: {model.device}")
    print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    print()

    # Quick inference test
    messages = [{"role": "user", "content": "Hello!"}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=10)

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Quick inference test successful!")
    print(f"Response: {response[:100]}...")
    print()
    print("="*70)
    print("[SUCCESS] GPU is working correctly!")
    print("="*70)
else:
    print()
    print("="*70)
    print("[ERROR] CUDA not available!")
    print("="*70)
