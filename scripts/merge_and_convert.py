#!/usr/bin/env python3
"""
Merge LoRA adapter with base model and convert to GGUF.
"""

import os
import sys
import subprocess
from pathlib import Path

# Paths
BASE_MODEL = Path("E:/projects/functiongemma-finetune/qwen3-0.6b")
LORA_ADAPTER = Path("E:/projects/functiongemma-finetune/notif-3level/qwen3-finetuned")
MERGED_OUTPUT = Path("E:/projects/functiongemma-finetune/notif-3level/qwen3-merged")
LLAMA_CPP = Path("E:/projects/notif/llama.cpp")
GGUF_OUTPUT = Path("E:/projects/notif/android/app/src/main/assets/models")

def merge_lora():
    """Merge LoRA adapter with base model."""
    print("=" * 60)
    print("Step 1: Merging LoRA adapter with base model")
    print("=" * 60)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch

    print(f"Loading base model from {BASE_MODEL}...")
    base_model = AutoModelForCausalLM.from_pretrained(
        str(BASE_MODEL),
        torch_dtype=torch.float16,
        device_map="cpu"
    )

    print(f"Loading LoRA adapter from {LORA_ADAPTER}...")
    model = PeftModel.from_pretrained(base_model, str(LORA_ADAPTER))

    print("Merging weights...")
    merged_model = model.merge_and_unload()

    print(f"Saving merged model to {MERGED_OUTPUT}...")
    MERGED_OUTPUT.mkdir(parents=True, exist_ok=True)
    merged_model.save_pretrained(str(MERGED_OUTPUT))

    # Also save tokenizer
    print("Saving tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(str(LORA_ADAPTER))
    tokenizer.save_pretrained(str(MERGED_OUTPUT))

    print("Merge complete!")
    return MERGED_OUTPUT

def convert_to_gguf(merged_path: Path):
    """Convert merged model to GGUF format."""
    print("\n" + "=" * 60)
    print("Step 2: Converting to GGUF format")
    print("=" * 60)

    convert_script = LLAMA_CPP / "convert_hf_to_gguf.py"
    output_file = merged_path / "qwen3-notif-f16.gguf"

    cmd = [
        sys.executable,
        str(convert_script),
        str(merged_path),
        "--outfile", str(output_file),
        "--outtype", "f16"
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)

    print(result.stdout)
    print(f"GGUF file created: {output_file}")
    return output_file

def quantize(gguf_file: Path, quant_type: str = "Q5_K_M"):
    """Quantize GGUF model."""
    print("\n" + "=" * 60)
    print(f"Step 3: Quantizing to {quant_type}")
    print("=" * 60)

    # Find quantize executable
    quantize_exe = LLAMA_CPP / "build" / "bin" / "llama-quantize"
    if not quantize_exe.exists():
        quantize_exe = LLAMA_CPP / "llama-quantize"
    if not quantize_exe.exists():
        # Try building
        print("Quantize executable not found. You may need to build llama.cpp first.")
        print("Skipping quantization - using F16 model.")
        return gguf_file

    output_file = gguf_file.parent / f"Qwen3-0.6B-notif-{quant_type}.gguf"

    cmd = [str(quantize_exe), str(gguf_file), str(output_file), quant_type]
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return gguf_file

    print(result.stdout)
    print(f"Quantized model: {output_file}")
    return output_file

def deploy_to_android(model_file: Path):
    """Copy model to Android assets."""
    print("\n" + "=" * 60)
    print("Step 4: Deploying to Android assets")
    print("=" * 60)

    GGUF_OUTPUT.mkdir(parents=True, exist_ok=True)
    dest = GGUF_OUTPUT / model_file.name

    import shutil
    shutil.copy2(model_file, dest)
    print(f"Copied to: {dest}")
    print(f"Size: {dest.stat().st_size / 1024 / 1024:.1f} MB")

def main():
    print("Qwen3 LoRA -> GGUF Conversion Pipeline")
    print("=" * 60)

    # Check paths
    if not BASE_MODEL.exists():
        print(f"Error: Base model not found at {BASE_MODEL}")
        sys.exit(1)
    if not LORA_ADAPTER.exists():
        print(f"Error: LoRA adapter not found at {LORA_ADAPTER}")
        sys.exit(1)

    # Step 1: Merge LoRA
    merged_path = merge_lora()

    # Step 2: Convert to GGUF
    gguf_file = convert_to_gguf(merged_path)

    # Step 3: Quantize
    quantized_file = quantize(gguf_file, "Q5_K_M")

    # Step 4: Deploy
    deploy_to_android(quantized_file)

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"\nFinal model: {quantized_file}")
    print("\nNext steps:")
    print("1. Update LlamaClassifier.kt MODEL_FILENAME if needed")
    print("2. Rebuild and test the app")

if __name__ == "__main__":
    main()
