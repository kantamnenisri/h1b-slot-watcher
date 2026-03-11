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

# Global log for debugging on the dashboard
last_api_status = "No attempts yet"

@app.route('/')
def live_summary():
    now_str = datetime.now().strftime("%d-%b %H:%M:%S")
    
    html = f"""
    <html>
    <head>
        <title>H1B Watcher Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto; background: #f4f7f6; }}
            .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            h1 {{ color: #2c3e50; font-size: 24px; margin-top: 0; }}
            .status-list {{ list-style: none; padding: 0; }}
            .status-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
            .status-item:last-child {{ border-bottom: none; }}
            .label {{ font-weight: bold; color: #34495e; }}
            .value {{ color: #27ae60; font-weight: 500; }}
            .log {{ font-size: 14px; padding: 10px; border-radius: 4px; background: #f8f9fa; border-left: 4px solid #ddd; }}
            .green {{ border-left-color: #27ae60; color: #1e7e34; }}
            .red {{ border-left-color: #e74c3c; color: #c0392b; }}
            .footer {{ font-size: 12px; color: #7f8c8d; text-align: center; margin-top: 20px; }}
            .btn {{ display: inline-block; padding: 8px 12px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; margin-top: 10px; }}
            .api-info {{ font-size: 11px; color: #95a5a6; }}
        </style>
        <meta http-equiv="refresh" content="60">
    </head>
    <body>
        <div class="card">
            <h1>H1B Watcher Dashboard v1.1</h1>
            <p>🕒 <b>Last Check:</b> {now_str}</p>
            <p class="api-info">📡 <b>WhatsApp API Status:</b> {last_api_status}</p>
            
            <h3>📊 Current Status</h3>
            <div class="status-list">
    """
    
    all_found = False
    for src, data_dict in previous_state.items():
        for i_id, item in data_dict.items():
            html += f"""
                <div class="status-item">
                    <span class="label">📍 {i_id}</span>
                    <span class="value">{item.get('earliest')}</span>
                </div>
            """
            all_found = True
    
    if not all_found:
        html += "<p><i>Scanning sources... Data loading in 60s.</i></p><a href='/' class='btn'>Refresh Now</a>"
    
    html += f"""
            </div>
        </div>

        <div class="card log green">
            <b>🟢 Last Release:</b><br>{last_released_global}
        </div>

        <div class="card log red">
            <b>🔴 Last Consumed:</b><br>{last_consumed_global}
        </div>

        <div class="footer">
            Checking sources every 60 seconds. <br>
            Hourly summary at the 20th minute of every hour.
        </div>
    </body>
    </html>
    """
    return html, 200

# ─── CONFIG ────────────────────────────────────────────────
PHONE_NUMBER = "+13058143780"
CALLMEBOT_APIKEY = "5042020"
CHECK_INTERVAL = 60
SUMMARY_MINUTE = 20 

# ─── STATE ─────────────────────────────────────────────────
previous_state = {}
last_released_global = "None yet"
last_consumed_global = "None yet"
last_summary_hour = -1

# ─── CALLMEBOT WHATSAPP ─────────────────────────────────────
def send_whatsapp(message: str):
    global last_api_status
    encoded = quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded}&apikey={CALLMEBOT_APIKEY}"
    try:
        r = requests.get(url, timeout=15)
        last_api_status = f"Status {r.status_code} at {datetime.now().strftime('%H:%M:%S')}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WhatsApp Status: {r.status_code}")
    except Exception as e:
        last_api_status = f"Error: {str(e)[:50]}"
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

def build_message(source, is_summary=False, is_startup=False):
    now_dt = datetime.now()
    now_str = now_dt.strftime("%d-%b %H:%M")
    
    if is_startup:
        header = "🚀 H1B WATCHER STARTED"
    elif is_summary:
        header = "📋 HOURLY H1B SUMMARY"
    else:
        header = f"🔔 H1B ALERT [{source}]"
        
    lines = [f"{header}", f"🕐 {now_str}", "───"]
    
    lines.append("📊 CURRENT STATUS:")
    all_found = False
    for src, data_dict in previous_state.items():
        for i_id, item in data_dict.items():
            lines.append(f"📍 {i_id}: {item.get('earliest')}")
            all_found = True
    
    if not all_found:
        lines.append("⚠️ Scanning sources...")
        
    lines.extend(["───", f"🟢 LAST: {last_released_global}", f"🔴 LAST: {last_consumed_global}"])
    return "\n".join(lines)

# ─── BACKGROUND MONITOR TASK ───────────────────────────────
def monitor_task():
    global last_summary_hour
    print("🚀 H1B Monitor Started...")
    
    while True:
        now = datetime.now()
        
        # 1. PERFORM SCAN
        sources = [
            (fetch_visaslots_info(), "visaslots.info"), 
            (fetch_usvisaslots_app(), "usvisaslots.app"), 
            (fetch_checkvisaslots(), "checkvisaslots.com")
        ]
        
        is_first_scan = not any(previous_state.values())
        
        for data, key in sources:
            if process_updates(data, key):
                send_whatsapp(build_message(key))
        
        # Send initial summary ONLY once it has data
        if is_first_scan and any(previous_state.values()):
            print("Initial scan complete. Sending first live status.")
            send_whatsapp(build_message("Global", is_summary=True, is_startup=True))

        # Hourly summary check
        if now.minute == SUMMARY_MINUTE and now.hour != last_summary_hour:
            send_whatsapp(build_message("Global", is_summary=True))
            last_summary_hour = now.hour
                
        time.sleep(CHECK_INTERVAL)

# ─── STARTUP ───────────────────────────────────────────────
if __name__ == "__main__":
    threading.Thread(target=monitor_task, daemon=True).start()
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
