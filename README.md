# Reyal Telegram

Sends ERPNext Notification Log entries to Telegram via a bot, with per-user settings, global configuration, delivery logging, and clean mobile-friendly message formatting.

---

## Requirements

- Frappe / ERPNext v15
- A Telegram bot token (from BotFather)
- Each user's Telegram chat ID

---

## Setup

### 1. Create a bot with BotFather

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the prompts.
3. Copy the **bot token**; it looks like `123456789:ABCdef...`.

### 2. Get your chat ID

Send any message to your bot, then open this URL in a browser (replace `<TOKEN>`):

```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

Find `"chat": {"id": ...}` in the response; that number is your chat ID.

For group chats, add the bot to the group, send a message mentioning it, then use the same URL. Group chat IDs are negative numbers (e.g. `-1001234567890`).

### 3. Install the app

```bash
cd /path/to/frappe-bench
pip install -e apps/reyal_telegram   # or: bench get-app from git remote
bench --site your.site install-app reyal_telegram
bench --site your.site migrate
```

### 4. Configure Telegram Settings

Go to **Telegram Settings** (single doctype) and set:

| Field | Value |
|---|---|
| Enabled | ✓ |
| Telegram Bot Token | Your BotFather token |
| Default Telegram Chat ID | Optional fallback chat ID |
| Disable Web Page Preview | Optional |
| Notification type toggles | Enable as required |

### 5. Create a Telegram Notification Profile per user

Go to **Telegram Notification Profile** and create one record per user:

| Field | Value |
|---|---|
| User | The Frappe user email |
| Enabled | ✓ |
| Telegram Chat ID | The user's personal chat ID |
| Display Name | Optional override for how the actor appears in messages |

### 6. Send a test message

Open **Telegram Settings**, scroll to the bottom, and use the **Send Test Message** button. Enter any chat ID (your own, or a group) to verify the bot can reach it.

---

## Message format

Messages are delivered as Telegram HTML with clickable document links in the heading. Examples:

- 💬 **Jane Doe** mentioned you in [Sales Order SO-0001](#)
- 📋 **Jane Doe** assigned you to [Task TASK-0001](#)
- 🔔 **Alert Subject**
- 📎 **Jane Doe** shared [Customer ACME Ltd](#) with you

---

## Delivery log

Every attempted send (including skips and failures) is recorded in **Telegram Notification Delivery**. Each record shows the status, formatted message, chat ID used, and any error detail.

---

## Routing rules

A notification is sent only when **all** of the following are true:

1. Telegram Settings is enabled and a bot token is configured.
2. The recipient has a Telegram Notification Profile and it is enabled.
3. A chat ID is available (profile or global default).
4. The notification type is enabled in settings.
5. The Notification Log has not already been marked `custom_telegram_sent`.

---

## Architecture

```
reyal_telegram/
├── hooks.py                          doc_events + custom_fields
├── telegram/doctype/
│   ├── telegram_settings/            Single; global config + test utility
│   ├── telegram_notification_profile/  Per-user Telegram config
│   └── telegram_notification_delivery/ Delivery audit log
└── services/
    ├── dispatcher.py                 Enqueues and orchestrates the send
    ├── formatter.py                  Type detection + Telegram HTML builder
    ├── sender.py                     Telegram Bot API HTTP call (stdlib only)
    └── utils.py                      HTML escape, text cleaning, URL building
```
