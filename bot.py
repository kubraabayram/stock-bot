import json
import os
import re
import requests

BOT_API = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("DEBUG TOKEN:", "***" if BOT_API else None)
print("DEBUG CHAT_ID:", "***" if CHAT_ID else None)

if not BOT_API or not CHAT_ID:
    raise RuntimeError("Telegram env variables missing")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message},
        timeout=10
    )

# -------------------------------------------------
# PRODUCT ID PARSERS
# -------------------------------------------------

def extract_inditex_product_id(url):
    match = re.search(r"c0p(\d+)", url)
    return match.group(1) if match else None

def extract_zara_product_id(url):
    match = re.search(r"p(\d+)", url)
    return match.group(1) if match else None

# -------------------------------------------------
# STOCK CHECKER
# -------------------------------------------------

def check_inditex_stock(store, product_id, sizes):
    store_ids = {
        "zara": "11701",
        "bershka": "34009455",
        "stradivarius": "34009555"
    }

    store_id = store_ids[store]
    url = f"https://www.{store}.com/itxrest/2/catalog/store/{store_id}/product/{product_id}/stock"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    for size in data.get("sizes", []):
        if size.get("name") in sizes and size.get("availability") == "in_stock":
            return size["name"]

    return None

# -------------------------------------------------
# MAIN
# -------------------------------------------------

with open("config.json") as f:
    config = json.load(f)

sizes_to_check = config["sizes_to_check"]

print("🟢 Stok kontrolü başladı")

for item in config["urls"]:
    store = item["store"]
    url = item["url"]

    if store == "mango":
        print("⏭️ MANGO atlandı")
        continue

    print(f"\n🔎 {store.upper()} sayfası taranıyor")

    if store == "zara":
        product_id = extract_zara_product_id(url)
    else:
        product_id = extract_inditex_product_id(url)

    if not product_id:
        print("⚠️ Product ID bulunamadı")
        continue

    try:
        size = check_inditex_stock(store, product_id, sizes_to_check)

        if size:
            msg = f"🛍️ {store.upper()} | {size} BEDEN STOKTA!\n{url}"
            print("✅ STOK VAR")
            send_telegram(msg)
        else:
            print("⛔ Stok yok")

    except Exception as e:
        print(f"⚠️ Hata: {e}")
