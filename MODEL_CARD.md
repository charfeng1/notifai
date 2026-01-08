---
license: apache-2.0
language:
- en
- zh
tags:
- notification-classification
- on-device
- llama.cpp
- gguf
- qwen3
base_model: Qwen/Qwen3-0.6B
datasets:
- charlesfeng1/notifai-dataset
---

# Qwen3-0.6B-NotifAI

Fine-tuned Qwen3-0.6B model for on-device notification classification. Part of the [NotifAI](https://github.com/charfeng1/notifai) project.

## Model Description

This model classifies mobile notifications into folders and priority levels, running entirely on-device for privacy.

| Metric | Value |
|--------|-------|
| Base Model | Qwen3-0.6B |
| Fine-tuning | LoRA (r=16, alpha=16) |
| Training Data | 16,000 synthetic notifications |
| Folder Accuracy | 94.0% |
| Priority Accuracy | 83.0% |
| Quantization | Q8_0 |
| Model Size | ~650 MB |

## Intended Use

- On-device notification classification for Android
- Privacy-preserving notification management
- Real-time classification (1.3s latency on mobile)

## Classification Output

```json
{"folder": "Work", "priority": "high"}
```

### Folders
- **Work** - Professional notifications (Slack, Teams, Jira)
- **Personal** - Friends & family (WeChat, WhatsApp)
- **Promotions** - Marketing & deals
- **Alerts** - System & transactional

### Priority
- **high** - Immediate attention needed
- **medium** - Important but not urgent
- **low** - Can wait

## Usage with llama.cpp

```bash
./llama-cli -m qwen3-0.6b-notifai-Q8_0.gguf -p "<prompt>"
```

## Training

- **Method**: LoRA fine-tuning with Unsloth
- **Hardware**: RTX 4060 Ti 16GB
- **Duration**: 81 minutes
- **Epochs**: 3
- **Learning Rate**: 2e-4

## Limitations

- Optimized for common notification types
- Best performance with English and Chinese text
- Requires ~650MB storage on device

## Citation

```bibtex
@misc{notifai2026,
  title={NotifAI: On-Device Notification Classification},
  author={封一},
  year={2026},
  url={https://github.com/charfeng1/notifai}
}
```

## License

Apache 2.0
