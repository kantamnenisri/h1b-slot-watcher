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

# ─── STATE ─────────────────────────────────────────────────
previous_state = {}
last_released_global = "None yet"
last_consumed_global = "None yet"

# ─── CALLMEBOT WHATSAPP ─────────────────────────────────────
def send_whatsapp(message: str):
    encoded = quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded}&apikey={CALLMEBOT_APIKEY}"
    try:
        r = requests.get(url, timeout=10)
        print(f"[WhatsApp] Status: {r.status_code}")
    except Exception as e:
        print(f"[WhatsApp Error] {e}")

# ─── SCRAPING LOGIC (STRICT H1B) ───────────────────────────
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
                results.append({"id": f"{cols[1]}-H1B", "earliest": cols[3], "city": cols[1]})
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

def build_message(slots, source):
    now = datetime.now().strftime("%H:%M:%S")
    lines = [f"🔔 H1B ALERT [{source}]", f"🕐 {now}", "───"]
    if not slots: lines.append("⚠️ NO SLOTS.")
    else:
        for s in slots[:5]: lines.append(f"📍 {s.get('id')} | {s.get('earliest')}")
    lines.extend(["───", f"🟢 {last_released_global}", f"🔴 {last_consumed_global}"])
    return "\n".join(lines)

# ─── BACKGROUND MONITOR TASK ───────────────────────────────
def monitor_task():
    print("🚀 Background Monitor Started...")
    while True:
        for data, key in [(fetch_visaslots_info(), "visaslots"), 
                          (fetch_usvisaslots_app(), "usvisaslots"), 
                          (fetch_checkvisaslots(), "checkvisaslots")]:
            if process_updates(data, key):
                send_whatsapp(build_message(data, key))
        time.sleep(CHECK_INTERVAL)

# ─── STARTUP ───────────────────────────────────────────────
if __name__ == "__main__":
    # Run the monitor in a separate thread
    threading.Thread(target=monitor_task, daemon=True).start()
    # Start Flask on the port Render provides
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
