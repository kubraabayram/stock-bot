import json
import re
import requests

STORE_IDS = {
    "zara": "11701",
    "bershka": "34009455",
    "stradivarius": "34009555"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/html"
}

def extract_product_ids_from_page(url):
    """
    Ürün sayfasındaki embedded JSON'dan GERÇEK productId'leri çıkarır
    """
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    html = r.text

    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
    if not match:
        return []

    data = json.loads(match.group(1))

    product_ids = set()

    try:
        products = data["product"]["detail"]["colors"]
        for color in products:
            for prod in color.get("products", []):
                product_ids.add(str(prod["id"]))
    except Exception:
        pass

    return list(product_ids)


def check_inditex_stock(store, product_id, sizes):
    store_id = STORE_IDS[store]

    url = f"https://www.{store}.com/itxrest/2/catalog/store/{store_id}/product/{product_id}/stock"

    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()

    for size in data.get("sizes", []):
        if size.get("name") in sizes and size.get("availability") == "in_stock":
            return size["name"]

    return None
