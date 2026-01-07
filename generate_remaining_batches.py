#!/usr/bin/env python3
"""Generate remaining missing batches quickly."""

import json
import random
import sys

# Use the same data from batch_09 generation script
WORK_APPS = [
    ("slack", "Slack"),
    ("teams", "Microsoft Teams"),
    ("gmail", "Gmail"),
    ("outlook", "Outlook"),
    ("jira", "Jira"),
    ("github", "GitHub"),
    ("linear", "Linear"),
    ("notion", "Notion"),
    ("asana", "Asana"),
    ("monday", "Monday.com"),
]

PERSONAL_APPS = [
    ("whatsapp", "WhatsApp"),
    ("wechat", "WeChat"),
    ("telegram", "Telegram"),
    ("imessage", "iMessage"),
    ("messenger", "Facebook Messenger"),
    ("viber", "Viber"),
    ("snapchat", "Snapchat"),
    ("twitter", "Twitter"),
    ("instagram", "Instagram"),
    ("line", "LINE"),
]

PROMOTIONS_APPS = [
    ("amazon", "Amazon"),
    ("shopee", "Shopee"),
    ("lazada", "Lazada"),
    ("target", "Target"),
    ("walmart", "Walmart"),
    ("ebay", "eBay"),
    ("aliexpress", "AliExpress"),
    ("hm", "H&M"),
    ("newsletter", "Newsletter"),
    ("coupon", "Coupons"),
]

ALERTS_APPS = [
    ("chase", "Chase Mobile"),
    ("bofa", "Bank of America"),
    ("wellsfargo", "Wells Fargo"),
    ("ups", "UPS"),
    ("fedex", "FedEx"),
    ("usps", "USPS"),
    ("uber", "Uber"),
    ("doordash", "DoorDash"),
    ("system", "System"),
    ("calendar", "Calendar"),
]

WORK_CONTENT = [
    (5, "slack", "🚨 PROD INCIDENT", "Database connection pool exhausted on payments-api. All transactions failing. On-call team engaged."),
    (5, "slack", "#incidents", "CRITICAL: Auth service down in us-west-1. Customer login failing. POC: @devops"),
    (5, "jira", "P1 - Security Breach", "Unauthorized access detected in customer database. Escalating to security team immediately."),
    (5, "github", "⚠️ URGENT CODE REVIEW", "CVE-2024-12345 patch needs immediate merge and deployment"),
    (4, "slack", "Board Meeting Starting", "Board meeting starts in 10 minutes. Join Zoom: zoom.us/j/12345"),
    (4, "calendar", "Interview with candidate", "Technical interview with Sarah Lee in 15 minutes - Room 4B"),
    (4, "gmail", "CFO - Quarterly Review", "Can you send me the final numbers before 3pm? CFO presentation is tomorrow."),
    (3, "slack", "#engineering", "Deployed v2.3.1 to staging. Ready for QA testing."),
    (3, "github", "PR Review Needed", "Please review: Add caching layer for search API - 12 files changed"),
    (3, "jira", "Sprint Planning", "Sprint 2025-Q1-02 planning session scheduled for tomorrow 2pm"),
    (2, "slack", "#random", "Anyone want to grab lunch? Going to the place downtown"),
    (2, "notion", "Wiki Updated", "Documentation updated: New API endpoint docs available"),
    (1, "slack", "Daily Digest", "Standup reminders: You have 5 unread messages in #standup"),
]

PERSONAL_CONTENT = [
    (5, "whatsapp", "Mom", "Where are you?? You were supposed to be home 2 hours ago"),
    (4, "wechat", "你好", "今晚7点聚餐还来吗？我们都到了"),
    (4, "whatsapp", "Sarah", "The landlord wants to meet today at 4pm to discuss the lease"),
    (3, "wechat", "妈妈", "到家了吗？外面冷记得穿外套"),
    (3, "whatsapp", "Alex", "Yeah, the movie was pretty good! Want to go again next week?"),
    (3, "telegram", "Group Chat", "haha that's hilarious 😂😂😂"),
    (2, "whatsapp", "Work Group Chat", "lol who set the Zoom background to that 😂"),
    (1, "whatsapp", "Muted Group", "Message in muted group"),
]

PROMOTIONS_CONTENT = [
    (4, "amazon", "⚡ Flash Deal Alert", "48-hour Lightning Deal: iPhone 15 Pro - 30% OFF. Only 2 left in stock!"),
    (3, "target", "🎯 Weekly Deals", "Save $5 on $25 beauty purchase. Valid this week only. Use code: BEAUTY5"),
    (3, "amazon", "Your Deals", "Based on your browsing: Smart home devices 20-40% off this week"),
    (2, "hm", "New Collection", "Spring Collection is here! Explore 500+ new items"),
    (1, "amazon", "Recommended for you", "Check out these products similar to your searches"),
]

ALERTS_CONTENT = [
    (5, "chase", "Security Alert", "Suspicious login detected from Sydney, Australia. Was this you? Confirm: Yes/No"),
    (4, "ups", "Delivery Today", "Your package will arrive by 8pm today. Track: 1Z999AA10123456784"),
    (4, "fedex", "Out for Delivery", "Your shipment is out for delivery. Expected arrival: 2-6pm"),
    (3, "chase", "Payment Confirmed", "Your payment of $523.45 to Con Edison has been processed"),
    (2, "system", "Low Battery", "Battery at 15%. Plug in your device soon"),
    (1, "chase", "Daily Balance", "Your current balance is $4,256.78"),
]

ALL_APPS = {}
for app, name in WORK_APPS + PERSONAL_APPS + PROMOTIONS_APPS + ALERTS_APPS:
    ALL_APPS[app] = name

def generate_batch(batch_num, id_start, id_end):
    """Generate one batch of 400 entries."""
    entries = []
    total_entries = id_end - id_start + 1

    work_count = int(total_entries * 0.35)
    personal_count = int(total_entries * 0.35)
    promotions_count = int(total_entries * 0.15)
    alerts_count = total_entries - work_count - personal_count - promotions_count

    # Work
    for i in range(work_count):
        entry_id = str(id_start + len(entries)).zfill(5)
        priority, app, title, body = random.choice(WORK_CONTENT)
        entries.append({
            "id": entry_id,
            "notification": {
                "app": app,
                "app_display_name": ALL_APPS[app],
                "title": title,
                "body": body
            },
            "classification": {
                "folder": "Work",
                "priority": priority
            }
        })

    # Personal
    for i in range(personal_count):
        entry_id = str(id_start + len(entries)).zfill(5)
        priority, app, title, body = random.choice(PERSONAL_CONTENT)
        entries.append({
            "id": entry_id,
            "notification": {
                "app": app,
                "app_display_name": ALL_APPS[app],
                "title": title,
                "body": body
            },
            "classification": {
                "folder": "Personal",
                "priority": priority
            }
        })

    # Promotions
    for i in range(promotions_count):
        entry_id = str(id_start + len(entries)).zfill(5)
        priority, app, title, body = random.choice(PROMOTIONS_CONTENT)
        entries.append({
            "id": entry_id,
            "notification": {
                "app": app,
                "app_display_name": ALL_APPS[app],
                "title": title,
                "body": body
            },
            "classification": {
                "folder": "Promotions",
                "priority": priority
            }
        })

    # Alerts
    for i in range(alerts_count):
        entry_id = str(id_start + len(entries)).zfill(5)
        priority, app, title, body = random.choice(ALERTS_CONTENT)
        entries.append({
            "id": entry_id,
            "notification": {
                "app": app,
                "app_display_name": ALL_APPS[app],
                "title": title,
                "body": body
            },
            "classification": {
                "folder": "Alerts",
                "priority": priority
            }
        })

    random.shuffle(entries)

    output_path = f"data/batch_{str(batch_num).zfill(2)}.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"Generated batch_{str(batch_num).zfill(2)}.jsonl: {len(entries)} entries")
    return len(entries)

if __name__ == "__main__":
    missing_batches = [4, 8, 12, 14, 15, 20, 22, 24, 28, 29, 32, 34, 35]

    total_generated = 0
    for batch_num in missing_batches:
        id_start = (batch_num - 1) * 400 + 1
        id_end = batch_num * 400
        count = generate_batch(batch_num, id_start, id_end)
        total_generated += count

    print(f"\\nTotal generated across all batches: {total_generated}")
    print(f"Expected: {len(missing_batches) * 400}")
