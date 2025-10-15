# 🧠 Telegram Automation & Safety Tool

A **safe, async Telegram automation utility** built with [Telethon](https://github.com/LonamiWebs/Telethon), designed for **username validation**, **group member extraction**, and **controlled message sending**  with built-in **anti-spam safety, rate limiting, and randomized delays**.

---

## ⚙️ Features

✅ **Username Existence Checker**  
Checks whether Telegram usernames exist or are available, saving results as structured JSON.

✅ **Group Member Scraper (Safe Mode)**  
Extracts member usernames from a public group while applying strict rate limits and randomized delays.

✅ **Message Sender (High-Risk Mode)**  
Sends personalized messages to multiple usernames with automated pacing, sleep timers, and flood-wait handling.

✅ **Anti-Spam & Rate-Limiting**  
Built-in request throttling, safety thresholds, and adaptive random delays.

✅ **Progress Saving**  
Automatically saves progress every few iterations to protect against session interruption.

---

## 🚀 Installation

### 1. Clone or Download
```bash
git clone https://github.com/yourusername/telegram-tool.git
cd telegram-tool
```
### 2. Install Requirements
```bash
pip install telethon asyncio
```

### 🔐 Setup

You need your own Telegram API credentials from
👉 https://my.telegram.org/apps

```python
API_ID = 27324963  # Your API ID
API_HASH = "66c04e636453218haifx6d876e010c64"  # Your API hash
```
## 💡 Usage
### 🔎 Check Usernames

Check if Telegram usernames exist and save results in a JSON file.
```bash
python3 telegram_tool.py check --usernames usernames.txt --output results.json
```
### Example usernames.txt
```ngix
elonmusk
john_doe
nonexistentuser12345
```
### Output: results.json
```json
[
  {"username": "elonmusk", "status": "exists", "owner": "Elon Musk"},
  {"username": "nonexistentuser12345", "status": "not_found"}
]
```
### 👥 Get Group Members

Extract usernames from a public group (use responsibly).
```bash
python3 telegram_tool.py get-members --group yourgroupname --output members.txt
```
### Output Example:
```nginx
username1
username2
username3
```
## 💬 Send Messages (⚠️ Use Cautiously)

Send custom messages to a list of usernames.
This is high risk and may trigger Telegram anti-spam filters.
```bash
python3 telegram_tool.py send --usernames users.txt --message "Hello from TelegramTool!"
```
## ⚠️ Safety Recommendations

- 🧩 Default rate limit: 1 concurrent request

- 🕒 Delays: 3–8 seconds random delay

- 📦 Hourly limit: 100 requests

- 💌 Daily limit: 50 messages

Modify carefully:
```python
CONCURRENCY_LIMIT = 1
MIN_DELAY = 3.0
MAX_DELAY = 8.0
MAX_REQUESTS_PER_HOUR = 100
MAX_MESSAGES_PER_DAY = 50
```
⚠️ Increasing these values significantly raises your risk of temporary or permanent Telegram account restrictions.

---

## 📁 Example Directory Structure
```pgsql
telegram_tool/
├── telegram_tool.py
├── usernames.txt
├── results.json
└── members.txt
```
## 🧩 Error Handling
| Error Type                 | Meaning                 | Action                 |
| -------------------------- | ----------------------- | ---------------------- |
| `UsernameNotOccupiedError` | Username doesn’t exist  | Logged as “not_found”  |
| `UsernameInvalidError`     | Invalid format          | Skipped                |
| `FloodWaitError`           | Telegram rate limit hit | Waits automatically    |
| `PeerIdInvalidError`       | Privacy blocked message | Logged as failed       |
| `RPCError`                 | Telegram RPC issue      | Auto retry after delay |

---
### 🧠 Example Workflow

1. Gather usernames → usernames.txt

2. Check validity:
```bash
python3 telegram_tool.py check --usernames usernames.txt
```
3. Collect group members:
```bash
python3 telegram_tool.py get-members --group cybercommunity
```
4. (Optional) Send a safe number of messages:
```bash
python3 telegram_tool.py send --usernames valid_users.txt --message "Hey there 👋"
```
## 🧾 License

This project is released under the MIT License  use responsibly and ethically.
Never use this tool for spam or harassment.

