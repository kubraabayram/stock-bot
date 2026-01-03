import json
import os
import requests
from inditex_helpers import extract_product_ids_from_page, check_inditex_stock

BOT_API = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("DEBUG TOKEN:", "***" if BOT_API else None)
print("DEBUG CHAT_ID:", "***" if CHAT_ID else None)

TELEGRAM_ENABLED = True
if not BOT_API or not CHAT_ID:
    print("⚠️ Telegram env variables missing")
    TELEGRAM_ENABLED = False

def send_telegram(msg):
    if not TELEGRAM_ENABLED:
        return
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)

# ---------------- MAIN ----------------

with open("config.json") as f:
    config = json.load(f)

sizes = config["sizes_to_check"]

print("🟢 Stok kontrolü başladı")

for item in config["urls"]:
    store = item["store"]
    url = item["url"]

    print(f"\n🔎 {store.upper()} sayfası taranıyor")

    try:
        product_ids = extract_product_ids_from_page(url)

        if not product_ids:
            print("⚠️ Product ID bulunamadı")
            continue

        for pid in product_ids:
            size = check_inditex_stock(store, pid, sizes)
            if size:
                msg = f"🛍️ {store.upper()} | {size} BEDEN STOKTA!\n{url}"
                print("✅ STOK VAR:", pid)
                send_telegram(msg)
                break
        else:
            print("⛔ Stok yok")

    except Exception as e:
        print("⚠️ Hata:", e)
