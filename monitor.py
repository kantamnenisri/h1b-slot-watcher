import requests
import time
import json
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup

# ─── CONFIG ────────────────────────────────────────────────
PHONE_NUMBER = "+13058143780"   # Your WhatsApp number
CALLMEBOT_APIKEY = "5042020"      # Your CallMeBot API key
CHECK_INTERVAL = 60              # seconds between checks
# TARGET_CONSULATES = ["HYDERABAD", "CHENNAI", "NEW DELHI", "MUMBAI"] # Optional filter

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
        print(f"[WhatsApp] Status: {r.status_code} | {r.text[:80]}")
    except Exception as e:
        print(f"[WhatsApp Error] {e}")

# ─── SOURCE 1: visaslots.info ───────────────────────────────
def fetch_visaslots_info():
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://visaslots.info", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                # STRICT H-1B FILTER
                if len(cols) >= 5 and "H-1B" == cols[1]:
                    location, visa, updated, earliest, slots = cols[0], cols[1], cols[2], cols[3], cols[4]
                    results.append({
                        "id": f"{location}-H1B",
                        "source": "visaslots.info",
                        "location": location,
                        "visa": visa,
                        "earliest": earliest,
                        "slots": slots,
                        "updated": updated
                    })
    except Exception as e:
        print(f"[visaslots.info Error] {e}")
    return results

# ─── SOURCE 2: usvisaslots.app ──────────────────────────────
def fetch_usvisaslots_app():
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://www.usvisaslots.app", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                # STRICT H1B FILTER (Checking typical visa type column)
                if len(cols) >= 4 and any("H1B" in str(col).upper() for col in cols[1:3]):
                    country = cols[0] if len(cols) > 0 else ""
                    city = cols[1] if len(cols) > 1 else ""
                    visa = "H1B"
                    earliest = cols[3] if len(cols) > 3 else ""
                    results.append({
                        "id": f"{city}-H1B",
                        "source": "usvisaslots.app",
                        "country": country,
                        "city": city,
                        "visa": visa,
                        "earliest": earliest,
                    })
    except Exception as e:
        print(f"[usvisaslots.app Error] {e}")
    return results

# ─── SOURCE 3: checkvisaslots.com ──────────────────────────
def fetch_checkvisaslots():
    results = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://checkvisaslots.com/latest-us-visa-availability.html",
                         headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                # STRICT H-1B FILTER
                if len(cols) >= 3 and "H-1B" in cols[1]:
                    location = cols[0]
                    results.append({
                        "id": f"{location}-H1B",
                        "source": "checkvisaslots.com",
                        "data": " | ".join(cols),
                        "earliest": cols[2] if len(cols) > 2 else ""
                    })
    except Exception as e:
        print(f"[checkvisaslots.com Error] {e}")
    return results

# ─── CHANGE DETECTOR ────────────────────────────────────────
def process_updates(current_data: list, source_key: str):
    global previous_state, last_released_global, last_consumed_global
    
    current_dict = {item['id']: item for item in current_data}
    prev_dict = previous_state.get(source_key, {})
    
    changes_detected = False
    
    if source_key not in previous_state:
        previous_state[source_key] = current_dict
        return False # Initial load

    # Check for released or updated slots
    for item_id, item in current_dict.items():
        if item_id not in prev_dict:
            last_released_global = f"🆕 RELEASED: {item_id} -> {item.get('earliest', 'Available')}"
            changes_detected = True
        else:
            prev_item = prev_dict[item_id]
            if item.get('earliest') != prev_item.get('earliest'):
                last_released_global = f"🔄 UPDATED: {item_id} -> {item.get('earliest')}"
                changes_detected = True
    
    # Check for consumed slots
    for item_id, item in prev_dict.items():
        if item_id not in current_dict:
            last_consumed_global = f"❌ CONSUMED: {item_id}"
            changes_detected = True

    if changes_detected:
        previous_state[source_key] = current_dict
        return True
    
    return False

# ─── BUILD ALERT MESSAGE ────────────────────────────────────
def build_message(slots_info: list, source: str) -> str:
    now = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    lines = [f"🔔 H1B ONLY ALERT [{source}]", f"🕐 {now}", "─────────────────"]
    
    lines.append("📊 LATEST LIVE H1B DATA:")
    if not slots_info:
        lines.append("   ⚠️ NO H1B SLOTS AVAILABLE.")
    else:
        for s in slots_info[:5]:
            if source == "visaslots.info":
                lines.append(f"📍 {s.get('location')} | {s.get('earliest')}")
            elif source == "usvisaslots.app":
                lines.append(f"📍 {s.get('city')} | {s.get('earliest')}")
            else:
                lines.append(f"📋 {s.get('id')} | {s.get('earliest')}")
            
    lines.append("─────────────────")
    lines.append(f"🟢 LAST H1B RELEASE: \n   {last_released_global}")
    lines.append(f"🔴 LAST H1B CONSUMED: \n   {last_consumed_global}")
    lines.append("─────────────────")
    return "\n".join(lines)

# ─── MAIN LOOP ───────────────────────────────────────────────
def main():
    print("🚀 H1B STRICT Watcher started...")
    send_whatsapp("✅ H1B STRICT Watcher ACTIVE!\nMonitoring only H1B visa slots.")

    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking sources for H1B...")

        sources = [
            (fetch_visaslots_info(), "visaslots.info"),
            (fetch_usvisaslots_app(), "usvisaslots.app"),
            (fetch_checkvisaslots(), "checkvisaslots.com")
        ]

        for data, key in sources:
            if process_updates(data, key):
                print(f"  ✅ H1B Change on {key}")
                send_whatsapp(build_message(data, key))

        print(f"  💤 Sleeping {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
