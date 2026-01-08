# 基准测试 005: FunctionGemma-270M 微调 v2（3级优先级）

**日期:** 2026-01-08
**模型:** FunctionGemma-270M (google/functiongemma-270m-it)
**任务:** 通知分类（文件夹 + 3级优先级）

## 测试结果

在简化的3级优先级系统（相比v1的5级）上对 FunctionGemma-270M 进行了微调。

| 指标 | 结果 |
|------|------|
| 文件夹准确率 | **90.6%** |
| 优先级准确率 | **54.6%** |
| 综合准确率 | 49.0% |
| 训练时间 | ~2 小时 |
| 测试样本 | 500 |

## 与 v1（5级优先级）对比

| 指标 | v1 (5级) | v2 (3级) | 变化 |
|------|----------|----------|------|
| 文件夹 | 94.0% | 90.6% | -3.4% |
| 优先级 | 38.0% | 54.6% | **+16.6%** |

简化为3级后，优先级准确率提升了16.6个百分点。

## 训练配置

```python
# 数据集
train_examples = 12,000
test_examples = 4,001
total_examples = 16,001

# LoRA 配置
r = 16
lora_alpha = 16
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
trainable_params = 3,796,992 (占 271M 的 1.4%)

# 训练参数
epochs = 3
batch_size = 4
gradient_accumulation = 4
learning_rate = 2e-4
scheduler = cosine
warmup_ratio = 0.1
dtype = bfloat16
quantization = 4-bit NF4
```

## 优先级细分

3级优先级系统：
- **1 (低):** 可忽略或稍后查看
- **2 (中):** 当天值得查看
- **3 (高):** 需要立即关注

| 优先级 | 准确率 | 样本数 |
|--------|--------|--------|
| 1 (低) | **79.4%** | 204/257 |
| 2 (中) | 22.9% | 32/140 |
| 3 (高) | 35.9% | 37/103 |

**问题:** 模型过度预测优先级1。低优先级容易识别，但区分中/高优先级仍然困难。

## 文件夹细分

| 文件夹 | 准确率 | 样本数 |
|--------|--------|--------|
| Work | **94.0%** | 189/201 |
| Personal | **94.9%** | 129/136 |
| Promotions | 89.8% | 79/88 |
| Alerts | 74.7% | 56/75 |

文件夹分类表现依然强劲，尤其是 Work 和 Personal。

## 数据分布

**训练集（12,000 样本）:**
- 优先级 1: 5,380 (44.8%)
- 优先级 2: 3,333 (27.8%)
- 优先级 3: 3,287 (27.4%)

**测试集（4,001 样本）:**
- 优先级 1: 2,028 (50.7%)
- 优先级 2: 995 (24.9%)
- 优先级 3: 978 (24.4%)

## 模型输出

**位置:** `E:\projects\notif\functiongemma-finetuned-notif-3level`

**格式:** FunctionGemma 函数调用语法
```
<start_function_call>call:classify_notification{app_name:<escape>Slack<escape>,title:<escape>Message<escape>,body:<escape>...<escape>,folder:<escape>Work<escape>,priority:<escape>3<escape>}<end_function_call>
```

## 主要发现

1. **优先级准确率提升** 从38%提升到54.6%（3级系统）
2. **低优先级(1)效果好** 达到79.4% - 模型能正确识别可忽略的通知
3. **中/高区分困难** - 模型难以区分紧急程度
4. **文件夹分类强** - 整体90.6%，Work/Personal接近95%

## 下一步

1. **尝试 Qwen3-0.6B** - 更大的模型（600M vs 270M），更简单的 JSON 输出格式
2. **类别权重** - 惩罚对优先级1的过度预测
3. **改进训练数据** - 添加更清晰的优先级2 vs 3区分示例

## 相关文件

- 训练脚本: `E:\projects\notif\scripts\finetune_functiongemma_3level.py`
- 评估脚本: `E:\projects\notif\scripts\evaluate_functiongemma_3level.py`
- 训练数据: `E:\projects\notif\functiongemma_train_3level.jsonl`
- 测试数据: `E:\projects\notif\functiongemma_test_3level.jsonl`
- 结果文件: `E:\projects\notif\functiongemma_3level_results.json`
