import json
import os
import re
import requests

BOT_API = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_API or not CHAT_ID:
    raise RuntimeError("Telegram env variables missing")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}

def extract_initial_state(html):
    match = re.search(r'__INITIAL_STATE__\s*=\s*({.*?});', html, re.S)
    if not match:
        return None
    return json.loads(match.group(1))

def check_inditex_page(url, sizes_to_check):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    state = extract_initial_state(r.text)
    if not state:
        return None

    products = json.dumps(state)

    for size in sizes_to_check:
        if size in products and "inStock\":true" in products:
            return size

    return None

# ---------------- MAIN ----------------

with open("config.json") as f:
    config = json.load(f)

print("🟢 Stok kontrolü başladı")

for item in config["urls"]:
    store = item["store"].upper()
    url = item["url"]

    print(f"🔎 {store} sayfası taranıyor")

    try:
        size = check_inditex_page(url, config["sizes_to_check"])

        if size:
            msg = f"🛍️ {store} | {size} BEDEN STOKTA!\n{url}"
            print("✅ STOK VAR")
            send_telegram(msg)
        else:
            print("⛔ Stok yok")

    except Exception as e:
        print(f"⚠️ Hata: {e}")
