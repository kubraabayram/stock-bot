import json
import os
import re
import requests

# -------------------------------------------------
# TELEGRAM
# -------------------------------------------------

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
# HELPERS
# -------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/json"
}

def extract_color_id(url):
    match = re.search(r"colorId=(\d+)", url)
    return match.group(1) if match else None

def size_matches(size_name, wanted_sizes):
    size_name = size_name.lower()
    for s in wanted_sizes:
        if s.lower() in size_name:
            return True
    return False

# -------------------------------------------------
# INDITEX SCRAPER (ZARA / BERSHKA / STRADIVARIUS)
# -------------------------------------------------

def check_inditex_page(url, sizes):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    html = r.text

    match = re.search(
        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        html,
        re.DOTALL
    )
    if not match:
        return None

    data = json.loads(match.group(1))
    wanted_color_id = extract_color_id(url)

    try:
        components = data["product"]["detail"]["commercialComponents"]

        for comp in components:
            for component in comp.get("components", []):
                for sku in component.get("skus", []):

                    # renk filtresi (linkteki colorId)
                    if wanted_color_id:
                        if str(sku.get("colorId")) != wanted_color_id:
                            continue

                    size_name = sku.get("sizeName", "")
                    availability = sku.get("availability")

                    if (
                        size_matches(size_name, sizes)
                        and availability in ["in_stock", "low_stock", "available"]
                    ):
                        return size_name

    except Exception as e:
        print("DEBUG parse error:", e)

    return None

# -------------------------------------------------
# MAIN
# -------------------------------------------------

with open("config.json") as f:
    config = json.load(f)

sizes_to_check = config["sizes_to_check"]

print("🟢 Stok kontrolü başladı")

# 🔔 TEST BLOĞU (sadece ilk çalışmada mesaj atar)
send_telegram("✅ Stock bot çalıştı ve Telegram bağlantısı başarılı.")

for item in config["urls"]:
    store = item["store"]
    url = item["url"]

    print(f"\n🔎 {store.upper()} sayfası taranıyor")

    # Mango GitHub Actions’ta bilinçli olarak atlanıyor
    if store == "mango":
        print("⏭️ MANGO atlandı")
        continue

    try:
        size = check_inditex_page(url, sizes_to_check)

        if size:
            msg = f"🛍️ {store.upper()} | {size} BEDEN STOKTA!\n{url}"
            print("✅ STOK VAR")
            send_telegram(msg)
        else:
            print("⛔ Stok yok")

    except Exception as e:
        print(f"⚠️ Hata: {e}")

