import json
import random

# Comprehensive app data for diversity
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

# Work content templates with realistic scenarios
WORK_CONTENT = [
    # High priority incidents
    (5, "slack", "🚨 PROD INCIDENT", "Database connection pool exhausted on payments-api. All transactions failing. On-call team engaged."),
    (5, "slack", "#incidents", "CRITICAL: Auth service down in us-west-1. Customer login failing. POC: @devops"),
    (5, "jira", "P1 - Security Breach", "Unauthorized access detected in customer database. Escalating to security team immediately."),
    (5, "github", "⚠️ URGENT CODE REVIEW", "CVE-2024-12345 patch needs immediate merge and deployment"),
    (5, "slack", "ALERT: Service Outage", "Search service API is returning 503 errors. Impact: 15% of users affected."),

    # High priority meetings/urgent items
    (4, "slack", "Board Meeting Starting", "Board meeting starts in 10 minutes. Join Zoom: zoom.us/j/12345"),
    (4, "calendar", "Interview with candidate", "Technical interview with Sarah Lee in 15 minutes - Room 4B"),
    (4, "gmail", "CFO - Quarterly Review", "Can you send me the final numbers before 3pm? CFO presentation is tomorrow."),
    (4, "teams", "Client Call Reminder", "Your meeting with Acme Corp starts in 5 minutes"),
    (4, "slack", "ACTION REQUIRED", "Your PR review is holding up the release. 2 files need approval."),

    # Medium priority - important but not urgent
    (3, "slack", "#engineering", "Deployed v2.3.1 to staging. Ready for QA testing."),
    (3, "github", "PR Review Needed", "Please review: Add caching layer for search API - 12 files changed"),
    (3, "jira", "Sprint Planning", "Sprint 2025-Q1-02 planning session scheduled for tomorrow 2pm"),
    (3, "linear", "Design Review", "New onboarding flow designs ready for feedback"),
    (3, "asana", "Project Status", "Weekly project update: 3/5 milestones complete this week"),
    (3, "teams", "Team Standup", "Your standup updates are due by end of day"),
    (3, "outlook", "Meeting rescheduled", "Your 2pm meeting has been moved to 3:30pm"),

    # Low priority
    (2, "slack", "#random", "Anyone want to grab lunch? Going to the place downtown"),
    (2, "notion", "Wiki Updated", "Documentation updated: New API endpoint docs available"),
    (2, "monday", "Task assigned", "You've been assigned: Update marketing landing page"),
    (2, "gmail", "Team Lunch", "Thursday team lunch is confirmed for 12:30pm at Bella Italia"),
    (2, "slack", "#announcements", "Reminder: Office is closed on Jan 20 for MLK day"),

    # Noise/bot messages
    (1, "slack", "Daily Digest", "Standup reminders: You have 5 unread messages in #standup"),
    (1, "slack", "Workflow", "Automated workflow: Issue closed by PR merge"),
    (1, "jira", "Comment added", "Someone commented on your issue #3456"),
    (1, "github", "Status check", "Continuous integration passed all tests"),
]

# Personal content with multiple languages
PERSONAL_CONTENT = [
    # Emergency/urgent
    (5, "whatsapp", "Mom", "Where are you?? You were supposed to be home 2 hours ago"),
    (5, "telegram", "Doctor's Office", "Your father's surgery time has moved up to 2pm. Get to hospital now."),
    (5, "wechat", "奶奶", "你爷爷出车祸了，赶快来医院"),

    # Important
    (4, "wechat", "你好", "今晚7点聚餐还来吗？我们都到了"),
    (4, "whatsapp", "Sarah", "The landlord wants to meet today at 4pm to discuss the lease"),
    (4, "imessage", "Mike", "Do you have time for coffee tomorrow? Need to talk about something important"),
    (4, "line", "田中さん", "明日の約束まだいいですか？確認したいことがあります"),
    (4, "messenger", "Dad", "Son, can you call me ASAP? Important family matter"),

    # Normal conversation
    (3, "wechat", "妈妈", "到家了吗？外面冷记得穿外套"),
    (3, "whatsapp", "Alex", "Yeah, the movie was pretty good! Want to go again next week?"),
    (3, "telegram", "Group Chat", "haha that's hilarious 😂😂😂"),
    (3, "instagram", "David Chen", "You're looking fit lately! What's your routine?"),
    (3, "messenger", "Jessica", "Did you see the new coffee place opened near the office?"),
    (3, "snapchat", "Emma", "At the beach! Check my story 🏖️"),
    (3, "wechat", "老李", "这周有空吗？想请你吃饭谢谢你上次的帮助"),
    (3, "viber", "Priya", "Haan, I'm coming to the wedding! So excited!"),
    (3, "whatsapp", "Cousin", "Happy birthday! Hope you have a great day"),
    (3, "telegram", "College Friends", "Class at 2pm tomorrow, don't be late!"),

    # Casual/low priority
    (2, "whatsapp", "Work Group Chat", "lol who set the Zoom background to that 😂"),
    (2, "wechat", "classmates group", "有人做完数学作业吗？能分享一下吗"),
    (2, "telegram", "Gaming Squad", "Dota 2 tonight? Starting at 9pm"),
    (2, "instagram", "Random Friend", "Liked your photo from yesterday 👍"),
    (2, "snapchat", "Friend Group", "Anyone going to the concert?"),
    (2, "whatsapp", "Sports Group", "Game highlights are up on YouTube"),

    # Muted conversations (low priority)
    (1, "whatsapp", "Muted Group", "Message in muted group"),
    (1, "wechat", "Business Contact", "Business message - muted"),
    (1, "telegram", "Broadcast List", "Broadcasting message to all subscribers"),
]

# Promotions content
PROMOTIONS_CONTENT = [
    # Time-sensitive deals (rarely high priority)
    (4, "amazon", "⚡ Flash Deal Alert", "48-hour Lightning Deal: iPhone 15 Pro - 30% OFF. Only 2 left in stock!"),
    (4, "shopee", "限时特卖 9.9元包邮", "iPhone充电线仅需9.9元！今晚11点59分截止"),

    # Normal promotions
    (3, "target", "🎯 Weekly Deals", "Save $5 on $25 beauty purchase. Valid this week only. Use code: BEAUTY5"),
    (3, "amazon", "Your Deals", "Based on your browsing: Smart home devices 20-40% off this week"),
    (3, "lazada", "你的淘淘券已领取", "满99减20优惠券已自动使用，赶紧下单"),
    (3, "walmart", "Rollback Prices", "Great Value items now even cheaper. Save up to 50%"),
    (3, "newsletter", "Weekly Newsletter", "This week's top stories and recommendations just for you"),
    (3, "ebay", "Bid to Win", "Last chance: Vintage camera - Auction ends in 2 hours!"),
    (3, "shopee", "限时促销", "春季大促！全店服装鞋帽满99元减20元"),

    # Generic marketing (lower priority)
    (2, "hm", "New Collection", "Spring Collection is here! Explore 500+ new items"),
    (2, "aliexpress", "AliExpress 双11 狂欢", "11月11号 超级大促 折扣商品每日更新"),
    (2, "coupon", "Deals Near You", "Save at local restaurants this week: See 10+ new coupons"),
    (2, "target", "Member Exclusive", "As a VIP member, enjoy 15% off all purchases"),
    (2, "shopee", "闪购推荐", "今日闪购热门商品：美妆护肤专场"),
    (2, "walmart", "Today's Rollback", "Checkout these items on sale today only"),

    # Spam/unwanted
    (1, "amazon", "Recommended for you", "Check out these products similar to your searches"),
    (1, "newsletter", "Daily Email", "Don't miss out on today's deals!"),
    (1, "lazada", "推荐商品", "根据你的浏览记录为你推荐"),
    (1, "aliexpress", "每日推送", "你关注的商品降价了，快来看看"),
    (1, "ebay", "Item you watched", "Someone else is watching this item. Stock limited!"),
]

# Alerts content - realistic scenarios
ALERTS_CONTENT = [
    # Security alerts (high priority)
    (5, "chase", "Security Alert", "Suspicious login detected from Sydney, Australia. Was this you? Confirm: Yes/No"),
    (5, "bofa", "Fraud Alert", "Your card was declined due to suspicious activity. Please call us."),
    (5, "wellsfargo", "Account Compromise", "Multiple failed login attempts detected. Your account is temporarily locked."),
    (5, "chase", "Card Fraud Alert", "Unauthorized transaction of $2,450 detected in NYC. Take action now."),

    # Important time-sensitive alerts
    (4, "ups", "Delivery Today", "Your package will arrive by 8pm today. Track: 1Z999AA10123456784"),
    (4, "fedex", "Out for Delivery", "Your shipment is out for delivery. Expected arrival: 2-6pm"),
    (4, "doordash", "Order Arriving Soon", "Driver is 5 minutes away with your order. Apartment code: 1234"),
    (4, "uber", "Driver Cancelled", "Your ride request was cancelled. Request a new one?"),
    (4, "calendar", "Appointment Reminder", "Doctor appointment tomorrow at 2pm. Dr. Smith, 123 Main St. Confirm attendance"),
    (4, "wellsfargo", "Payment Due", "Your credit card payment of $523 is due tomorrow. Pay now"),

    # Transaction confirmations
    (3, "chase", "Payment Confirmed", "Your payment of $523.45 to Con Edison has been processed"),
    (3, "bofa", "Card Payment", "Confirmed: $89.99 charged to your Visa ending in 4242 at Target"),
    (3, "amazon", "Delivery Confirmation", "Your order has been delivered. Track your package anytime"),
    (3, "uber", "Trip Complete", "Trip Summary: $28.55 charged. From Airport to Downtown. Rating: 5/5"),
    (3, "doordash", "Order Confirmed", "Order confirmed! Arriving in about 30 minutes"),
    (3, "usps", "Package Delivered", "Your package was delivered and left in your mailbox"),
    (3, "fedex", "Signature Required", "Signature will be required for delivery. Update preferred time?"),
    (3, "ups", "Package Status", "Your package left the distribution center and is on the way"),

    # Low priority system notifications
    (2, "system", "Low Battery", "Battery at 15%. Plug in your device soon"),
    (2, "system", "Update Available", "iOS 17.3.1 update is available. Download now?"),
    (2, "calendar", "Upcoming Event", "Birthday party tomorrow at 7pm - Don't forget!"),
    (2, "wellsfargo", "Statement Ready", "Your monthly statement is ready to view"),
    (2, "chase", "Rewards Earned", "You earned 500 points this month. Redeem today!"),

    # Routine alerts
    (1, "chase", "Daily Balance", "Your current balance is $4,256.78"),
    (1, "system", "Storage Full", "Storage is 90% full. Remove some items"),
    (1, "bofa", "Account Update", "Your business account deposit has been processed"),
    (1, "calendar", "Event Reminder", "Your dentist appointment reminder"),
]

# Spanish content examples for diversity
SPANISH_CONTENT = [
    (4, "whatsapp", "Mamá", "¿Ya llegaste a casa? Ten cuidado en el camino"),
    (3, "wechat", "Jorge", "¿Vienes a la fiesta este sábado? Todos van a estar"),
    (3, "telegram", "Grupo Trabajo", "Reunión a las 3pm en la sala 4B"),
    (3, "whatsapp", "Amigos", "¿Alguien sabe dónde está el lugar de la reunión?"),
    (2, "messenger", "Amigos", "Alguien quiere jugar futbol mañana?"),
    (2, "whatsapp", "Grupo", "¿Vamos a comer al lugar de siempre?"),
]

# Hindi content examples
HINDI_CONTENT = [
    (4, "whatsapp", "माताजी", "रास्ते में ध्यान रखना। बारिश हो रही है"),
    (3, "telegram", "परिवार", "कल शाम 6 बजे घर पर सब आ जाना"),
    (3, "messenger", "राज", "तुम्हारे प्रोजेक्ट की मीटिंग कल 10 बजे है"),
    (3, "whatsapp", "मित्र", "क्या तुम कल मेरे पार्टी में आ रहे हो?"),
    (2, "whatsapp", "दोस्त", "क्रिकेट मैच देखने चलते हो आज?"),
]

# Japanese content examples
JAPANESE_CONTENT = [
    (4, "line", "母親", "帰ったら電話をください。心配しています"),
    (3, "telegram", "同僚", "明日の会議は2時に会議室Aです"),
    (3, "line", "友達", "このレストラン知ってますか？新しくオープンしたんです"),
    (3, "whatsapp", "グループ", "明日の飲み会は何時からですか"),
    (2, "whatsapp", "チーム", "明日のサッカーの試合は何時からですか？"),
]

# German content examples
GERMAN_CONTENT = [
    (4, "whatsapp", "Mutter", "Bitte ruf mich an wenn du nach Hause kommst"),
    (3, "telegram", "Team", "Das Meeting morgen ist um 14 Uhr im Konferenzraum"),
    (3, "messenger", "Thomas", "Kommst du zum Fussballspiel am Samstag?"),
    (2, "whatsapp", "Freunde", "Wer hat Lust auf Kino heute Abend?"),
]

# French content examples
FRENCH_CONTENT = [
    (4, "whatsapp", "Maman", "Appelle-moi quand tu arriveras à la maison"),
    (3, "telegram", "Équipe", "La réunion est demain à 15h dans la salle de conférence"),
    (3, "messenger", "Pierre", "Tu viens à la fête ce weekend?"),
    (2, "whatsapp", "Amis", "Qui veut aller au cinéma ce soir?"),
]

# Generate all data
entries = []
id_start = 3201
id_end = 3600
total_entries = id_end - id_start + 1

# Calculate distribution for balanced coverage
work_count = int(total_entries * 0.35)  # 140 work notifications
personal_count = int(total_entries * 0.35)  # 140 personal notifications
promotions_count = int(total_entries * 0.15)  # 60 promotional notifications
alerts_count = total_entries - work_count - personal_count - promotions_count  # 60 alerts

# Create a mapping dictionary for all apps
ALL_APPS = {}
for app, name in WORK_APPS + PERSONAL_APPS + PROMOTIONS_APPS + ALERTS_APPS:
    ALL_APPS[app] = name

# Generate Work notifications
for i in range(work_count):
    entry_id = str(id_start + len(entries)).zfill(5)
    priority, app, title, body = random.choice(WORK_CONTENT)
    app_name = ALL_APPS.get(app, "Work App")

    entry = {
        "id": entry_id,
        "notification": {
            "app": app,
            "app_display_name": app_name,
            "title": title,
            "body": body
        },
        "classification": {
            "folder": "Work",
            "priority": priority
        }
    }
    entries.append(entry)

# Generate Personal notifications
for i in range(personal_count):
    entry_id = str(id_start + len(entries)).zfill(5)
    # Mix of all language content
    content_pool = PERSONAL_CONTENT + SPANISH_CONTENT + HINDI_CONTENT + JAPANESE_CONTENT + GERMAN_CONTENT + FRENCH_CONTENT
    priority, app, title, body = random.choice(content_pool)
    app_name = ALL_APPS.get(app, "Personal App")

    entry = {
        "id": entry_id,
        "notification": {
            "app": app,
            "app_display_name": app_name,
            "title": title,
            "body": body
        },
        "classification": {
            "folder": "Personal",
            "priority": priority
        }
    }
    entries.append(entry)

# Generate Promotions notifications
for i in range(promotions_count):
    entry_id = str(id_start + len(entries)).zfill(5)
    priority, app, title, body = random.choice(PROMOTIONS_CONTENT)
    app_name = ALL_APPS.get(app, "Shop App")

    entry = {
        "id": entry_id,
        "notification": {
            "app": app,
            "app_display_name": app_name,
            "title": title,
            "body": body
        },
        "classification": {
            "folder": "Promotions",
            "priority": priority
        }
    }
    entries.append(entry)

# Generate Alerts notifications
for i in range(alerts_count):
    entry_id = str(id_start + len(entries)).zfill(5)
    priority, app, title, body = random.choice(ALERTS_CONTENT)
    app_name = ALL_APPS.get(app, "Alert App")

    entry = {
        "id": entry_id,
        "notification": {
            "app": app,
            "app_display_name": app_name,
            "title": title,
            "body": body
        },
        "classification": {
            "folder": "Alerts",
            "priority": priority
        }
    }
    entries.append(entry)

# Shuffle entries to randomize order
random.shuffle(entries)

# Write to JSONL file
output_path = "E:/projects/notif/data/batch_09.jsonl"
with open(output_path, 'w', encoding='utf-8') as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f"Generated {len(entries)} notification entries")
print(f"Saved to: {output_path}")
print(f"\nDistribution:")
print(f"Work: {work_count} entries")
print(f"Personal: {personal_count} entries")
print(f"Promotions: {promotions_count} entries")
print(f"Alerts: {alerts_count} entries")

# Count actual priority distribution
priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for entry in entries:
    p = entry['classification']['priority']
    priority_counts[p] += 1

print(f"\nPriority Distribution:")
for p in range(1, 6):
    pct = (priority_counts[p] / len(entries)) * 100
    print(f"Priority {p}: {priority_counts[p]} ({pct:.1f}%)")

# Count apps
app_counts = {}
for entry in entries:
    app = entry['notification']['app']
    app_counts[app] = app_counts.get(app, 0) + 1

print(f"\nTop 10 Apps:")
for app, count in sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {app}: {count}")

# Verify all IDs are unique and in range
all_ids = [entry['id'] for entry in entries]
print(f"\nVerification:")
print(f"Total entries: {len(entries)}")
print(f"Unique IDs: {len(set(all_ids))} (should be {len(entries)})")
print(f"All IDs in range [03201-03600]: {all('03201' <= id <= '03600' for id in all_ids)}")
print(f"ID range in generated data: {min(all_ids)} to {max(all_ids)}")
