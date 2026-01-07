# 基准测试 005: FunctionGemma-270M 微调 v1

**日期:** 2026-01-08
**模型:** FunctionGemma-270M（LoRA 微调）
**训练样本:** 6,000 个样本
**测试样本:** 100 个样本
**硬件:** NVIDIA GeForce RTX 4060 Ti (16GB)

## 测试结果

| 指标 | 分数 |
|------|------|
| **文件夹分类准确率** | **94.0%** (94/100) |
| 优先级分类准确率 | 38.0% (38/100) |
| 解析失败率 | 1.0% (1/100) |
| 幻觉率 | 0% (0/100) |

## 与基线对比

| 指标 | 基线 (002) | 微调后 (005) | 改进 |
|------|-----------|-------------|------|
| 文件夹准确率 | 35.0% | **94.0%** | **+59.0%** |
| 优先级准确率 | 2.0% | 38.0% | +36.0% |
| 解析失败率 | 2.0% | 1.0% | -1.0% |
| 幻觉率 | ~20% | **0%** | **-20%** |

## 关键发现

### ✓ 优点
- **文件夹分类显著提升** - 从 35% 提升至 94%，提升幅度达 59 个百分点
- **零幻觉** - 模型不再生成无效类别，完全遵循枚举约束
- **解析成功率高** - 99% 的输出可正确解析
- **训练效率高** - 仅需 55 分钟即可完成 3 个 epoch 的训练

### ✗ 缺点
- **优先级准确率仍然较低 (38%)** - 远低于生产环境 80% 的目标
- **优先级分类存在严重类别不平衡问题**

## 优先级准确率问题分析

### 训练数据分布（5 级优先级）

| 优先级 | 样本数 | 占比 |
|--------|--------|------|
| Priority 2 | 2,082 | 34.7% |
| Priority 3 | 1,638 | 27.3% |
| Priority 1 | 1,044 | 17.4% |
| Priority 4 | 814 | 13.6% |
| Priority 5 | 422 | **7.0%** |

**问题根源:**
1. **严重的类别不平衡** - Priority 5 仅占 7%，模型难以学习
2. **5 级分类过于细粒度** - 对于 270M 参数的小模型来说，区分 5 个优先级增加了不必要的复杂性
3. **优先级边界模糊** - 人类标注者在 Priority 2 vs 3 或 Priority 4 vs 5 之间的区分也存在主观性

### 优先级语义分析

通过 Explore Agent 对各优先级样本的分析：

| 优先级 | 典型场景 | 语义含义 |
|--------|---------|---------|
| Priority 1 | 社交媒体点赞、娱乐推荐、促销广告 | 可忽略 |
| Priority 2 | 电商促销、付款确认、约会匹配 | 稍后查看 |
| Priority 3 | 私信、任务分配、会议提醒、快递 | 日常通知 |
| Priority 4 | PR 审核、截止日期、支付失败 | 有人等待 |
| Priority 5 | 生产故障、安全警报、医疗紧急 | 立即中断 |

**结论:** Priority 1+2 语义接近（可延迟），Priority 4+5 语义接近（需立即处理）

## 错误样本

### 文件夹分类错误（6 个）

| 序号 | 应用 | 标题 | 期望 | 预测 |
|------|-----|------|------|------|
| 5 | Microsoft Teams | Q4 Planning - Board Review | Work | Work, Personal, Promotions, Alerts |
| 11 | Target | Welcome Back! 20% Off... | Promotions | (解析失败) |
| 28 | Sprint | Your Wireless Bill | Alerts | Work, Personal, Promotions, Alerts |
| 67 | Pinterest | Your Pin is Popular! | Promotions | Personal |
| 71 | Newegg | GPU Stock Alert: RTX 4090... | Promotions | Work, Personal, Promotions, Alerts |
| 88 | Google Fit | Daily Goal Achieved! | Alerts | Personal |

**分析:**
- 3 个错误输出了所有 4 个类别（模型不确定时的行为）
- 2 个错误是 Promotions vs Personal 的混淆
- 1 个是解析失败（截断）

## 技术细节

### 训练配置

```python
# LoRA 配置
lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0,
    bias="none",
    task_type="CAUSAL_LM",
)

# 训练参数
TrainingArguments(
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    bf16=True,
    optim="adamw_8bit",
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
)

# 量化配置
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
```

### 训练过程

- **总步数:** 1,125 steps (6,000 samples / 4 batch / 4 grad_accum * 3 epochs)
- **初始 Loss:** 3.012
- **最终 Loss:** 0.218
- **训练时间:** 55 分钟
- **显存占用:** ~10 GB（4-bit 量化）

### 关键实现

- 使用 `apply_chat_template()` + `tools` 参数生成标准 FunctionGemma 格式
- 使用 `DataCollatorForSeq2Seq` 处理标签填充（`label_pad_token_id=-100`）
- 训练完成后保存 LoRA adapter，评估时使用 `PeftModel.from_pretrained()` 加载

## 幻觉分析

**验证结果:** ✓ **零幻觉** (0/100 样本)

微调后，模型完全遵循枚举约束：
- 所有文件夹预测都在 {Work, Personal, Promotions, Alerts} 内
- 所有优先级预测都在 {1, 2, 3, 4, 5} 内
- 基线的幻觉问题（"Order Details", "Home" 等）完全消除

## 结论

**状态:** ⚠️ 部分成功 - 文件夹分类可用，优先级分类需改进

**成功点:**
- ✅ 文件夹准确率达到 94%，满足生产环境要求
- ✅ 消除了基线的幻觉问题
- ✅ 证明 FunctionGemma-270M 可通过微调显著改善

**待改进:**
- ❌ 优先级准确率 38% 不可接受
- 根本原因是 5 级分类过于复杂 + 类别不平衡

## 下一步

1. **简化优先级为 3 级** ✓ 已完成
   - 映射: Priority 1+2 -> Low, Priority 3 -> Medium, Priority 4+5 -> High
   - 已重新映射完整数据集 (10,800 样本)

2. **重新训练**
   - 使用更大的训练集 (8,000+ 样本)
   - 使用 3 级优先级系统
   - 预期优先级准确率可达 80%+

3. **评估改进后的模型**
   - 验证 3 级优先级是否显著提升准确率
   - 确认文件夹准确率保持在 90%+

**预期结果:**
- 文件夹准确率: ≥90%
- 优先级准确率: ≥80%
- 幻觉率: 0%
