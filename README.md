# H1B Visa Slot Watcher (Live-Only)

A real-time monitor for H1B visa slots across multiple sources with WhatsApp alerts.

## Features
- **Strict H1B Filtering:** Specifically monitors H1B slots, ignoring other visa types.
- **WhatsApp Alerts:** Uses CallMeBot API to send real-time notifications.
- **Change Tracking:** Notifies you of both "Released" (new/updated) and "Consumed" (gone) slots.
- **Multi-Source:** Scrapes `visaslots.info`, `usvisaslots.app`, and `checkvisaslots.com`.

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Update `PHONE_NUMBER` and `CALLMEBOT_APIKEY` in `monitor.py`.
4. Run the watcher:
   ```bash
   python monitor.py
   ```

## Sources
- [visaslots.info](https://visaslots.info)
- [usvisaslots.app](https://www.usvisaslots.app)
- [checkvisaslots.com](https://checkvisaslots.com)
