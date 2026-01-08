# Qwen3-0.6B Fine-tuning for Notification Classification (3-Level Priority)

**Date:** 2026-01-08
**Model:** Qwen3-0.6B (Qwen/Qwen3-0.6B)
**Task:** Notification classification (folder + 3-level priority)

## Summary

Fine-tuned Qwen3-0.6B on notification classification with 3-level priority system. **Massive improvement** over FunctionGemma v2, especially in priority classification.

| Metric | Result |
|--------|--------|
| Folder Accuracy | **94.0%** |
| Priority Accuracy | **83.0%** |
| Both Correct | **78.2%** |
| Parse Failures | 0% |
| Training Time | ~81 minutes |
| Test Samples | 500 |

## Comparison to FunctionGemma v2

| Metric | FunctionGemma v2 | Qwen3-0.6B | Change |
|--------|-----------------|------------|--------|
| Folder | 90.6% | **94.0%** | +3.4% |
| Priority | 54.6% | **83.0%** | **+28.4%** |
| Both | 49.0% | **78.2%** | **+29.2%** |

### Priority Breakdown Comparison

| Priority | FunctionGemma v2 | Qwen3-0.6B | Change |
|----------|-----------------|------------|--------|
| 1 (Low) | 79.4% | 90.7% | +11.3% |
| 2 (Medium) | 22.9% | **66.4%** | **+43.5%** |
| 3 (High) | 35.9% | **86.4%** | **+50.5%** |

**Key Finding:** Qwen3 solved the Medium/High priority confusion that plagued FunctionGemma. The larger model (600M vs 270M) and simpler JSON output format made a significant difference.

## Training Configuration

```python
# Dataset
train_examples = 12,000
test_examples = 4,001
total_examples = 16,001

# Model
base_model = "Qwen/Qwen3-0.6B"
parameters = 606,142,464

# Quantization (4-bit NF4)
load_in_4bit = True
bnb_4bit_quant_type = "nf4"
bnb_4bit_compute_dtype = torch.bfloat16  # CRITICAL
bnb_4bit_use_double_quant = True

# LoRA Configuration
r = 16
lora_alpha = 16
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
trainable_params = 10,092,544 (1.67% of 606M)

# Training
epochs = 3
batch_size = 4
gradient_accumulation = 4
effective_batch_size = 16
learning_rate = 2e-4
scheduler = cosine
warmup_ratio = 0.1
dtype = bfloat16
total_steps = 2,250
```

## Priority Breakdown

The 3-level priority system:
- **1 (Low):** Can ignore or check later
- **2 (Medium):** Worth checking today
- **3 (High):** Requires immediate attention

| Priority | Accuracy | Samples |
|----------|----------|---------|
| 1 (Low) | **90.7%** | 233/257 |
| 2 (Medium) | 66.4% | 93/140 |
| 3 (High) | **86.4%** | 89/103 |

## Folder Breakdown

| Folder | Accuracy | Samples |
|--------|----------|---------|
| Work | **96.5%** | 194/201 |
| Personal | 92.6% | 126/136 |
| Promotions | 90.9% | 80/88 |
| Alerts | 93.3% | 70/75 |

## Output Format

**System Prompt:**
```
You are a notification classifier. Classify the notification into a folder and priority level.

Folders:
- Work: Job-related notifications...
- Personal: Family, friends...
- Promotions: Marketing, sales...
- Alerts: System alerts, security...

Priority levels:
- 1 (Low): Can ignore or check later
- 2 (Medium): Worth checking today
- 3 (High): Requires immediate attention

Respond with ONLY a JSON object: {"folder": "<folder>", "priority": <1-3>}
/no_think
```

**Model Output:**
```json
{"folder": "Work", "priority": 3}
```

## Training Metrics

- Final training loss: 0.2257
- Final mean token accuracy: 96.95%
- Training time: 1 hour 21 minutes (2,250 steps)

## Model Output

**Location:** `E:\projects\functiongemma-finetune\notif-3level\qwen3-finetuned`

## Key Findings

1. **Priority accuracy dramatically improved** from 54.6% to 83.0% (+28.4%)
2. **Medium/High distinction solved** - Medium went from 22.9% to 66.4%, High from 35.9% to 86.4%
3. **Folder classification improved** from 90.6% to 94.0%
4. **Zero parse failures** - model reliably outputs valid JSON
5. **Simple JSON format** works better than FunctionGemma's function-calling syntax

## Why Qwen3 Works Better

1. **Larger model** (606M vs 271M parameters) - more capacity to learn nuanced distinctions
2. **Simpler output format** - JSON is easier to learn than FunctionGemma's complex syntax
3. **`/no_think` directive** - disables Qwen3's thinking mode for direct responses
4. **Better pre-training** - Qwen3 likely has more diverse training data

## Files

- Training script: `E:\projects\functiongemma-finetune\notif-3level\finetune.py`
- Evaluation script: `E:\projects\functiongemma-finetune\notif-3level\evaluate.py`
- Conversion script: `E:\projects\functiongemma-finetune\notif-3level\convert_to_qwen3.py`
- Training data: `E:\projects\functiongemma-finetune\notif-3level\train.jsonl`
- Test data: `E:\projects\functiongemma-finetune\notif-3level\test.jsonl`
- Results: `E:\projects\functiongemma-finetune\notif-3level\results.json`
