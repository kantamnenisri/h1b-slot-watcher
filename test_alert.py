import requests
import json
from datetime import datetime
from urllib.parse import quote

# ─── CONFIG ────────────────────────────────────────────────
PHONE_NUMBER = "+13058143780"
CALLMEBOT_APIKEY = "5042020"

# ─── MOCKED STATE FOR TESTING ──────────────────────────────
# Simulating that we had "HYDERABAD-H-1B" and "CHENNAI-H-1B"
# But now "CHENNAI-H-1B" is gone (consumed).
last_released = "[visaslots] NEW DELHI-H-1B -> 15-Oct-2024"
last_consumed = "[visaslots] CHENNAI-H-1B (Gone)"

mock_live_data = [
    {"location": "HYDERABAD", "earliest": "12-Sep-2024"},
    {"location": "NEW DELHI", "earliest": "15-Oct-2024"},
    {"location": "MUMBAI", "earliest": "No Slots"}
]

def send_whatsapp(message: str):
    encoded = quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded}&apikey={CALLMEBOT_APIKEY}"
    try:
        r = requests.get(url, timeout=10)
        print(f"[Test WhatsApp] Status: {r.status_code} | {r.text[:80]}")
    except Exception as e:
        print(f"[Test WhatsApp Error] {e}")

def build_test_message() -> str:
    now = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    lines = [f"🧪 TEST: H1B SLOT ALERT [visaslots.info]", f"🕐 {now}", "─────────────────"]
    
    lines.append("📊 LATEST LIVE DATA:")
    for s in mock_live_data:
        lines.append(f"📍 {s.get('location')} | {s.get('earliest')}")
            
    lines.append("─────────────────")
    lines.append(f"🆕 LAST RELEASED: \n   {last_released}")
    lines.append(f"❌ LAST CONSUMED: \n   {last_consumed}")
    lines.append("─────────────────")
    lines.append("🔗 Check: visaslots.info")
    return "\n".join(lines)

if __name__ == "__main__":
    print("Sending test alert with mock consumed data...")
    msg = build_test_message()
    send_whatsapp(msg)
    print("Done! Check WhatsApp.")
