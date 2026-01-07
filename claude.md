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
- `app`: Package name or lowercase app identifier (e.g., "slack", "gmail", "wechat")
- `app_display_name`: User-facing app name (e.g., "Slack", "Gmail", "WeChat")
- `title`: Short notification title (0-100 chars)
- `body`: Notification body text (0-500 chars)
- `folder`: Must be exactly one of: `Work`, `Personal`, `Promotions`, `Alerts`
- `priority`: Integer 1-5 where 1=ignore, 2=low, 3=normal, 4=important, 5=urgent

## Folder Definitions

### Work
Professional messages from work apps like Slack, Jira, Teams, work email, GitHub, Linear, etc.

**Examples:**
- Slack messages from work channels
- Jira issue updates
- Work email notifications
- GitHub PR reviews
- Calendar reminders for meetings

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

2. **Apps**: Cover wide range of common apps
   - Work: Slack, Teams, Gmail, Outlook, Jira, GitHub, Linear, Notion
   - Personal: WhatsApp, WeChat, Telegram, iMessage, Facebook Messenger
   - Promotions: Amazon, Shopee, Lazada, Target, Walmart, newsletters
   - Alerts: Chase Bank, UPS, FedEx, Uber, DoorDash, system apps

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
{"id": "001", "notification": {"app": "slack", "app_display_name": "Slack", "title": "#incidents", "body": "PROD DOWN - payments service returning 500s"}, "classification": {"folder": "Work", "priority": 5}}
{"id": "002", "notification": {"app": "wechat", "app_display_name": "WeChat", "title": "妈妈", "body": "到家了吗？外面冷记得穿外套"}, "classification": {"folder": "Personal", "priority": 3}}
{"id": "003", "notification": {"app": "amazon", "app_display_name": "Amazon", "title": "Your order has shipped!", "body": "Good news! Your package will arrive tomorrow by 8pm. Track: TBA123456789"}, "classification": {"folder": "Alerts", "priority": 3}}
{"id": "004", "notification": {"app": "target", "app_display_name": "Target", "title": "🎯 50% OFF Everything!", "body": "Flash sale ends tonight! Use code SAVE50 at checkout. Shop now →"}, "classification": {"folder": "Promotions", "priority": 2}}
{"id": "005", "notification": {"app": "gmail", "app_display_name": "Gmail", "title": "Sarah Chen", "body": "Can you review the Q1 deck before the board meeting tomorrow?"}, "classification": {"folder": "Work", "priority": 4}}
{"id": "006", "notification": {"app": "chase", "app_display_name": "Chase Mobile", "title": "Security Alert", "body": "We detected a login from a new device in London, UK. Was this you?"}, "classification": {"folder": "Alerts", "priority": 5}}
```

## Your Output

Generate **100 unique, realistic notification entries** in JSONL format. Ensure broad coverage of all folders, apps, languages, and priority levels. Focus on quality and realism over quantity.
