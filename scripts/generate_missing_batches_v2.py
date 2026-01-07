#!/usr/bin/env python3
"""Generate remaining batches efficiently with Chinese app support."""

import json
import random

# Real Android package names with Chinese apps
APPS = {
    "work": [
        ("com.slack", "Slack"),
        ("com.microsoft.teams", "Microsoft Teams"),
        ("com.google.android.gm", "Gmail"),
        ("com.ss.android.lark", "飞书"),  # Feishu
        ("com.alibaba.android.rimet", "钉钉"),  # DingTalk
        ("com.github.android", "GitHub"),
    ],
    "personal": [
        ("com.whatsapp", "WhatsApp"),
        ("com.tencent.mm", "微信"),  # WeChat
        ("com.ss.android.ugc.aweme", "抖音"),  # Douyin
        ("com.xingin.xhs", "小红书"),  # RedNote
        ("org.telegram.messenger", "Telegram"),
        ("com.instagram", "Instagram"),
    ],
    "promotions": [
        ("com.amazon.mShop.android.shopping", "Amazon"),
        ("com.target.ui", "Target"),
        ("com.shopee.ph", "Shopee"),
    ],
    "alerts": [
        ("com.chase.sig.android", "Chase Mobile"),
        ("com.ups.mobile.android", "UPS Mobile"),
        ("com.fedex.ida.android", "FedEx"),
        ("com.ubercab", "Uber"),
    ]
}

# Sample content with natural Chinese
CONTENT_TEMPLATES = {
    "work_urgent": [
        ("PROD DOWN - payment failures", "Work", 5),
        ("紧急：生产环境故障，所有服务中断", "Work", 5),
        ("Security breach detected", "Work", 5),
    ],
    "work_normal": [
        ("PR review needed for feature branch", "Work", 4),
        ("会议提醒：15分钟后产品评审会", "Work", 4),
        ("Sprint planning tomorrow at 2pm", "Work", 3),
        ("团队日报截止时间：下午5点", "Work", 3),
    ],
    "personal_urgent": [
        ("妈妈：你在哪？快回家", "Personal", 5),
        ("Dad: Emergency - call me ASAP", "Personal", 5),
    ],
    "personal_normal": [
        ("到家了吗？外面冷记得穿外套", "Personal", 3),
        ("有人评论了你的视频", "Personal", 3),
        ("Hey! Coffee tomorrow at 3pm?", "Personal", 3),
        ("你关注的博主发布了新笔记", "Personal", 2),
    ],
    "promotions": [
        ("Flash sale 50% OFF - ends tonight!", "Promotions", 2),
        ("限时特卖：iPhone充电线仅9.9元", "Promotions", 2),
        ("Daily deals - check them out", "Promotions", 1),
    ],
    "alerts_urgent": [
        ("Security Alert: Suspicious login detected", "Alerts", 5),
        ("账号异常登录：请确认操作", "Alerts", 5),
    ],
    "alerts_normal": [
        ("Package out for delivery", "Alerts", 3),
        ("Payment confirmed: $523.45", "Alerts", 2),
        ("您的包裹已送达小区驿站", "Alerts", 2),
    ]
}

def generate_entry(entry_id, folder_type):
    """Generate one notification entry."""
    # Select app
    app_pkg, app_name = random.choice(APPS[folder_type])

    # Select content template based on folder
    if folder_type == "work":
        templates = CONTENT_TEMPLATES["work_urgent"] + CONTENT_TEMPLATES["work_normal"]
    elif folder_type == "personal":
        templates = CONTENT_TEMPLATES["personal_urgent"] + CONTENT_TEMPLATES["personal_normal"]
    elif folder_type == "promotions":
        templates = CONTENT_TEMPLATES["promotions"]
    else:  # alerts
        templates = CONTENT_TEMPLATES["alerts_urgent"] + CONTENT_TEMPLATES["alerts_normal"]

    body, folder, priority = random.choice(templates)

    #Vary title slightly
    titles = {
        "Work": ["#engineering", "Project Update", "Meeting Reminder", "紧急通知", "任务指派"],
        "Personal": ["Mom", "Friend", "妈妈", "朋友", "Group Chat"],
        "Promotions": ["Deal Alert!", "Limited Time", "Special Offer", "限时优惠"],
        "Alerts": ["Security", "Delivery Update", "Transaction", "账号提醒"]
    }
    title = random.choice(titles[folder])

    return {
        "id": entry_id,
        "notification": {
            "app": app_pkg,
            "app_display_name": app_name,
            "title": title,
            "body": body
        },
        "classification": {
            "folder": folder,
            "priority": priority
        }
    }

def generate_batch(batch_num, id_start, id_end):
    """Generate one batch ensuring 35% Chinese apps."""
    entries = []
    total = id_end - id_start + 1

    # Distribution
    work_count = int(total * 0.36)
    personal_count = int(total * 0.31)
    promotions_count = int(total * 0.18)
    alerts_count = total - work_count - personal_count - promotions_count

    current_id = id_start

    # Generate Work
    for _ in range(work_count):
        entries.append(generate_entry(str(current_id).zfill(5), "work"))
        current_id += 1

    # Generate Personal
    for _ in range(personal_count):
        entries.append(generate_entry(str(current_id).zfill(5), "personal"))
        current_id += 1

    # Generate Promotions
    for _ in range(promotions_count):
        entries.append(generate_entry(str(current_id).zfill(5), "promotions"))
        current_id += 1

    # Generate Alerts
    for _ in range(alerts_count):
        entries.append(generate_entry(str(current_id).zfill(5), "alerts"))
        current_id += 1

    random.shuffle(entries)

    # Write to file
    output_path = f"data/batch_{str(batch_num).zfill(2)}.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"Generated {output_path}: {len(entries)} entries")
    return len(entries)

if __name__ == "__main__":
    # Missing batches with their ID ranges
    missing = [
        (4, 1201, 1600),
        (14, 5201, 5600),
        (20, 7601, 8000),
        (22, 8401, 8800),
        (24, 9201, 9600),
        (28, 10801, 11200),
        (32, 12401, 12800),
        (34, 13201, 13600),
    ]

    total = 0
    for batch_num, start_id, end_id in missing:
        count = generate_batch(batch_num, start_id, end_id)
        total += count

    print(f"\nTotal generated: {total} entries across {len(missing)} batches")
