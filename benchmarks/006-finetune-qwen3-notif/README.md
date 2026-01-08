# 基准测试 006: Qwen3-0.6B 微调（3级优先级）

**日期:** 2026-01-08
**模型:** Qwen3-0.6B (Qwen/Qwen3-0.6B)
**任务:** 通知分类（文件夹 + 3级优先级）

## 摘要

对 Qwen3-0.6B 进行了3级优先级系统的通知分类微调。相比 FunctionGemma v2 **大幅提升**，尤其是优先级分类。

| 指标 | 结果 |
|------|------|
| 文件夹准确率 | **94.0%** |
| 优先级准确率 | **83.0%** |
| 综合准确率 | **78.2%** |
| 解析失败率 | 0% |
| 训练时间 | ~81 分钟 |
| 测试样本 | 500 |

## 与 FunctionGemma v2 对比

| 指标 | FunctionGemma v2 | Qwen3-0.6B | 变化 |
|------|-----------------|------------|------|
| 文件夹 | 90.6% | **94.0%** | +3.4% |
| 优先级 | 54.6% | **83.0%** | **+28.4%** |
| 综合 | 49.0% | **78.2%** | **+29.2%** |

### 优先级细分对比

| 优先级 | FunctionGemma v2 | Qwen3-0.6B | 变化 |
|--------|-----------------|------------|------|
| 1 (低) | 79.4% | 90.7% | +11.3% |
| 2 (中) | 22.9% | **66.4%** | **+43.5%** |
| 3 (高) | 35.9% | **86.4%** | **+50.5%** |

**关键发现:** Qwen3 解决了困扰 FunctionGemma 的中/高优先级混淆问题。更大的模型（600M vs 270M）和更简单的 JSON 输出格式产生了显著差异。

## 与基础模型对比（未微调）

来自[基准测试 001](../001-baseline-qwen3-0.6b/README.md)的基础 Qwen3-0.6B 模型（未微调）：

| 指标 | 基础 Qwen3 | 微调后 Qwen3 | 提升 |
|------|------------|--------------|------|
| 文件夹准确率 | 59.0% | **94.0%** | **+35.0%** |
| 优先级准确率 | 17.0% | **83.0%** | **+66.0%** |
| 解析失败率 | 0% | 0% | - |

**备注:** 基础模型使用5级优先级，微调后使用3级。在聊天模板中使用 `enable_thinking=False` 时，两者都能达到0%解析失败率。

**结论:** 微调带来巨大提升 - 尤其是优先级分类（绝对提升 +66%）。

## 训练配置

```python
# 数据集
train_examples = 12,000
test_examples = 4,001
total_examples = 16,001

# 模型
base_model = "Qwen/Qwen3-0.6B"
parameters = 606,142,464

# 量化（4-bit NF4）
load_in_4bit = True
bnb_4bit_quant_type = "nf4"
bnb_4bit_compute_dtype = torch.bfloat16  # 关键参数
bnb_4bit_use_double_quant = True

# LoRA 配置
r = 16
lora_alpha = 16
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
trainable_params = 10,092,544 (占 606M 的 1.67%)

# 训练参数
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

## 优先级细分

3级优先级系统：
- **1 (低):** 可忽略或稍后查看
- **2 (中):** 当天值得查看
- **3 (高):** 需要立即关注

| 优先级 | 准确率 | 样本数 |
|--------|--------|--------|
| 1 (低) | **90.7%** | 233/257 |
| 2 (中) | 66.4% | 93/140 |
| 3 (高) | **86.4%** | 89/103 |

## 文件夹细分

| 文件夹 | 准确率 | 样本数 |
|--------|--------|--------|
| Work | **96.5%** | 194/201 |
| Personal | 92.6% | 126/136 |
| Promotions | 90.9% | 80/88 |
| Alerts | 93.3% | 70/75 |

## 输出格式

**系统提示:**
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

**模型输出:**
```json
{"folder": "Work", "priority": 3}
```

## 训练指标

- 最终训练损失: 0.2257
- 最终平均 token 准确率: 96.95%
- 训练时间: 1 小时 21 分钟（2,250 步）

## 模型输出

**位置:** `E:\projects\functiongemma-finetune\notif-3level\qwen3-finetuned`

## 关键发现

1. **优先级准确率大幅提升** 从 54.6% 到 83.0%（+28.4%）
2. **中/高区分问题解决** - 中优先级从 22.9% 到 66.4%，高优先级从 35.9% 到 86.4%
3. **文件夹分类提升** 从 90.6% 到 94.0%
4. **零解析失败** - 模型可靠地输出有效 JSON
5. **简单 JSON 格式** 比 FunctionGemma 的函数调用语法效果更好

## 为什么 Qwen3 效果更好

1. **更大的模型**（606M vs 271M 参数）- 更强的学习细微区分能力
2. **更简单的输出格式** - JSON 比 FunctionGemma 的复杂语法更容易学习
3. **`/no_think` 指令** - 禁用 Qwen3 的思考模式以获得直接响应
4. **更好的预训练** - Qwen3 可能有更多样化的训练数据

## 相关文件

- 训练脚本: `E:\projects\functiongemma-finetune\notif-3level\finetune.py`
- 评估脚本: `E:\projects\functiongemma-finetune\notif-3level\evaluate.py`
- 转换脚本: `E:\projects\functiongemma-finetune\notif-3level\convert_to_qwen3.py`
- 训练数据: `E:\projects\functiongemma-finetune\notif-3level\train.jsonl`
- 测试数据: `E:\projects\functiongemma-finetune\notif-3level\test.jsonl`
- 结果文件: `E:\projects\functiongemma-finetune\notif-3level\results.json`
