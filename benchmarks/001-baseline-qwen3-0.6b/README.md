# 基准测试 001: Qwen3-0.6B 基线（未微调）

**日期:** 2026-01-07
**模型:** Qwen3-0.6B-Instruct（基础模型，未微调）
**测试样本:** 100 个样本
**硬件:** NVIDIA GeForce RTX 4060 Ti (16GB)

## 测试结果

| 指标 | 分数 |
|------|------|
| **文件夹分类准确率** | **59.0%** (59/100) |
| **优先级分类准确率** | 17.0% (17/100) |
| **解析失败率** | 0.0% (0/100) |

## 主要发现

### ✓ 优点
- **完美的 JSON 输出** - 0% 解析失败，始终生成有效的 JSON 格式
- **零幻觉** - 100% 的预测都在有效的文件夹和优先级范围内，从不发明新的类别
- **GPU 推理正常工作** - 模型加载在 cuda:0，占用 1.19 GB 显存
- **指令遵循能力** - 使用 `/no_think` 后正确响应提示
- **输出模式尊重** - 严格遵守提示词中定义的文件夹列表

### ✗ 缺点
- **文件夹准确率低 (59%)** - 低于生产环境 80% 的目标
- **优先级准确率差 (17%)** - 模型在优先级分类上表现不佳
- **类别混淆** - 常见的错误分类：
  - Alerts（提醒）→ Work（工作）（例如："包裹已送达"、"收到付款"）
  - Work（工作）→ Promotions（促销）（例如：Slack 消息、Gmail 工作邮件）
  - Promotions（促销）→ Work（工作）（例如：Netflix 新内容）

### 错误样本
1. Slack "#critical-incidents"（工作）→ 预测：促销
2. Amazon "Your order is on its way"（提醒）→ 预测：工作
3. FedEx "Package delivered"（提醒）→ 预测：工作
4. Bank of America "Payment received"（提醒）→ 预测：工作

## 技术细节

### 模型配置
- 模型路径: `./models/qwen3-0.6b`
- torch.dtype: bfloat16
- device_map: auto（GPU）
- max_new_tokens: 100
- do_sample: False（贪婪解码）

### 关键实现细节
1. **必须在系统提示中添加 `/no_think`** 以禁用思考模式
2. **在聊天模板中使用 `enable_thinking=False`**
3. **处理 Unicode 错误**（中文文本如微信消息）

### 系统提示格式
```
You classify notifications into folders.

Folders:
[Work]: Professional messages from work apps like Slack, Jira, Teams, work email, Feishu, DingTalk
[Personal]: Messages from friends and family via WhatsApp, WeChat, Telegram, Douyin, RedNote
[Promotions]: Marketing, deals, spam, promotional content from shopping and service apps
[Alerts]: Banking, security, system notifications, delivery updates, transactional messages

Output JSON only: {"folder": "...", "priority": 1-5}
Priority: 1=ignore, 2=low, 3=normal, 4=important, 5=urgent
/no_think
```

## 与 Qwen2.5-0.5B 的对比
- **Qwen2.5-0.5B:** 52% 文件夹准确率
- **Qwen3-0.6B:** 59% 文件夹准确率（+7%）
- Qwen3-0.6B 是更好的基础模型

## 结论

**状态:** ❌ 低于 80% 目标 - 需要微调

Qwen3-0.6B 基础模型：
- ✓ 生成完美的 JSON 格式（对生产环境至关重要）
- ✓ 理解指令遵循
- ✗ 缺乏通知分类的领域知识
- ✗ 未经训练时容易混淆文件夹类别

**下一步:** 使用训练数据集进行微调（类似 functiongemma-finetune 项目）
**预期结果:** 微调后文件夹准确率达到 80%+

## 幻觉分析

**验证结果:** ✓ 零幻觉（0/100 样本）

模型从未预测有效集合之外的文件夹或优先级值：
- 所有文件夹预测 ∈ {Work, Personal, Promotions, Alerts}
- 所有优先级预测 ∈ {1, 2, 3, 4, 5}

**重要性:**
- 生产环境可以安全解析模型输出，无需额外验证
- 不会因意外值导致系统崩溃
- 提示工程有效（`/no_think` + 明确的类别列表）
- 无需 GBNF 语法约束即可保证输出格式
