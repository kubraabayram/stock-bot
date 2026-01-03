import json
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_API = os.getenv("BOT_API")
CHAT_ID = os.getenv("CHAT_ID")

print("DEBUG TOKEN:", "***" if BOT_API else None)
print("DEBUG CHAT_ID:", "***" if CHAT_ID else None)

if not BOT_API or not CHAT_ID:
    raise RuntimeError("Telegram env variables missing")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

# -------------------------------------------------
# PRODUCT ID PARSERS
# -------------------------------------------------

def extract_inditex_product_id(url):
    """
    Zara / Bershka / Stradivarius
    c0p455810677.html  -> 455810677
    """
    match = re.search(r"c0p(\d+)", url)
    return match.group(1) if match else None

def extract_mango_product_id(url):
    """
    tokali-chelsea-bot_87090411 -> 87090411
    """
    match = re.search(r"_(\d+)", url)
    return match.group(1) if match else None

# -------------------------------------------------
# STOCK CHECKERS
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
            return size["label"]

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
        product_id = extract_mango_product_id(url)
    else:
        product_id = extract_inditex_product_id(url)

    print(f"🔎 {store.upper()} | {product_id}")

    if not product_id:
        print("⚠️ Product ID çıkarılamadı")
        continue

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
