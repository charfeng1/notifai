# Claude Agent Guidelines: Synthetic Notification Data Generation

## Your Task

Generate realistic synthetic notification data for training a notification classification model. Each notification should be classified into one of four folders with an appropriate priority score.

## Output Format

Generate data in JSONL format (one JSON object per line):

```jsonl
{"id": "001", "notification": {"app": "slack", "app_display_name": "Slack", "title": "#incidents", "body": "PROD DOWN - payments service returning 500s"}, "classification": {"folder": "Work", "priority": 5}}
{"id": "002", "notification": {"app": "wechat", "app_display_name": "WeChat", "title": "Mom", "body": "到家了吗"}, "classification": {"folder": "Personal", "priority": 4}}
```

## Schema Requirements

Each entry must have:

```json
{
  "id": "unique_string",
  "notification": {
    "app": "package_name",
    "app_display_name": "Human Readable Name",
    "title": "Notification title",
    "body": "Notification body text"
  },
  "classification": {
    "folder": "Work|Personal|Promotions|Alerts",
    "priority": 1-5
  }
}
```

### Field Rules

- `id`: Unique identifier (sequential numbers are fine: "001", "002", etc.)
- `app`: **Android package name** in reverse domain notation (e.g., "com.slack", "com.google.android.gm", "com.tencent.mm")
- `app_display_name`: User-facing app name (e.g., "Slack", "Gmail", "微信")
- `title`: Short notification title (0-100 chars)
- `body`: Notification body text (0-500 chars)
- `folder`: Must be exactly one of: `Work`, `Personal`, `Promotions`, `Alerts`
- `priority`: Integer 1-5 where 1=ignore, 2=low, 3=normal, 4=important, 5=urgent

## Folder Definitions

### Work
Professional messages from work apps like Slack, Jira, Teams, work email, GitHub, Linear, Feishu, DingTalk, etc.

**Examples:**
- Slack messages from work channels
- Jira issue updates
- Work email notifications
- GitHub PR reviews
- Calendar reminders for meetings
- Feishu/Lark enterprise messaging (Chinese)
- DingTalk/钉钉 work notifications (Chinese)

**Priority guidelines:**
- 5: Production incidents, urgent escalations, immediate blockers
- 4: PR reviews needed, important updates, meeting starting soon
- 3: General work messages, non-urgent updates
- 2: FYI notifications, low-priority mentions
- 1: Noise from automated bots

### Personal
Messages from friends and family via messaging apps.

**Examples:**
- WhatsApp/WeChat/Telegram messages from contacts
- SMS from family members
- iMessage conversations
- Social media DMs from friends
- Douyin/抖音 notifications (Chinese short video)
- Xiaohongshu/小红书/RedNote social updates (Chinese lifestyle)

**Priority guidelines:**
- 5: Emergency messages from family
- 4: Important personal matters, time-sensitive plans
- 3: Normal conversation, casual messages
- 2: Group chat chatter
- 1: Muted conversation notifications

### Promotions
Marketing, deals, spam, promotional content from shopping and service apps.

**Examples:**
- Retail sales notifications (Amazon, Target, etc.)
- Email marketing campaigns
- App promotional push notifications
- Coupon codes and discount alerts
- Newsletter digests

**Priority guidelines:**
- 5: Never (promotions are never urgent)
- 4: Rare (only if time-sensitive deal user explicitly wants)
- 3: Normal promotional content
- 2: Generic marketing
- 1: Spam, unwanted promotions

### Alerts
Banking, security, system notifications, delivery updates, transactional messages.

**Examples:**
- Bank transaction alerts
- Package delivery updates
- Security/login alerts
- System notifications (low battery, etc.)
- Appointment reminders
- Payment confirmations

**Priority guidelines:**
- 5: Security alerts, suspicious activity, fraud warnings
- 4: Important deliveries, payment failures, appointment in 15min
- 3: Normal transaction confirmations, delivery updates
- 2: Low-importance system notifications
- 1: Routine automated alerts

## Generation Guidelines

### Diversity Requirements

Generate diverse notifications across:

1. **Languages**: Include English, Chinese, Spanish, Hindi, and other languages where appropriate
   - Chinese family messages are common (WeChat)
   - Work tools are typically English
   - Shopping apps may be in user's native language

2. **Apps**: Cover wide range of common apps with **real Android package names**
   - Work: Slack (com.slack), Teams (com.microsoft.teams), Gmail (com.google.android.gm), Feishu/飞书 (com.ss.android.lark), DingTalk/钉钉 (com.alibaba.android.rimet), Jira, GitHub, Notion
   - Personal: WhatsApp (com.whatsapp), WeChat/微信 (com.tencent.mm), Douyin/抖音 (com.ss.android.ugc.aweme), RedNote/小红书 (com.xingin.xhs), Telegram (org.telegram.messenger), Messenger, Instagram, LINE
   - Promotions: Amazon (com.amazon.mShop.android.shopping), Shopee (com.shopee.ph), Lazada, Target (com.target.ui), Taobao/淘宝, JD/京东
   - Alerts: Chase (com.chase.sig.android), UPS (com.ups.mobile.android), FedEx (com.fedex.ida.android), Uber (com.ubercab), DoorDash, system (android)

3. **Scenarios**: Realistic use cases
   - Work incidents, PR reviews, meeting reminders
   - Family emergencies, casual chat, making plans
   - Sales, coupons, marketing emails
   - Package deliveries, bank alerts, security warnings

4. **Message length**: Vary from very short (1 word) to longer (200+ chars)

5. **Priority distribution**:
   - Avoid making everything priority 5
   - Most notifications should be 2-3
   - Priority 5 should be rare and genuinely urgent
   - Use priority 1 for noise

### Realism Checks

- **Work notifications** should reference realistic technical terms, channel names, project names
- **Chinese messages** should use natural conversational Chinese, not translations
- **Promotions** should sound like actual marketing copy with percentages, urgency tactics
- **Banking alerts** should have realistic transaction amounts and merchant names
- **Delivery notifications** should include tracking numbers, delivery time windows

### Chinese App Requirements

**IMPORTANT:** At least 30-40% of your generated notifications should be from Chinese apps with natural Chinese content.

**Chinese Work Apps (Feishu/DingTalk):**
- Package names: `com.ss.android.lark` (Feishu/飞书), `com.alibaba.android.rimet` (DingTalk/钉钉)
- Content: Project updates, meeting reminders, approval requests, team messages
- Use natural Chinese business language: "紧急通知", "会议提醒", "项目进度", "审批", "考勤"
- Examples: "生产环境故障", "客户要求今天下午交付", "请审查代码"

**Chinese Personal Apps:**
- WeChat (com.tencent.mm/微信): Family messages, friend chat, group conversations
- Douyin (com.ss.android.ugc.aweme/抖音): Video likes, comments, live stream notifications
- RedNote (com.xingin.xhs/小红书): Social updates, product recommendations, comments

**Chinese Personal Content Examples:**
- Family urgent: "爸爸住院了快来医院", "妈妈找你有急事"
- Family normal: "到家了吗", "今晚回来吃饭吗", "外面冷记得穿外套"
- Friends: "周末去哪玩", "一起吃饭吗", "你看到我发的消息了吗"
- Social: "有人点赞了你的视频", "有人评论了你的笔记", "你关注的博主更新了"

### What to Avoid

- Don't make every notification urgent (priority 5)
- Don't use placeholder text like "Lorem ipsum" or "Test message"
- Don't classify incorrectly (e.g., a marketing email as "Personal")
- Don't generate duplicate `id` values
- Don't use fictional apps that don't exist
- Don't generate offensive, harmful, or inappropriate content

## Quality Standards

Your synthetic data will be validated against the schema. Ensure:
- ✅ All required fields present
- ✅ Folder names exactly match: `Work`, `Personal`, `Promotions`, `Alerts`
- ✅ Priority is integer 1-5
- ✅ Unique IDs
- ✅ Valid JSON formatting
- ✅ Realistic, diverse content

## Example Set

```jsonl
{"id": "001", "notification": {"app": "com.slack", "app_display_name": "Slack", "title": "#incidents", "body": "PROD DOWN - payments service returning 500s"}, "classification": {"folder": "Work", "priority": 5}}
{"id": "002", "notification": {"app": "com.tencent.mm", "app_display_name": "微信", "title": "妈妈", "body": "到家了吗？外面冷记得穿外套"}, "classification": {"folder": "Personal", "priority": 3}}
{"id": "003", "notification": {"app": "com.ss.android.lark", "app_display_name": "飞书", "title": "紧急通知", "body": "生产环境数据库故障，所有服务暂停，技术团队正在抢修"}, "classification": {"folder": "Work", "priority": 5}}
{"id": "004", "notification": {"app": "com.ss.android.ugc.aweme", "app_display_name": "抖音", "title": "新消息", "body": "有人评论了你的视频：哈哈哈太搞笑了"}, "classification": {"folder": "Personal", "priority": 3}}
{"id": "005", "notification": {"app": "com.amazon.mShop.android.shopping", "app_display_name": "Amazon", "title": "Your order has shipped!", "body": "Good news! Your package will arrive tomorrow by 8pm. Track: TBA123456789"}, "classification": {"folder": "Alerts", "priority": 3}}
{"id": "006", "notification": {"app": "com.target.ui", "app_display_name": "Target", "title": "🎯 50% OFF Everything!", "body": "Flash sale ends tonight! Use code SAVE50 at checkout. Shop now →"}, "classification": {"folder": "Promotions", "priority": 2}}
{"id": "007", "notification": {"app": "com.xingin.xhs", "app_display_name": "小红书", "title": "种草提醒", "body": "你关注的博主分享了新的美妆教程"}, "classification": {"folder": "Personal", "priority": 3}}
{"id": "008", "notification": {"app": "com.alibaba.android.rimet", "app_display_name": "钉钉", "title": "视频会议", "body": "10分钟后全员会议开始，请准时参加"}, "classification": {"folder": "Work", "priority": 4}}
{"id": "009", "notification": {"app": "com.chase.sig.android", "app_display_name": "Chase Mobile", "title": "Security Alert", "body": "We detected a login from a new device in London, UK. Was this you?"}, "classification": {"folder": "Alerts", "priority": 5}}
```

## Your Output

Generate **400 unique, realistic notification entries** in JSONL format.

**CRITICAL REQUIREMENTS:**
- At least 30-40% must be from Chinese apps (Feishu, DingTalk, WeChat, Douyin, RedNote)
- Use real Android package names (e.g., com.slack, com.tencent.mm, com.ss.android.lark)
- All Chinese content must be natural and conversational, not translated
- Ensure broad coverage of all folders, apps, languages, and priority levels
- Focus on quality and realism over quantity
