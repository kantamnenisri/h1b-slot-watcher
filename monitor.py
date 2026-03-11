import requests
import time
import json
import threading
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup
from flask import Flask, request, redirect

# ─── FLASK APP FOR RENDER FREE TIER ────────────────────────
app = Flask(__name__)

# Global logs for debugging on the dashboard
last_api_status = "No attempts yet"
current_activity = "Initializing..."

@app.route('/')
def live_summary():
    now_str = datetime.now().strftime("%d-%b %H:%M:%S")
    
    html = f"""
    <html>
    <head>
        <title>H1B Watcher Dashboard v1.2</title>
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
            .btn {{ display: inline-block; padding: 10px 15px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; margin: 5px 0; border: none; cursor: pointer; }}
            .btn-test {{ background: #9b59b6; }}
            .api-info {{ font-size: 11px; color: #95a5a6; }}
            .activity {{ font-size: 13px; color: #e67e22; font-weight: bold; }}
        </style>
        <meta http-equiv="refresh" content="30">
    </head>
    <body>
        <div class="card">
            <h1>H1B Watcher Dashboard v1.2</h1>
            <p>🕒 <b>Last Check:</b> {now_str}</p>
            <p class="activity">🏃 <b>Current Activity:</b> {current_activity}</p>
            <p class="api-info">📡 <b>WhatsApp API Status:</b> {last_api_status}</p>
            
            <a href="/test-whatsapp" class="btn btn-test">Send Test WhatsApp Now</a>
            <a href="/" class="btn">Refresh Dashboard</a>

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
        html += "<p><i>Waiting for first successful scan...</i></p>"
    
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
            Hourly summary at the 45th minute of every hour.
        </div>
    </body>
    </html>
    """
    return html, 200

@app.route('/test-whatsapp')
def test_whatsapp_route():
    send_whatsapp("🧪 Manual Test: Your H1B Watcher is connected!")
    return redirect("/")

# ─── CONFIG ────────────────────────────────────────────────
PHONE_NUMBER = "+13058143780"
CALLMEBOT_APIKEY = "5042020"
CHECK_INTERVAL = 60
SUMMARY_MINUTE = 45 # Changed from 20 to 45 per user request

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
        r = requests.get(url, timeout=10)
        last_api_status = f"Status {r.status_code} at {datetime.now().strftime('%H:%M:%S')}"
    except Exception as e:
        last_api_status = f"Error: {str(e)[:50]}"

# ─── SCRAPING LOGIC (WITH BETTER TIMEOUTS) ──────────────────
def fetch_visaslots_info():
    global current_activity
    current_activity = "Checking visaslots.info..."
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://visaslots.info", headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 5 and "H-1B" == cols[1]:
                results.append({"id": f"{cols[0]}-H1B", "earliest": cols[3]})
    except Exception as e: print(f"[Error vslots] {e}")
    return results

def fetch_usvisaslots_app():
    global current_activity
    current_activity = "Checking usvisaslots.app..."
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://www.usvisaslots.app", headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 4 and any("H1B" in str(col).upper() for col in cols[1:3]):
                results.append({"id": f"{cols[1]}-H1B", "earliest": cols[3]})
    except Exception as e: print(f"[Error usvapp] {e}")
    return results

def fetch_checkvisaslots():
    global current_activity
    current_activity = "Checking checkvisaslots.com..."
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://checkvisaslots.com/latest-us-visa-availability.html", headers=headers, timeout=8)
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
    header = "📋 HOURLY H1B SUMMARY" if is_summary else f"🔔 H1B ALERT [{source}]"
    if is_startup: header = "🚀 H1B WATCHER RESTARTED"
    
    lines = [f"{header}", f"🕐 {datetime.now().strftime('%d-%b %H:%M')}", "───", "📊 CURRENT STATUS:"]
    all_found = False
    for src, data_dict in previous_state.items():
        for i_id, item in data_dict.items():
            lines.append(f"📍 {i_id}: {item.get('earliest')}")
            all_found = True
    if not all_found: lines.append("⚠️ Scanning sources...")
    lines.extend(["───", f"🟢 LAST: {last_released_global}", f"🔴 LAST: {last_consumed_global}"])
    return "\n".join(lines)

# ─── BACKGROUND MONITOR TASK ───────────────────────────────
def monitor_task():
    global last_summary_hour, current_activity
    while True:
        now = datetime.now()
        
        # Hourly summary check
        if now.minute == SUMMARY_MINUTE and now.hour != last_summary_hour:
            send_whatsapp(build_message("Global", is_summary=True))
            last_summary_hour = now.hour
            
        # Perform scan with shorter timeouts
        sources = [
            (fetch_visaslots_info(), "visaslots.info"), 
            (fetch_usvisaslots_app(), "usvisaslots.app"), 
            (fetch_checkvisaslots(), "checkvisaslots.com")
        ]
        
        is_first_scan = not any(previous_state.values())
        for data, key in sources:
            if process_updates(data, key):
                send_whatsapp(build_message(key))
        
        if is_first_scan and any(previous_state.values()):
            send_whatsapp(build_message("Global", is_summary=True, is_startup=True))

        current_activity = "Sleeping (Next scan in 60s)..."
        time.sleep(CHECK_INTERVAL)

# ─── STARTUP ───────────────────────────────────────────────
if __name__ == "__main__":
    threading.Thread(target=monitor_task, daemon=True).start()
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
