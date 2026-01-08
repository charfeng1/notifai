# Model Download Instructions

## Qwen3-0.6B GGUF Model

The Android app uses Qwen3-0.6B quantized to Q5_K_M format (~424MB).

### Option 1: Download Pre-Quantized (Recommended)

```bash
# Install Hugging Face CLI
pip install huggingface-hub

# Download Q5_K_M model
hf download unsloth/Qwen3-0.6B-GGUF Qwen3-0.6B-Q5_K_M.gguf --local-dir ./models

# Copy to Android project
cp models/Qwen3-0.6B-Q5_K_M.gguf android/app/src/main/assets/models/
```

### Option 2: Convert from Base Model

If you want to convert the base model yourself:

```bash
# 1. Clone llama.cpp
cd E:/projects/functiongemma-finetune
git clone https://github.com/ggerganov/llama.cpp.git

# 2. Build llama-quantize
cd llama.cpp
cmake -B build
cmake --build build --config Release

# 3. Convert safetensors to GGUF F16
python convert_hf_to_gguf.py ../qwen3-0.6b --outfile qwen3-0.6b-f16.gguf

# 4. Quantize to Q5_K_M
./build/bin/llama-quantize qwen3-0.6b-f16.gguf qwen3-0.6b-q5_k_m.gguf Q5_K_M

# 5. Copy to notifai project
cp qwen3-0.6b-q5_k_m.gguf E:/projects/notif/models/Qwen3-0.6B-Q5_K_M.gguf
```

## Model Specs

- **Size**: ~424MB (Q5_K_M quantization)
- **Format**: GGUF (llama.cpp compatible)
- **Source**: [unsloth/Qwen3-0.6B-GGUF](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF)
- **Base Model**: [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B)

## Why This Model?

- **Small enough** for on-device Android inference
- **Fast** on Pixel 7 Pro CPU (~500-800ms per classification)
- **Q5_K_M** provides good balance of size vs quality
- **GGUF format** works with llama.cpp (supports GBNF grammars)

## Note

This model file is **not committed to git** (too large). Download it locally before building the Android app.
