# 提交材料检查清单

## 已完成

| 材料 | 文件 | 状态 |
|------|------|------|
| 项目基本信息表 | `project_info.md` | ✅ 已创建 |
| 详细项目文档 | `project_documentation.md` | ✅ 已创建 |
| GPU 性能报告（赛道一） | `gpu_performance.md` | ✅ 已创建 |
| 演示文稿内容 | `slides_content.md` | ✅ 已创建（需转为 PDF） |
| README.md | 根目录 `README.md` | ✅ 已更新 |

---

## 需要您完成

### 1. 填写个人信息

在 `project_info.md` 中填写以下空白：

```markdown
- 队长手机：[填写]
- 队长邮箱：[填写]
```

### 2. 录制演示视频（3-5 分钟）

**必须内容：**
1. 项目介绍（30秒）- 通知过载问题 + 解决方案
2. 核心功能演示（2-3分钟）
   - 接收通知 → 自动分类
   - 展示 4 个文件夹
   - 添加自定义文件夹
   - 优先级排序
3. 技术亮点（1分钟）
   - 展示 Logcat 性能日志（22.79 tok/s）
   - 强调隐私（无网络请求）
4. 总结（30秒）- 开源仓库 + 未来规划

**格式要求：**
- MP4 格式，不超过 200MB
- 需包含真人讲解或字幕说明
- 上传至百度网盘/阿里云盘/Google Drive

### 3. 制作演示文稿（PDF）

根据 `slides_content.md` 内容制作 PDF：
- 不超过 20 页
- 包含截图和架构图

### 4. 打包 ZIP 文件

将以下文件打包：
```
submission.zip
├── project_info.md
├── project_documentation.md
├── gpu_performance.md
├── slides.pdf              # 需制作
└── demo_video_link.txt     # 视频网盘链接
```

### 5. 发送邮件

**收件人**: h19718353@gmail.com
**主题格式**: [作品提交]-赛道一-NotifAI-NotifAI

---

## 截止时间

**2026年1月8日 23:59 (GMT+8)**

---

## 快速命令

```bash
# 查看所有提交材料
ls -la docs/contest_writeup/

# 生成视频演示的 adb 命令
adb logcat -s LlamaPerf:I LlamaJNI:I ClassificationService:I
```
