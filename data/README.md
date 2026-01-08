# NotifAI Training Dataset

Synthetic notification dataset for training notification classification models.

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total samples | 16,000 |
| Languages | English, Chinese |
| Folders | 4 (Work, Personal, Promotions, Alerts) |
| Priority levels | 3 (High, Medium, Low) |

## Files

| File | Description | Samples |
|------|-------------|---------|
| `training_data.jsonl` | Main training dataset | 16,000 |
| `raw/batch_*.jsonl` | Raw generation batches | ~400 each |

## Data Format

Each line is a JSON object:

```json
{
  "id": "00001",
  "notification": {
    "app": "com.slack",
    "app_display_name": "Slack",
    "title": "#incidents",
    "body": "PROD DOWN - payments service returning 500s"
  },
  "classification": {
    "folder": "Work",
    "priority": "high"
  }
}
```

## Folder Definitions

| Folder | Description | Example Apps |
|--------|-------------|--------------|
| **Work** | Professional/work-related | Slack, Teams, Jira, 飞书, 钉钉 |
| **Personal** | Friends & family messages | WeChat, WhatsApp, SMS |
| **Promotions** | Marketing & deals | Amazon, 淘宝, email newsletters |
| **Alerts** | System & transactional | Banking, delivery, security |

## Priority Definitions

| Priority | Description | Action |
|----------|-------------|--------|
| **high** | Urgent, needs immediate attention | Immediate push + vibration |
| **medium** | Important but not urgent | Batched every 30 min |
| **low** | Can wait, low importance | Silent, stored only |

## Generation

Dataset was synthetically generated using Claude to ensure:
- Realistic notification content
- Balanced folder distribution
- Natural Chinese and English text
- Diverse app coverage (Chinese apps: 飞书, 钉钉, 微信, 抖音, 小红书)

## License

Apache 2.0 - Same as the main project.

## Citation

```bibtex
@misc{notifai2026,
  title={NotifAI: On-Device Notification Classification},
  author={封一},
  year={2026},
  url={https://github.com/charfeng1/notifai}
}
```
