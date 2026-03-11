# H1B Visa Slot Watcher (Live-Only)

A real-time monitor for H1B visa slots across multiple sources with WhatsApp alerts.

**Live Status:** [https://h1b-slot-watcher.onrender.com](https://h1b-slot-watcher.onrender.com)

## Features
- **Strict H1B Filtering:** Specifically monitors H1B slots, ignoring other visa types.
- **WhatsApp Alerts:** Uses CallMeBot API to send real-time notifications.
- **Change Tracking:** Notifies you of both "Released" (new/updated) and "Consumed" (gone) slots.
- **Multi-Source:** Scrapes `visaslots.info`, `usvisaslots.app`, and `checkvisaslots.com`.

## 🛠️ Keeping the Free Tier Awake
Render's Free Tier "sleeps" after 15 minutes of inactivity. To keep the watcher running 24/7, you **must** ping the URL every 10-14 minutes.

### Option 1: Cron-job.org (Recommended - 100% Free)
1. Create a free account at [cron-job.org](https://cron-job.org/).
2. Click **"Create Cronjob"**.
3. **Title:** `H1B Watcher Ping`
4. **URL:** `https://h1b-slot-watcher.onrender.com/`
5. **Schedule:** Every 10 minutes.
6. Click **Create**.

### Option 2: UptimeRobot
1. Create a free account at [uptimerobot.com](https://uptimerobot.com/).
2. Add a **New Monitor**.
3. **Monitor Type:** HTTP(s).
4. **URL:** `https://h1b-slot-watcher.onrender.com/`
5. **Monitoring Interval:** 5 or 10 minutes.

## ⚙️ Configuration
To receive alerts on your own phone, you must update the following variables in `monitor.py`:

1.  **PHONE_NUMBER:** Your WhatsApp number with country code (e.g., `+91XXXXXXXXXX`).
2.  **CALLMEBOT_APIKEY:** Your unique API key from CallMeBot.

### How to apply changes:
After editing `monitor.py` locally:
1.  **Commit the changes:** `git commit -am "Update credentials"`
2.  **Push to GitHub:** `git push origin master`
3.  **Render will automatically redeploy** and start using your new number.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `python monitor.py`
