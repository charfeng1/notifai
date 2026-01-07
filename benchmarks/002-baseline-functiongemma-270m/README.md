# 基准测试 002: FunctionGemma-270M 基线（未微调）

**日期:** 2026-01-07
**模型:** FunctionGemma-270M（基础模型，未微调）
**测试样本:** 100 个样本
**硬件:** NVIDIA GeForce RTX 4060 Ti (16GB)

## 测试结果

| 指标 | 分数 |
|------|------|
| **文件夹分类准确率** | **35.0%** (35/100) |
| **优先级分类准确率** | 2.0% (2/100) |
| **解析失败率** | 2.0% (2/100) |
| **幻觉率** | **4/20 错误样本** (~20%) |

## 关键发现

### ✗ 严重问题
- **文件夹准确率极低 (35%)** - 远低于生产环境 80% 的目标
- **优先级准确率极差 (2%)** - 几乎无法正确分类优先级
- **⚠️ 存在幻觉问题** - 模型生成不存在的文件夹名称
  - "Order Details"（应为 Alerts）
  - "Home"（应为 Promotions）
  - "Security Alerts"（应为 Alerts）
  - "App Store"（应为 Promotions）
- **忽略枚举约束** - 即使在函数声明中指定了 enum，模型仍发明新类别

### ✓ 优点
- **模型体积小** - 仅占用 0.54 GB 显存（Qwen3 需要 1.19 GB）
- **推理速度快** - 270M 参数模型，适合移动设备
- **解析失败率低** - 仅 2% 无法解析

## 幻觉分析

**验证结果:** ✗ **存在严重幻觉**（4/20 错误样本）

模型预测了有效集合之外的文件夹名称：
- 有效文件夹: {Work, Personal, Promotions, Alerts}
- 幻觉预测: "Order Details", "Home", "Security Alerts", "App Store"

**影响:**
- ❌ 生产环境不安全 - 意外值会导致系统崩溃
- ❌ 函数声明中的枚举约束无效
- ✓ 可通过 GBNF 语法强制约束解决
- ✓ 或通过微调改善

## 与 Qwen3-0.6B 对比

| 指标 | FunctionGemma-270M | Qwen3-0.6B | 差异 |
|------|-------------------|-----------|------|
| 文件夹准确率 | **35.0%** | **59.0%** | -24% |
| 优先级准确率 | 2.0% | 17.0% | -15% |
| 解析失败率 | 2.0% | 0.0% | +2% |
| 幻觉率 | ~20% | 0% | +20% |
| 显存占用 | 0.54 GB | 1.19 GB | -0.65 GB |
| 参数量 | 270M | 600M | -330M |

**总结:**
- Qwen3-0.6B 在所有准确率指标上**显著优于** FunctionGemma-270M
- Qwen3-0.6B **零幻觉**，FunctionGemma-270M 存在严重幻觉问题
- FunctionGemma-270M 唯一优势：模型更小，适合资源受限设备

## 技术细节

### FunctionGemma 格式
使用特殊控制令牌进行函数调用：
- `<start_of_turn>developer/user/model<end_of_turn>` - 对话轮次
- `<start_function_declaration>...<end_function_declaration>` - 函数模式
- `<start_function_call>...<end_function_call>` - 模型输出
- `<escape>...<escape>` - 所有字符串值需要转义

### 函数声明示例
```
declaration:classify_notification{
  description:<escape>Classify notification into folder and priority. ...<escape>,
  parameters:{
    properties:{
      folder:{
        description:<escape>One of: Work, Personal, Promotions, Alerts<escape>,
        enum:[<escape>Work<escape>,<escape>Personal<escape>,<escape>Promotions<escape>,<escape>Alerts<escape>],
        type:<escape>STRING<escape>
      },
      priority:{...}
    },
    required:[<escape>folder<escape>,<escape>priority<escape>],
    type:<escape>OBJECT<escape>
  }
}
```

### 问题根源
**枚举约束无效:** 即使明确指定 `enum:[Work,Personal,Promotions,Alerts]`，模型仍然：
1. 生成 "Order Details" 而不是 "Alerts"
2. 生成 "Home" 而不是 "Promotions"
3. 生成 "Security Alerts" 而不是 "Alerts"
4. 生成 "App Store" 而不是 "Promotions"

这表明 FunctionGemma-270M 的指令遵循能力较弱，可能需要：
- 更强的提示工程
- GBNF 语法强制约束
- 微调以提高类别理解

## 结论

**状态:** ❌❌ 不推荐用于生产环境

FunctionGemma-270M 基础模型：
- ✓ 体积小，适合移动设备
- ✓ 推理速度快
- ✗ 准确率极低（35%）
- ✗ 存在幻觉问题（20%）
- ✗ 优先级分类几乎无效（2%）
- ✗ 忽略枚举约束

**推荐:** 使用 Qwen3-0.6B 代替
- 准确率更高（59% vs 35%）
- 零幻觉
- 更好的指令遵循能力
- 虽然大 2 倍，但在 16GB 设备上完全可行

**下一步:**
1. ~~使用 FunctionGemma-270M~~ - 不推荐
2. **使用 Qwen3-0.6B** - 推荐
3. 对 Qwen3-0.6B 进行微调以提高到 80%+
4. 部署时使用 GBNF 语法作为额外保障
