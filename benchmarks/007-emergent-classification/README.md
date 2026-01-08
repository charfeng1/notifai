# 涌现分类能力：Qwen3-0.6B 泛化到未见过的文件夹

**日期:** 2026-01-08
**模型:** Qwen3-0.6B 微调版（来自基准测试 006）
**测试:** 模型能否将通知分类到训练中从未见过的文件夹类别？

## 摘要

测试微调后的通知分类器能否泛化到**训练数据中完全不存在的新文件夹类别**。模型展现出**涌现泛化能力**，在全新类别上达到 73.3% 的准确率。

| 指标 | 结果 |
|------|------|
| 新文件夹准确率 | **73.3%** (11/15) |
| 有效 JSON 输出 | **100%** (15/15) |
| 完美分类的类别 | 3/5（社交、健康、出行） |

## 实验设计

### 训练类别（微调时见过）
- Work（工作）
- Personal（个人）
- Promotions（促销）
- Alerts（提醒）

### 测试类别（训练时从未见过）
- **Finance（财务）** - 银行、支付、投资、账单、交易
- **Shopping（购物）** - 电商、配送、订单更新、包裹追踪
- **Social（社交）** - 社交媒体、好友请求、点赞、评论、@提及
- **Health（健康）** - 医疗预约、健身应用、健康提醒、用药
- **Travel（出行）** - 航班、酒店、交通、行程更新、登机牌

## 各类别结果

| 类别 | 准确率 | 测试用例 |
|------|--------|----------|
| Social（社交） | **100%** (3/3) | Instagram、Twitter、TikTok |
| Health（健康） | **100%** (3/3) | MyFitnessPal、Apple Health、CVS Pharmacy |
| Travel（出行） | **100%** (3/3) | United Airlines、Uber、Marriott |
| Finance（财务） | 33% (1/3) | Chase 正确；Venmo、Robinhood 混淆 |
| Shopping（购物） | 33% (1/3) | Target 正确；Amazon、FedEx 混淆 |

## 详细结果

### 正确分类 (11/15)

| 应用 | 标题 | 期望 | 预测 |
|------|------|------|------|
| Chase | Payment received | Finance | Finance |
| Target | Order ready | Shopping | Shopping |
| Instagram | New follower | Social | Social |
| Twitter | New mention | Social | Social |
| TikTok | Video liked | Social | Social |
| MyFitnessPal | Daily reminder | Health | Health |
| Apple Health | Stand reminder | Health | Health |
| CVS Pharmacy | Prescription ready | Health | Health |
| United Airlines | Flight reminder | Travel | Travel |
| Uber | Trip completed | Travel | Travel |
| Marriott | Check-in available | Travel | Travel |

### 错误分类 (4/15)

| 应用 | 标题 | 期望 | 预测 | 分析 |
|------|------|------|------|------|
| Venmo | Payment complete | Finance | Shopping | 支付 ≈ 交易 → 电商混淆 |
| Robinhood | Stock alert | Finance | Shopping | 投资 ≈ 买卖 → 电商混淆 |
| Amazon | Your order shipped | Shopping | Travel | 发货 ≈ 物流 → 交通混淆 |
| FedEx | Package delivered | Shopping | Travel | 配送 ≈ 物流 → 交通混淆 |

## 分析

### 为什么模型能泛化

1. **学会了通用分类模式** - 不只是记住文件夹名称
2. **阅读新的文件夹描述** - 使用系统提示中的描述来理解新类别
3. **应用语义理解** - 将通知内容映射到最相关的类别

### 混淆模式

错误揭示了有趣的语义重叠：

```
Finance ↔ Shopping（财务 ↔ 购物）
├── Venmo "payment" → 被视为商业交易
└── Robinhood "stock" → 被视为买卖行为

Shopping ↔ Travel（购物 ↔ 出行）
├── Amazon "shipped" → 被视为物流/运输
└── FedEx "delivered" → 被视为包裹移动
```

这些混淆是**语义上合理的** - 模型没有幻觉出随机类别，而是做出了可辩护（虽然不正确）的解释。

### 这意味着什么

1. **模型学会了分类的概念**，而不仅仅是训练类别
2. **新文件夹可以工作**，只要描述清晰且独特
3. **语义重叠**会导致类别间混淆（财务/购物、购物/出行）
4. **生产意义**: 可以添加新文件夹类别而无需重新训练，但应确保描述互不重叠

## 与基础模型对比

| 模型 | 新类别准确率 | 备注 |
|------|-------------|------|
| 基础 Qwen3（未微调） | ~20%（估计） | 基于通用知识猜测 |
| 微调后 Qwen3 | **73.3%** | 学到的分类模式可迁移 |

## 技术细节

### 测试用系统提示
```
You are a notification classifier. Classify the notification into a folder and priority level.

Folders:
- Finance: Banking, payments, investments, bills, transactions
- Shopping: E-commerce, deliveries, order updates, package tracking
- Social: Social media, friend requests, likes, comments, mentions
- Health: Medical appointments, fitness apps, health reminders, medication
- Travel: Flights, hotels, transportation, trip updates, boarding passes

Priority levels:
- 1 (Low): Can ignore or check later
- 2 (Medium): Worth checking today
- 3 (High): Requires immediate attention

Respond with ONLY a JSON object: {"folder": "<folder>", "priority": <1-3>}
/no_think
```

### 模型配置
- 基础: Qwen3-0.6B + 基准测试 006 的 LoRA 适配器
- 量化: 4-bit NF4
- 生成: 贪婪解码 (do_sample=False)

## 关键发现

1. **涌现泛化得到确认** - 模型将分类能力迁移到未见过的类别
2. **100% 格式合规** - 即使是新类别也始终输出有效 JSON
3. **语义推理** - 模型阅读并使用文件夹描述，而不仅仅是名称
4. **类别区分度很重要** - 清晰、不重叠的描述能提高准确率

## 生产环境启示

### 添加新文件夹
- 可以**无需重新训练**就添加新文件夹类别
- 应确保文件夹描述**独特且不重叠**
- 部署前用代表性样本测试

### 推荐的文件夹设计
- 使用互斥的描述
- 避免语义重叠（如"支付"出现在多个文件夹中）
- 具体说明每个文件夹应包含什么

## 文件

- 测试脚本: `E:\projects\functiongemma-finetune\notif-3level\test_emergent.py`
- 结果: `E:\projects\functiongemma-finetune\notif-3level\emergent_results.json`
- 模型: `E:\projects\functiongemma-finetune\notif-3level\qwen3-finetuned`

## 结论

微调后的 Qwen3-0.6B 模型展现出**涌现分类行为** - 它能泛化到训练中从未见过的文件夹类别。这表明模型学会了通知分类的底层概念，而不仅仅是特定的训练类别。

**状态:** 涌现泛化能力确认（新类别 73.3% 准确率）

---

## 连贯性测试：模型仍保持通用能力

除了涌现分类能力，我们还测试了微调后的模型是否仍然能够执行通用任务。

### 测试结果

| 任务类型 | 提示 | 结果 | 状态 |
|----------|------|------|------|
| 知识问答 | "What is the capital of France?" | "The capital of France is Paris." | ✅ |
| 数学计算 | "What is 15 + 27?" | 完整推理 → **42**（正确） | ✅ |
| 代码生成 | "Write a Python function that adds two numbers." | `def add(a, b): return a + b` | ✅ |
| 创意写作 | "Write a haiku about the moon." | 写出了俳句（音节计数略有偏差） | ✅ |
| 翻译 | "Translate 'Hello' to Spanish." | 正确推理翻译过程 | ✅ |
| 对话 | "Can you help me with something?" | 友好、开放式回应 | ✅ |

### 数学推理示例

```
提示: What is 15 + 27?

模型输出:
<think>
Okay, the user is asking for the sum of 15 and 27. Let me think.
15 plus 27. Hmm, how do I add these numbers? Well, maybe I can
break them down. 15 is 10 + 5, and 27 is 20 + 7. Adding those
together: 10 + 20 is 30, and 5 + 7 is 12. Then 30 + 12 equals 42.
</think>

**Answer:** 15 + 27 = 42
```

### 代码生成示例

```
提示: Write a Python function that adds two numbers.

模型输出:
def add(a, b):
    return a + b
```

### 为什么模型保持连贯

1. **LoRA 微调只修改 1.67% 的参数** - 基础模型知识完整保留
2. **适配器层叠加** - 新技能"添加"到模型上，而非"覆盖"
3. **领域特定训练** - 只在通知分类任务上训练，不干扰其他能力

### 结论

微调**非常成功**：
- ✅ 通知分类：94.0% 文件夹 / 83.0% 优先级
- ✅ 涌现泛化：73.3% 在未见类别上
- ✅ 通用能力：数学、代码、翻译、对话全部正常
- ✅ 无灾难性遗忘

模型同时获得了新技能（通知分类）并保留了原有能力（通用智能）。
