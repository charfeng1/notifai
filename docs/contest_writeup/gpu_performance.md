# GPU 性能报告

> **项目背景**：本项目在发现比赛仅剩 48 小时后启动（1月6日发现，1月7日开始开发，1月8日完成），在 24 小时内完成了从数据生成、模型微调到 Android 应用部署的全流程。

---

## 硬件使用情况

### 开发与训练环境

| 项目 | 规格 |
|------|------|
| **GPU** | NVIDIA GeForce RTX 4060 Ti 16GB |
| **CPU** | Intel/AMD (Windows) |
| **RAM** | 32GB |
| **训练框架** | PyTorch + Unsloth + PEFT |

### 部署测试设备

| 项目 | 规格 |
|------|------|
| **设备型号** | Google Pixel (ARM64) |
| **CPU** | Qualcomm Snapdragon (ARMv8.2 + DotProd) |
| **GPU** | Adreno (未使用，纯 CPU 推理) |
| **RAM** | 8GB |

### 资源占用

| 指标 | 数值 | 说明 |
|------|------|------|
| **模型大小** | ~650 MB | Qwen3-0.6B-notifai Q8_0 量化 |
| **内存占用（推理时）** | ~1.2 GB | 包含 KV Cache |
| **内存占用（空闲）** | ~300 MB | 模型已加载但未推理 |
| **CPU 利用率（推理时）** | 70-80% | 4 线程并行 |

### 当前架构说明

**重要**：本项目当前使用 **CPU 推理**，未启用 GPU/Vulkan 加速。选择 CPU 的原因：

1. **兼容性优先** - CPU 推理兼容所有 Android 设备，Vulkan 支持参差不齐
2. **性能已足够** - 多架构优化后达到 22.79 tok/s，满足实时分类需求
3. **开发时间限制** - 24 小时内完成全部开发，Vulkan 集成需要额外时间

---

## 开发历程：基准测试驱动的决策

### 基线测试：选择正确的基座模型

在微调之前，我们对两个候选模型进行了基线测试（未微调），以评估其指令遵循能力和输出格式稳定性。

| 模型 | 文件夹准确率 | 优先级准确率 | 解析失败率 | 幻觉率 | 显存 |
|------|-------------|-------------|-----------|--------|------|
| FunctionGemma-270M | 35.0% | 2.0% | 2.0% | **20%** | 0.54 GB |
| **Qwen3-0.6B** | **59.0%** | 17.0% | **0%** | **0%** | 1.19 GB |

**关键发现：**
- FunctionGemma 存在严重幻觉问题，会生成不存在的文件夹名（如 "Order Details", "Home"）
- Qwen3 零幻觉，100% 输出有效 JSON
- 使用 `/no_think` 指令可禁用 Qwen3 的思考模式，获得直接响应

**决策：** 选择 Qwen3-0.6B 作为基座模型进行微调。

---

## 模型迭代过程

### 设计思路：从小模型到大模型

由于时间紧迫，我们采用了快速迭代策略：

#### 第一次尝试：FunctionGemma-270M（微调后）

| 指标 | 结果 | 问题 |
|------|------|------|
| 文件夹准确率 | 90.6% | ✅ 可接受 |
| 优先级准确率 | 54.6% | ❌ 不足 |
| 中优先级准确率 | 22.9% | ❌ 严重混淆 |
| 高优先级准确率 | 35.9% | ❌ 严重混淆 |

**问题分析**：270M 参数模型无法区分"今天处理"和"立即处理"的细微语义差异。

#### 第二次尝试：Qwen3-0.6B（最终选择）

| 指标 | FunctionGemma | Qwen3-0.6B | 提升 |
|------|--------------|------------|------|
| 文件夹准确率 | 90.6% | **94.0%** | +3.4% |
| 优先级准确率 | 54.6% | **83.0%** | **+28.4%** |
| 中优先级准确率 | 22.9% | **66.4%** | **+43.5%** |
| 高优先级准确率 | 35.9% | **86.4%** | **+50.5%** |

**关键发现**：
- 更大的模型（600M vs 270M）能更好区分细微语义差异
- 简单 JSON 输出格式比 FunctionGemma 的复杂函数调用语法更容易学习
- `/no_think` 指令有效禁用 Qwen3 的思考模式

### 训练性能

| 指标 | FunctionGemma | Qwen3-0.6B |
|------|--------------|------------|
| 训练时间 | ~2 小时 | ~81 分钟 |
| 可训练参数 | 3.8M (1.4%) | 10.1M (1.67%) |
| GPU 显存占用 | ~8 GB | ~12 GB |
| 训练数据 | 12,000 条 | 12,000 条 |

### 详细微调配置（Qwen3-0.6B）

```python
# 模型
base_model = "Qwen/Qwen3-0.6B"
parameters = 606,142,464

# 4-bit 量化训练
load_in_4bit = True
bnb_4bit_quant_type = "nf4"
bnb_4bit_compute_dtype = torch.bfloat16
bnb_4bit_use_double_quant = True

# LoRA 配置
r = 16
lora_alpha = 16
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                  "gate_proj", "up_proj", "down_proj"]
trainable_params = 10,092,544  # 1.67%

# 训练超参数
epochs = 3
batch_size = 4
gradient_accumulation = 4
effective_batch_size = 16
learning_rate = 2e-4
scheduler = "cosine"
warmup_ratio = 0.1
total_steps = 2,250
final_loss = 0.2257
```

---

## 涌现能力发现：训练名称偏见

### 实验：模型能否泛化到未见过的文件夹？

我们测试了微调后的模型能否分类到训练数据中**完全不存在**的文件夹类别。

| 新类别 | 准确率 | 测试应用 |
|--------|--------|----------|
| Social（社交） | **100%** | Instagram, Twitter, TikTok |
| Health（健康） | **100%** | MyFitnessPal, Apple Health, CVS |
| Travel（出行） | **100%** | United Airlines, Uber, Marriott |
| Finance（财务） | 33% | Chase ✓, Venmo ✗, Robinhood ✗ |
| Shopping（购物） | 33% | Target ✓, Amazon ✗, FedEx ✗ |

**整体准确率：73.3%** - 模型展现出涌现泛化能力。

### 发现：训练名称偏见问题

在生产环境测试中发现关键问题：**即使添加了描述匹配的自定义文件夹，模型仍分类到训练时的文件夹名称**。

| 场景 | 期望 | 实际 | 原因 |
|------|------|------|------|
| 添加 "Github" 文件夹，收到 PR 通知 | Github | Work | 模型记住了 "Work" 这个名称 |
| 添加 "Appointments" 文件夹，收到医生预约 | Appointments | Personal | 模型记住了 "Personal" 这个名称 |

### 解决方案：重命名默认文件夹

将默认文件夹重命名为训练时**从未见过**的名称：

| 原名称（训练时） | 新名称（生产环境） |
|-----------------|-------------------|
| Work | **Job** |
| Personal | **Private** |
| Promotions | **Deals** |
| Alerts | **Notices** |

**结果：** 重命名后，模型开始阅读文件夹描述进行分类，自定义文件夹功能正常工作。

---

## 推理性能指标

### 延迟分布

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **P50 总延迟** | ~72,000 ms | **1,300 ms** | **55x** |
| **P90 总延迟** | ~75,000 ms | **1,600 ms** | **47x** |
| **P99 总延迟** | ~80,000 ms | **2,500 ms** | **32x** |

### 详细性能分解

| 阶段 | 耗时 | 占比 | 说明 |
|------|------|------|------|
| **Prefill（首次）** | 1,594 ms | 64% | 处理 203 tokens |
| **Prefill（缓存）** | 380 ms | 29% | 仅处理 35 tokens |
| **Decode** | 877 ms | 68% | 生成 20 tokens @ 22.79 tok/s |
| **JNI 开销** | ~100 ms | 8% | Kotlin ↔ Native 数据传输 |

### 吞吐量

| 指标 | 数值 | 说明 |
|------|------|------|
| **Prefill 速度** | 85.6 tok/s | 批量处理 prompt tokens |
| **Decode 速度** | 22.79 tok/s | 自回归生成速度 |
| **Time to First Token** | 340 ms | 用户感知延迟 |
| **端到端分类速度** | ~46 通知/分钟 | 假设每条 1.3 秒 |

---

## 优化技术

### 1. 多架构构建（23x 提升）

编译 6 种针对不同 CPU 特性优化的库：

| 库变体 | 目标指令集 | 适用设备 |
|--------|-----------|----------|
| `llama_jni` | 通用 ARM64 | 所有设备（回退） |
| `llama_jni_v8` | ARMv8 + NEON | 2016+ 设备 |
| `llama_jni_v8_2` | ARMv8.2 + FP16 | 2018+ 设备 |
| `llama_jni_v8_2_dotprod` | + DotProd | Pixel 3+, 高通 855+ |
| `llama_jni_v8_2_i8mm` | + I8MM | 最新旗舰 |
| `llama_jni_v8_2_dotprod_i8mm` | DotProd + I8MM | Pixel 6+ |

**运行时检测**：
```kotlin
// 读取 /proc/cpuinfo 检测 CPU 特性
val hasDotProd = cpuFeatures.contains("asimddp")
val hasI8mm = cpuFeatures.contains("i8mm")
// 动态加载最优库
System.loadLibrary(optimalLibraryName)
```

### 2. 编译器优化

```cmake
target_compile_options(${target_name} PRIVATE
    -O3                    # 最高优化级别
    -DNDEBUG               # 禁用调试断言
    -fvectorize            # SIMD 自动向量化 ← 关键
    -ffp-model=fast        # 快速浮点运算 ← 关键
    -flto                  # 链接时优化 ← 关键
    -ffunction-sections    # 死代码消除
    -fdata-sections        # 死数据消除
)
```

### 3. KV Cache 系统提示缓存（50% 提升）

| 阶段 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 预填充 tokens | 203 | 35 | -83% |
| Prefill 延迟 | 1,594 ms | 380 ms | -76% |
| 总延迟 | 2,500 ms | 1,300 ms | -48% |

**原理**：缓存不变的系统提示（~184 tokens），只处理变化的通知内容（~35 tokens）。

**实现细节**：
```cpp
// JNI 层缓存接口
JNIEXPORT jint nativeCacheSystemPrompt(JNIEnv*, jobject, jstring);
JNIEXPORT void nativeInvalidateCache(JNIEnv*, jobject);
JNIEXPORT jboolean nativeIsCacheValid(JNIEnv*, jobject);

// 推理路径选择
if (g_system_prompt_cached) {
    // 快速路径: 只清除用户消息位置之后的 KV Cache
    llama_memory_seq_rm(kv, 0, g_system_prompt_tokens, -1);
} else {
    // 慢速路径: 处理完整提示
    llama_memory_clear(kv, true);
}
```

**缓存失效场景**：用户修改文件夹设置、修改偏好指令、应用重启。通过系统提示的 hash 值检测变化。

### 4. 量化选择

| 量化方案 | 模型大小 | 内存占用 | 速度 | 质量 |
|----------|----------|----------|------|------|
| FP16 | ~1.2 GB | ~2.0 GB | 基线 | 基线 |
| **Q8_0（当前）** | **~650 MB** | **~1.2 GB** | +10% | **-1%** |
| Q5_K_M（备选） | ~475 MB | ~1.0 GB | +20% | -2% |
| Q4_K_M | ~400 MB | ~0.8 GB | +25% | -5% |

**当前选择 Q8_0**：在 24 小时开发周期内优先保证分类质量和功能正确性。

**未来可切换 Q5_K_M**：如需进一步优化包体积和内存占用，Q5_K_M（475MB，1GB 内存）是理想的生产环境选择，质量损失仅 2%。

---

## 与同类方案对比

| 方案 | 模型 | Decode 速度 | 框架 |
|------|------|------------|------|
| PocketPal (llama.rn) | Qwen3-0.6B Q8 | 15.89 tok/s | React Native |
| **NotifAI（本项目）** | **Qwen3-0.6B-notifai Q8_0** | **22.79 tok/s** | **原生 Kotlin** |
| MLC-LLM | Qwen3-0.6B | ~18 tok/s | Vulkan |

**优势分析**：
- 比 PocketPal 快 43%（原生实现无 JS 桥接开销）
- 比 MLC-LLM 快 27%（CPU 优化充分）

---

## 合成数据生成

### 使用 Claude Code 生成高质量训练数据

由于时间紧迫且无法获取真实用户通知数据（隐私限制），我们使用 **Claude Code** 生成了 16,000 条高质量合成通知数据。

#### 数据生成策略

| 维度 | 要求 | 实现 |
|------|------|------|
| **多语言** | 中英文混合 | 30-40% 中文内容（微信、飞书、钉钉、抖音、小红书） |
| **多应用** | 真实包名 | 25+ 应用，使用真实 Android 包名 |
| **多场景** | 覆盖四类文件夹 | Work, Personal, Promotions, Alerts 均衡分布 |
| **优先级分布** | 避免全部紧急 | P1:P2:P3 ≈ 45%:28%:27% |

#### 生成流程

```
1. 设计详细的 CLAUDE.md 指南（定义格式、示例、规则）
     ↓
2. Claude Code 按批次生成（每批 400-500 条）
     ↓
3. 自动化验证脚本检查格式和分布
     ↓
4. 人工抽检质量（语言自然度、分类正确性）
     ↓
5. 合并为 16,001 条训练/测试数据集
```

#### 数据质量

| 指标 | 数值 |
|------|------|
| 总样本数 | 16,001 条 |
| 训练集 | 12,000 条 (75%) |
| 测试集 | 4,001 条 (25%) |
| 中文内容占比 | 23.7% |
| 应用多样性 | 1,019 个唯一应用 |
| 格式合规率 | 100% |

#### 示例数据

```jsonl
{"notification": {"app": "com.slack", "title": "#incidents", "body": "PROD DOWN - payments service returning 500s"}, "classification": {"folder": "Work", "priority": 3}}
{"notification": {"app": "com.tencent.mm", "title": "妈妈", "body": "到家了吗？外面冷记得穿外套"}, "classification": {"folder": "Personal", "priority": 2}}
{"notification": {"app": "com.ss.android.lark", "title": "紧急通知", "body": "生产环境数据库故障，技术团队正在抢修"}, "classification": {"folder": "Work", "priority": 3}}
```

**为什么选择 Claude Code 生成数据**：
1. **高质量** - 生成的通知自然、多样，不像模板化数据
2. **快速迭代** - 2 小时内完成 16K 条数据生成
3. **可控分布** - 通过 prompt 精确控制语言、应用、优先级分布
4. **中文质量** - Claude 对中文理解好，生成的微信/飞书消息自然流畅

---

## 24 小时开发时间线

| 时间 | 里程碑 | 说明 |
|------|--------|------|
| 1月6日 晚 | 发现比赛 | 距离截止仅 48 小时 |
| 1月7日 00:00 | 开始开发 | 确定技术方案 |
| 1月7日 06:00 | 数据生成完成 | 16K 条合成通知数据 |
| 1月7日 12:00 | FunctionGemma 微调 | 发现模型太小 |
| 1月7日 18:00 | Qwen3 微调完成 | 94% 准确率 |
| 1月8日 00:00 | Android 集成 | 多架构优化 |
| 1月8日 12:00 | KV Cache 优化 | 50% 加速 |
| 1月8日 18:00 | 自定义文件夹 | 涌现能力发现 |
| 1月8日 23:00 | 提交 | 完成全部开发 |

**未来优化方向**（因时间限制未实现）：
1. Vulkan GPU 加速（预期 1.5-2x 提升）
2. GBNF 语法约束（强制 JSON 输出）
3. 更激进的量化方案（Q4/Q5）
4. 投机解码

---

## 结论

| 成果 | 数值 | 意义 |
|------|------|------|
| **23x 推理加速** | 1→22.79 tok/s | 从不可用到流畅 |
| **50% 缓存优化** | 2.5s→1.3s | 接近实时响应 |
| **94% 分类准确率** | 微调后 | 生产就绪 |
| **73% 涌现泛化** | 未见类别 | 自定义文件夹可行 |
| **24 小时完成** | 全流程 | 快速原型能力 |

**关键技术贡献**：
1. 多架构 ARM 优化库的 CMake 构建方案（6 种库变体）
2. KV Cache 系统提示缓存的 JNI 实现（hash 检测失效）
3. 运行时 CPU 特性检测和动态库加载（/proc/cpuinfo 解析）
4. 基线测试驱动的模型选择（Qwen3 vs FunctionGemma）
5. LoRA 微调配置优化（1.67% 参数，81 分钟训练）
6. 训练名称偏见的发现与解决方案（重命名释放涌现能力）
7. 智能通知分发策略（高优先级立即推送，中优先级批量聚合）

**基准测试索引**：
| 编号 | 内容 | 关键发现 |
|------|------|----------|
| 001 | Qwen3-0.6B 基线 | 59% 准确率，零幻觉，需微调 |
| 002 | FunctionGemma 基线 | 35% 准确率，20% 幻觉，不推荐 |
| 004 | Android 推理优化 | 23x 加速，22.79 tok/s |
| 005 | FunctionGemma 微调 | 90.6% 文件夹，54.6% 优先级，中/高混淆 |
| 006 | Qwen3 微调 | 94% 文件夹，83% 优先级，最终选择 |
| 007 | 涌现分类测试 | 73.3% 新类别，训练名称偏见发现 |
| 008 | KV Cache 优化 | 50% 加速，83% tokens 节省 |
