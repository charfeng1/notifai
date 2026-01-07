#!/usr/bin/env python3
"""Add notifications from Chinese apps to increase coverage."""

import json
import random

# Chinese apps with realistic content
CHINESE_WORK_APPS = [
    ("com.ss.android.lark", "Feishu", "飞书"),
    ("com.alibaba.android.rimet", "DingTalk", "钉钉"),
]

CHINESE_PERSONAL_APPS = [
    ("com.tencent.mm", "WeChat", "微信"),
    ("com.ss.android.ugc.aweme", "Douyin", "抖音"),
    ("com.xingin.xhs", "RedNote", "小红书"),
]

# Feishu/Lark work content (Chinese enterprise messaging)
FEISHU_CONTENT = [
    (5, "紧急通知", "生产环境数据库连接失败，所有服务不可用，技术团队正在处理"),
    (5, "#故障", "支付系统崩溃，用户无法下单，立即响应"),
    (4, "会议提醒", "15分钟后产品评审会，会议室3A"),
    (4, "项目进度", "客户要求今天下午5点前交付演示版本"),
    (3, "代码审查", "请审查PR #245: 添加用户认证模块"),
    (3, "#开发", "新版本已部署到测试环境，请QA团队开始测试"),
    (2, "#闲聊", "谁中午一起吃饭？"),
    (1, "日报提醒", "请提交今日工作日报"),
]

# DingTalk work content
DINGTALK_CONTENT = [
    (5, "紧急审批", "差旅报销审批超时，财务部要求今日完成"),
    (4, "视频会议", "10分钟后全员会议开始，请准时参加"),
    (4, "任务提醒", "项目里程碑即将到期，请尽快完成"),
    (3, "考勤提醒", "您今日尚未打卡，请及时处理"),
    (3, "公告", "公司年会安排已发布，请查看详情"),
    (2, "群消息", "技术部群聊有新消息"),
    (1, "日程提醒", "明日会议提醒"),
]

# WeChat personal content
WECHAT_CONTENT = [
    (5, "爸爸", "你妈妈摔倒了正在医院，快来"),
    (5, "家人", "紧急家庭会议，今晚必须回家"),
    (4, "妈妈", "今晚7点到家吃饭，给你做了你最爱吃的"),
    (4, "老板", "明天早上8点开会，别迟到"),
    (3, "朋友", "周末一起去爬山吗？"),
    (3, "同学群", "下周同学聚会，大家都要来啊"),
    (3, "表姐", "生日快乐！晚上有时间吗一起吃饭"),
    (2, "购物群", "这个商品打折了，要不要拼单"),
    (2, "游戏群", "今晚组队开黑吗"),
    (1, "群聊", "群消息99+"),
]

# Douyin content
DOUYIN_CONTENT = [
    (4, "直播提醒", "你关注的主播正在直播，快来观看"),
    (3, "新消息", "有人评论了你的视频"),
    (3, "点赞通知", "你的作品获得了100个赞"),
    (2, "推荐", "为你推荐感兴趣的内容"),
    (1, "系统通知", "每日推荐已更新"),
]

# RedNote/Xiaohongshu content
REDNOTE_CONTENT = [
    (4, "种草提醒", "你关注的博主发布了新笔记"),
    (3, "互动消息", "有人收藏了你的笔记"),
    (3, "评论通知", "有人评论：这个产品真的好用吗？"),
    (2, "推荐", "根据你的兴趣为你推荐"),
    (1, "每日推荐", "今日热门笔记推荐"),
]

def generate_chinese_entries(start_id, count):
    """Generate entries with Chinese apps."""
    entries = []

    # Distribution
    feishu_count = int(count * 0.15)
    dingtalk_count = int(count * 0.15)
    wechat_count = int(count * 0.40)
    douyin_count = int(count * 0.15)
    rednote_count = count - feishu_count - dingtalk_count - wechat_count - douyin_count

    current_id = start_id

    # Feishu (Work)
    for i in range(feishu_count):
        pkg, app_en, app_cn = random.choice(CHINESE_WORK_APPS)
        if "lark" in pkg:
            priority, title, body = random.choice(FEISHU_CONTENT)
            entries.append({
                "id": str(current_id).zfill(5),
                "notification": {
                    "app": pkg,
                    "app_display_name": app_cn,
                    "title": title,
                    "body": body
                },
                "classification": {
                    "folder": "Work",
                    "priority": priority
                }
            })
            current_id += 1

    # DingTalk (Work)
    for i in range(dingtalk_count):
        pkg, app_en, app_cn = random.choice(CHINESE_WORK_APPS)
        if "rimet" in pkg:
            priority, title, body = random.choice(DINGTALK_CONTENT)
            entries.append({
                "id": str(current_id).zfill(5),
                "notification": {
                    "app": pkg,
                    "app_display_name": app_cn,
                    "title": title,
                    "body": body
                },
                "classification": {
                    "folder": "Work",
                    "priority": priority
                }
            })
            current_id += 1

    # WeChat (Personal)
    for i in range(wechat_count):
        priority, title, body = random.choice(WECHAT_CONTENT)
        entries.append({
            "id": str(current_id).zfill(5),
            "notification": {
                "app": "com.tencent.mm",
                "app_display_name": "微信",
                "title": title,
                "body": body
            },
            "classification": {
                "folder": "Personal",
                "priority": priority
            }
        })
        current_id += 1

    # Douyin (Personal)
    for i in range(douyin_count):
        priority, title, body = random.choice(DOUYIN_CONTENT)
        entries.append({
            "id": str(current_id).zfill(5),
            "notification": {
                "app": "com.ss.android.ugc.aweme",
                "app_display_name": "抖音",
                "title": title,
                "body": body
            },
            "classification": {
                "folder": "Personal",
                "priority": priority
            }
        })
        current_id += 1

    # RedNote (Personal)
    for i in range(rednote_count):
        priority, title, body = random.choice(REDNOTE_CONTENT)
        entries.append({
            "id": str(current_id).zfill(5),
            "notification": {
                "app": "com.xingin.xhs",
                "app_display_name": "小红书",
                "title": title,
                "body": body
            },
            "classification": {
                "folder": "Personal",
                "priority": priority
            }
        })
        current_id += 1

    random.shuffle(entries)
    return entries

if __name__ == "__main__":
    # Generate 2000 additional entries for Chinese apps
    entries = generate_chinese_entries(16001, 2000)

    # Append to training_data.jsonl
    with open("training_data.jsonl", 'a', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"Added {len(entries)} Chinese app notifications to training_data.jsonl")
    print(f"New total entries: {16000 + len(entries)}")

    # Show distribution
    app_counts = {}
    for entry in entries:
        app = entry["notification"]["app_display_name"]
        app_counts[app] = app_counts.get(app, 0) + 1

    print("\nChinese App Distribution:")
    for app, count in sorted(app_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(entries)) * 100
        print(f"  {app}: {count} ({pct:.1f}%)")
