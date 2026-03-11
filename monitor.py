import requests
import time
import json
import threading
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup
from flask import Flask

# ─── FLASK APP FOR RENDER FREE TIER ────────────────────────
app = Flask(__name__)

@app.route('/')
def health_check():
    return "H1B Watcher is Running!", 200

# ─── CONFIG ────────────────────────────────────────────────
PHONE_NUMBER = "+13058143780"
CALLMEBOT_APIKEY = "5042020"
CHECK_INTERVAL = 60
SUMMARY_MINUTE = 5 # Send summary at the 5th minute of every hour

# ─── STATE ─────────────────────────────────────────────────
previous_state = {}
last_released_global = "None yet"
last_consumed_global = "None yet"
last_summary_hour = -1

# ─── CALLMEBOT WHATSAPP ─────────────────────────────────────
def send_whatsapp(message: str):
    encoded = quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded}&apikey={CALLMEBOT_APIKEY}"
    try:
        r = requests.get(url, timeout=15)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WhatsApp Status: {r.status_code}")
    except Exception as e:
        print(f"[WhatsApp Error] {e}")

# ─── SCRAPING LOGIC ────────────────────────────────────────
def fetch_visaslots_info():
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://visaslots.info", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 5 and "H-1B" == cols[1]:
                results.append({"id": f"{cols[0]}-H1B", "earliest": cols[3], "location": cols[0]})
    except Exception as e: print(f"[Error vslots] {e}")
    return results

def fetch_usvisaslots_app():
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://www.usvisaslots.app", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 4 and any("H1B" in str(col).upper() for col in cols[1:3]):
                city = cols[1] if len(cols) > 1 else "Unknown"
                results.append({"id": f"{city}-H1B", "earliest": cols[3], "city": city})
    except Exception as e: print(f"[Error usvapp] {e}")
    return results

def fetch_checkvisaslots():
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://checkvisaslots.com/latest-us-visa-availability.html", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 3 and "H-1B" in cols[1]:
                results.append({"id": f"{cols[0]}-H1B", "earliest": cols[2]})
    except Exception as e: print(f"[Error checkv] {e}")
    return results

# ─── UPDATES & ALERTS ───────────────────────────────────────
def process_updates(current_data: list, source_key: str):
    global previous_state, last_released_global, last_consumed_global
    current_dict = {item['id']: item for item in current_data}
    prev_dict = previous_state.get(source_key, {})
    changes = False
    
    if source_key not in previous_state:
        previous_state[source_key] = current_dict
        return False

    for i_id, item in current_dict.items():
        if i_id not in prev_dict or item.get('earliest') != prev_dict[i_id].get('earliest'):
            last_released_global = f"🆕 {i_id} -> {item.get('earliest')}"
            changes = True
    
    for i_id in prev_dict:
        if i_id not in current_dict:
            last_consumed_global = f"❌ {i_id} GONE"
            changes = True
            
    if changes: previous_state[source_key] = current_dict
    return changes

def build_message(source, is_summary=False):
    now_dt = datetime.now()
    now_str = now_dt.strftime("%d-%b %H:%M")
    header = "📋 HOURLY H1B SUMMARY" if is_summary else f"🔔 H1B ALERT [{source}]"
    lines = [f"{header}", f"🕐 {now_str}", "───"]
    
    lines.append("📊 CURRENT STATUS:")
    # Collect all current slots from state to show a full summary
    all_found = False
    for src, data_dict in previous_state.items():
        for i_id, item in data_dict.items():
            lines.append(f"📍 {i_id}: {item.get('earliest')}")
            all_found = True
    
    if not all_found:
        lines.append("⚠️ No H1B slots found across sources.")
        
    lines.extend(["───", f"🟢 LAST RELEASE: {last_released_global}", f"🔴 LAST CONSUMED: {last_consumed_global}"])
    return "\n".join(lines)

# ─── BACKGROUND MONITOR TASK ───────────────────────────────
def monitor_task():
    global last_summary_hour
    print("🚀 H1B Monitor with Hourly Summaries Started...")
    
    while True:
        now = datetime.now()
        
        # 1. CHECK FOR HOURLY SUMMARY (at the 5th minute)
        if now.minute == SUMMARY_MINUTE and now.hour != last_summary_hour:
            print(f"Sending hourly summary at {now.strftime('%H:%M:%S')}")
            send_whatsapp(build_message("Global", is_summary=True))
            last_summary_hour = now.hour
            
        # 2. CHECK FOR IMMEDIATE UPDATES
        sources = [
            (fetch_visaslots_info(), "visaslots.info"),
            (fetch_usvisaslots_app(), "usvisaslots.app"),
            (fetch_checkvisaslots(), "checkvisaslots.com")
        ]
        
        for data, key in sources:
            if process_updates(data, key):
                print(f"Immediate update detected on {key}")
                send_whatsapp(build_message(key))
                
        time.sleep(CHECK_INTERVAL)

# ─── STARTUP ───────────────────────────────────────────────
if __name__ == "__main__":
    threading.Thread(target=monitor_task, daemon=True).start()
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
