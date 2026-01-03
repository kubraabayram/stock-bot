import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from scraperHelpers import (
    check_stock_zara,
    check_stock_bershka,
    check_stock_mango,
    check_stock_stradivarius
)

# =====================
# LOAD CONFIG
# =====================
with open("config.json", "r") as f:
    config = json.load(f)

urls_to_check = config["urls"]
sizes_to_check = config["sizes_to_check"]

# =====================
# TELEGRAM
# =====================
BOT_API = os.getenv("BOT_API")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(message):
    if not BOT_API or not CHAT_ID:
        print("Telegram env eksik")
        return

    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    requests.post(
        url,
        data={"chat_id": CHAT_ID, "text": message},
        timeout=10
    )

# =====================
# SELENIUM (TEK SEFER)
# =====================
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("🤖 Stok kontrolü başladı")

# =====================
# MAIN (TEK TUR)
# =====================
try:
    for item in urls_to_check:
        url = item["url"]
        store = item["store"]

        print(f"🔍 Kontrol ediliyor: {url}")
        driver.get(url)

        if store == "zara":
            size = check_stock_zara(driver, sizes_to_check)
        elif store == "stradivarius":
            size = check_stock_stradivarius(driver, sizes_to_check)    
        elif store == "bershka":
            size = check_stock_bershka(driver, sizes_to_check)
        elif store == "mango":
            size = check_stock_mango(driver, sizes_to_check)
        else:
            continue

        if size:
            message = f"🛍️ {size} beden STOKTA!\n{url}"
            send_telegram_message(message)
            print("🔥 STOK VAR")
        else:
            print("⏳ Stok yok")

except Exception as e:
    send_telegram_message(f"⚠️ Bot hata verdi:\n{e}")
    raise

finally:
    driver.quit()
