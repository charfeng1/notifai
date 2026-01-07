# Notifai - Smart Notification Filter

## Product Requirements Document

**Version:** 1.0
**Date:** January 7, 2025
**Timeline:** 2 days
**Platform:** Android (Pixel 7 Pro target device)

---

## Overview

Notifai is an on-device AI-powered notification organizer that observes all incoming notifications, classifies them using a local 0.5B language model, and presents users with a structured, folder-based view of their notification history.

The app operates as a **relay, not an interceptor** - users receive their normal notifications unchanged while gaining an intelligent second view that organizes everything automatically.

---

## Problem Statement

Mobile notifications are chaotic. Users receive hundreds daily across work tools (Slack, Jira, Email), personal messaging (WeChat, WhatsApp), promotions, and alerts. The native notification shade offers no organization, prioritization, or filtering. Users either miss important messages in the noise or waste mental energy triaging constantly.

---

## Solution

A passive notification observer that:

1. Captures all notifications at the OS level via NotificationListenerService
2. Classifies each using an on-device LLM (Qwen 0.5B)
3. Stores structured metadata in local database
4. Presents an organized folder-based UI
5. Allows user customization of folders and classification behavior

---

## Target User

Contest demo: Developer/power user with 5+ messaging apps who wants notification sanity without changing existing habits.

---

## Core Features

### 1. Notification Observation (P0)

**What:** Background service that receives copies of all notifications.

**Behavior:**
- Runs as foreground service with persistent notification ("Notifai active")
- Does NOT dismiss or modify original notifications
- Captures: package name, app name, title, body, timestamp, icons
- Triggers classification pipeline on each received notification

**Technical:** Android NotificationListenerService

### 2. On-Device AI Classification (P0)

**What:** Local LLM classifies each notification into a folder with priority score.

**Model:** Qwen3-0.5B (Q4 quantized) via llama.cpp

**Input format:**
```
<system>
You classify notifications into folders.

Folders:
[Work]: Professional messages from work apps like Slack, Jira, Teams, work email
[Personal]: Messages from friends and family
[Promotions]: Marketing, deals, spam, promotional content
[Alerts]: Banking, security, system notifications, delivery updates

{user_custom_instructions}

Output JSON: {"folder": "...", "priority": 1-5}
</system>

<user>
App: {app_name}
Title: {title}
Body: {body}
</user>
```

**Output:**
```json
{"folder": "Personal", "priority": 4}
```

**Performance target:** <1 second per classification on Pixel 7 Pro CPU

### 3. Structured Folder View (P0)

**What:** Main UI showing notifications organized by AI-assigned folders.

**Layout:**
```
┌─────────────────────────────┐
│ Notifai                  ⚙️│
├─────────────────────────────┤
│ 📁 Work (12)              → │
│ 📁 Personal (5)           → │
│ 📁 Promotions (23)        → │
│ 📁 Alerts (2)             → │
├─────────────────────────────┤
│ Recent                      │
│ ┌─────────────────────────┐ │
│ │ 👤 Mom (WeChat)         │ │
│ │ 到家了吗                 │ │
│ │ 2 min ago → Personal    │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

**Interactions:**
- Tap folder → expand to show notifications in that folder
- Tap notification → deep link to source app
- Pull to refresh (re-fetch from DB)

### 4. Custom Folders (P2)

**What:** Users create their own folders with natural language descriptions.

**UI Flow:**
1. Settings → Folders → Add Folder
2. Enter folder name: "Urgent Family"
3. Enter description: "Messages from parents about health or emergencies"
4. Save

**Behavior:**
- Custom folders appear in classification prompt
- Model uses description to route notifications
- Users can edit/delete custom folders
- Default folders (Work, Personal, Promotions, Alerts) can be edited but not deleted

**Data model:**
```kotlin
data class Folder(
    val id: String,
    val name: String,
    val description: String,
    val isDefault: Boolean,
    val sortOrder: Int
)
```

### 5. App Selection (P0)

**What:** Users choose which apps to process through AI classification.

**Why:**
- Saves battery/CPU - skip classification for irrelevant apps
- Reduces noise - user doesn't want games or system apps cluttering folders
- Privacy - user may not want certain app notifications logged

**UI:** Settings → Monitored Apps → Toggle list of installed apps

**Layout:**
```
┌─────────────────────────────────┐
│ Monitored Apps                  │
├─────────────────────────────────┤
│ ☑️ Slack                        │
│ ☑️ WeChat                       │
│ ☑️ Gmail                        │
│ ☑️ Jira                         │
│ ☐ Candy Crush                   │
│ ☐ YouTube                       │
│ ☐ Settings                      │
├─────────────────────────────────┤
│ 4 apps monitored                │
└─────────────────────────────────┘
```

**Behavior:**
- Default: All apps OFF (user opts in)
- Or: Smart defaults ON for common productivity/messaging apps
- Notifications from unmonitored apps are ignored entirely (not stored, not classified)
- Quick actions: "Select All" / "Deselect All" / "Select Messaging Apps"

**Data model:**
```kotlin
@Entity(tableName = "monitored_apps")
data class MonitoredAppEntity(
    @PrimaryKey val packageName: String,
    val appName: String,
    val isEnabled: Boolean
)
```

**Service logic:**
```kotlin
override fun onNotificationPosted(sbn: StatusBarNotification) {
    val pkg = sbn.packageName
    if (!appRepository.isMonitored(pkg)) return  // Skip entirely

    // Proceed with classification...
}
```

---

### 6. Personal Instructions (P2)

**What:** Free-text field for users to customize classification behavior.

**UI:** Settings → Personal Instructions → Text field (280 char limit)

**Example input:**
```
I'm a developer. #incidents channels are always urgent.
淘宝 promotions are never important. Chinese messages from
family contacts are high priority.
```

**Behavior:**
- Appended to system prompt as `{user_custom_instructions}`
- Applied to all future classifications
- Does not retroactively reclassify existing notifications

---

## Non-Goals (Out of Scope)

- Notification dismissal/interception
- Cross-device sync
- Cloud backup
- Notification reply from within app
- Scheduled digests
- Widgets
- Wear OS support
- Per-app rules UI
- Nested folders
- Notification grouping/summarization

---

## Technical Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Android OS                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           Notification Shade                        │ │
│  │  (User sees normal notifications unchanged)         │ │
│  └─────────────────────────────────────────────────────┘ │
│                         │                                │
│                         ▼ (copy)                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │        NotificationListenerService                  │ │
│  │  - Receives notification posted/removed events      │ │
│  │  - Extracts: pkg, title, body, timestamp            │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                   Notifai App                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Classification Pipeline                │ │
│  │  1. Build prompt (folders + user instructions)      │ │
│  │  2. Run inference (llama.cpp + Qwen 0.5B Q4)       │ │
│  │  3. Parse JSON output                               │ │
│  │  4. Store in Room DB                                │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                  Room Database                      │ │
│  │  - notifications (id, app, title, body, folder...)  │ │
│  │  - folders (id, name, description, isDefault)       │ │
│  │  - settings (personal_instructions)                 │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                Jetpack Compose UI                   │ │
│  │  - Folder list view                                 │ │
│  │  - Notification list per folder                     │ │
│  │  - Settings (folders, instructions)                 │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Data Models

### Notification
```kotlin
@Entity(tableName = "notifications")
data class NotificationEntity(
    @PrimaryKey val id: String,
    val packageName: String,
    val appName: String,
    val title: String,
    val body: String,
    val timestamp: Long,
    val folder: String,
    val priority: Int,
    val isRead: Boolean = false
)
```

### Folder
```kotlin
@Entity(tableName = "folders")
data class FolderEntity(
    @PrimaryKey val id: String,
    val name: String,
    val description: String,
    val isDefault: Boolean,
    val sortOrder: Int
)
```

### Settings
```kotlin
@Entity(tableName = "settings")
data class SettingsEntity(
    @PrimaryKey val key: String,
    val value: String
)
// Keys: "personal_instructions"
```

---

## Default Folders

| Name | Description | Default |
|------|-------------|---------|
| Work | Professional messages from work apps like Slack, Jira, Teams, work email | ✓ |
| Personal | Messages from friends and family, personal conversations | ✓ |
| Promotions | Marketing, deals, spam, promotional content from shopping and service apps | ✓ |
| Alerts | Banking, security, system notifications, delivery updates, transactional messages | ✓ |

---

## Permissions Required

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
<uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />

<service
    android:name=".NotificationListener"
    android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE"
    android:exported="true">
    <intent-filter>
        <action android:name="android.service.notification.NotificationListenerService" />
    </intent-filter>
</service>
```

---

## User Flows

### First Launch
1. Open app → Onboarding screen explaining what app does
2. "Grant notification access" button → Opens Android Settings
3. User toggles Notifai in Notification Access list
4. Return to app → "Select apps to monitor" screen
5. User toggles on Slack, WeChat, Gmail, etc.
6. "Done" → Main screen (empty, waiting for notifications)

### Selecting Apps
1. Settings → Monitored Apps
2. See list of all installed apps with toggles
3. Toggle on apps to monitor, toggle off to ignore
4. Changes apply immediately to new notifications

### Viewing Notifications
1. Open app → See folder list with counts
2. Tap "Personal (5)" → See 5 notifications in Personal folder
3. Tap notification → Opens source app via deep link

### Creating Custom Folder
1. Settings → Folders → "+" button
2. Enter name: "Urgent Family"
3. Enter description: "Messages from parents about health or emergencies"
4. Save → Return to folder list
5. New folder appears, future notifications may route to it

### Setting Personal Instructions
1. Settings → Personal Instructions
2. Enter: "I work at a bank. Compliance messages are always urgent."
3. Save → Applied to future classifications

---

## Success Metrics (Contest Demo)

1. **Works:** Notifications appear in app within 1 second of arrival
2. **Accurate:** >80% of notifications classified into sensible folder (subjective)
3. **Fast:** Classification completes in <1 second
4. **Stable:** No crashes during 10-minute demo
5. **Impressive:** Judge understands value prop within 30 seconds

---

## 2-Day Development Schedule

### Day 1 (8-10 hours)

| Time | Task |
|------|------|
| 2h | Project setup, dependencies, llama.cpp Android build |
| 2h | NotificationListenerService implementation |
| 1.5h | Room database + data models (notifications, folders, monitored apps) |
| 1.5h | App selection UI (list installed apps, toggle monitoring) |
| 2h | LLM inference pipeline (prompt building, inference, parsing) |
| 1h | Basic UI: folder list + notification list (minimal styling) |

**End of Day 1:** Notifications captured from selected apps, classified, stored, displayed in ugly but functional UI.

### Day 2 (8-10 hours)

| Time | Task |
|------|------|
| 2h | Custom folders CRUD UI |
| 1h | Personal instructions UI |
| 2h | UI polish (Compose styling, icons, animations) |
| 1h | Deep linking to source apps |
| 1h | Foreground service notification + battery optimization handling |
| 1h | Testing, bug fixes |
| 1h | Demo prep, screenshots |

**End of Day 2:** Polished, demo-ready app.

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| llama.cpp Android build issues | Medium | Start here; use pre-built binaries if available |
| Model too slow on CPU | Low | Pixel 7 Pro is fast; Q4 0.5B should be fine |
| Classification accuracy poor | Medium | Tune prompt; fallback to "Uncategorized" folder |
| Battery drain | Low | Foreground service is standard pattern |
| NotificationListenerService killed | Medium | Battery optimization exemption + proper foreground service |

---

## Future Enhancements (Post-Contest)

- Notification summarization ("You missed 12 work messages: 3 about Project X...")
- Smart notification muting (learn what user ignores)
- Widgets showing folder counts
- Scheduled digest notifications
- Export/backup
- Fine-tuned model trained on user's own classification corrections

---

## Appendix: Sample Prompts

### Basic Classification
```
<system>
You classify notifications into folders.

Folders:
[Work]: Professional messages from work apps like Slack, Jira, Teams, work email
[Personal]: Messages from friends and family
[Promotions]: Marketing, deals, spam, promotional content
[Alerts]: Banking, security, system notifications, delivery updates

Output JSON only: {"folder": "...", "priority": 1-5}
Priority: 1=ignore, 2=low, 3=normal, 4=important, 5=urgent
</system>

<user>
App: Slack
Title: #incidents
Body: PROD DOWN - payments service returning 500s
</user>
```

**Expected output:**
```json
{"folder": "Work", "priority": 5}
```

### With Custom Folder + Instructions
```
<system>
You classify notifications into folders.

Folders:
[Work]: Professional messages from work apps like Slack, Jira, Teams, work email
[Personal]: Messages from friends and family
[Urgent Family]: Messages from parents about health or emergencies
[Promotions]: Marketing, deals, spam, promotional content
[Alerts]: Banking, security, system notifications, delivery updates

User preferences:
Chinese messages from family are usually important. Mom and Dad (妈/爸) are highest priority.

Output JSON only: {"folder": "...", "priority": 1-5}
</system>

<user>
App: WeChat
Title: 妈妈
Body: 爸爸住院了快回电话
</user>
```

**Expected output:**
```json
{"folder": "Urgent Family", "priority": 5}
```
