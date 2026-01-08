# FunctionGemma-270M Fine-tuning v2 (3-Level Priority)

**Date:** 2026-01-08
**Model:** FunctionGemma-270M (google/functiongemma-270m-it)
**Task:** Notification classification (folder + 3-level priority)

## Summary

Fine-tuned FunctionGemma-270M on notification classification with simplified 3-level priority system (vs 5-level in v1).

| Metric | Result |
|--------|--------|
| Folder Accuracy | **90.6%** |
| Priority Accuracy | **54.6%** |
| Both Correct | 49.0% |
| Training Time | ~2 hours |
| Test Samples | 500 |

## Comparison to v1 (5-Level Priority)

| Metric | v1 (5-level) | v2 (3-level) | Change |
|--------|-------------|--------------|--------|
| Folder | 94.0% | 90.6% | -3.4% |
| Priority | 38.0% | 54.6% | **+16.6%** |

Simplifying to 3 levels improved priority accuracy by 16.6 percentage points.

## Training Configuration

```python
# Dataset
train_examples = 12,000
test_examples = 4,001
total_examples = 16,001

# LoRA Configuration
r = 16
lora_alpha = 16
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
trainable_params = 3,796,992 (1.4% of 271M)

# Training
epochs = 3
batch_size = 4
gradient_accumulation = 4
learning_rate = 2e-4
scheduler = cosine
warmup_ratio = 0.1
dtype = bfloat16
quantization = 4-bit NF4
```

## Priority Breakdown

The 3-level priority system:
- **1 (Low):** Can ignore or check later
- **2 (Medium):** Worth checking today
- **3 (High):** Requires immediate attention

| Priority | Accuracy | Samples |
|----------|----------|---------|
| 1 (Low) | **79.4%** | 204/257 |
| 2 (Medium) | 22.9% | 32/140 |
| 3 (High) | 35.9% | 37/103 |

**Issue:** Model over-predicts Priority 1. Low priority is easy to identify, but distinguishing Medium vs High remains difficult.

## Folder Breakdown

| Folder | Accuracy | Samples |
|--------|----------|---------|
| Work | **94.0%** | 189/201 |
| Personal | **94.9%** | 129/136 |
| Promotions | 89.8% | 79/88 |
| Alerts | 74.7% | 56/75 |

Folder classification remains strong, especially for Work and Personal.

## Data Distribution

**Training Set (12,000 examples):**
- Priority 1: 5,380 (44.8%)
- Priority 2: 3,333 (27.8%)
- Priority 3: 3,287 (27.4%)

**Test Set (4,001 examples):**
- Priority 1: 2,028 (50.7%)
- Priority 2: 995 (24.9%)
- Priority 3: 978 (24.4%)

## Model Output

**Location:** `E:\projects\notif\functiongemma-finetuned-notif-3level`

**Format:** FunctionGemma function-calling syntax
```
<start_function_call>call:classify_notification{app_name:<escape>Slack<escape>,title:<escape>Message<escape>,body:<escape>...<escape>,folder:<escape>Work<escape>,priority:<escape>3<escape>}<end_function_call>
```

## Key Findings

1. **Priority accuracy improved** from 38% to 54.6% with 3-level system
2. **Low priority (1) works well** at 79.4% - model correctly identifies ignorable notifications
3. **Medium/High distinction is hard** - the model struggles to differentiate urgency levels
4. **Folder classification strong** - 90.6% overall, with Work/Personal near 95%

## Next Steps

1. **Try Qwen3-0.6B** - Larger model (600M vs 270M) with simpler JSON output format
2. **Class weighting** - Penalize over-prediction of Priority 1
3. **Better training data** - Add clearer examples for Priority 2 vs 3 distinction

## Files

- Training script: `E:\projects\notif\scripts\finetune_functiongemma_3level.py`
- Evaluation script: `E:\projects\notif\scripts\evaluate_functiongemma_3level.py`
- Training data: `E:\projects\notif\functiongemma_train_3level.jsonl`
- Test data: `E:\projects\notif\functiongemma_test_3level.jsonl`
- Results: `E:\projects\notif\functiongemma_3level_results.json`
