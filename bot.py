import json
import os
import requests

# ================== ENV ==================

# GitHub Actions + local uyumlu
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("DEBUG TOKEN:", TELEGRAM_BOT_TOKEN)
print("DEBUG CHAT_ID:", TELEGRAM_CHAT_ID)

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("Telegram env variables missing")

# ================== TELEGRAM ==================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload, timeout=10)

# ================== INDITEX ==================

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
            return size.get("name")

    return None

# ================== MANGO ==================

def check_mango_stock(product_id, sizes):
    url = f"https://shop.mango.com/ws/products/{product_id}/stock"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    for size in data.get("sizes", []):
        if size.get("label") in sizes and size.get("stock", 0) > 0:
            return size.get("label")

    return None

# ================== MAIN ==================

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

sizes_to_check = config["sizes_to_check"]

print("🟢 Stok kontrolü başladı")

for item in config["urls"]:
    store = item["store"]
    url = item["url"]

    # product_id URL'den otomatik çekiliyor
    try:
        product_id = url.split("p")[1].split(".")[0]
    except Exception:
        print(f"⚠️ product_id alınamadı: {url}")
        continue

    print(f"🔎 {store.upper()} | {product_id}")

    try:
        if store in ["zara", "bershka", "stradivarius"]:
            size = check_inditex_stock(store, product_id, sizes_to_check)
        elif store == "mango":
            size = check_mango_stock(product_id, sizes_to_check)
        else:
            continue

        if size:
            msg = f"🛍️ {store.upper()} | {size} BEDEN STOKTA!\n{url}"
            print("✅ STOK VAR")
            send_telegram(msg)
        else:
            print("⛔ Stok yok")

    except Exception as e:
        print(f"⚠️ Hata: {e}")
