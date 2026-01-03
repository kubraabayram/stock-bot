from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# =========================
# ZARA
# =========================
def check_stock_zara(driver, sizes_to_check):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(2)

        size_buttons = driver.find_elements(By.XPATH, "//button")

        for btn in size_buttons:
            text = btn.text.strip().upper()

            for size in sizes_to_check:
                if size.upper() == text:
                    disabled = btn.get_attribute("disabled")
                    aria_disabled = btn.get_attribute("aria-disabled")

                    if not disabled and aria_disabled != "true":
                        return size

        return None

    except Exception as e:
        print("Zara stock check error:", e)
        return None


# =========================
# BERSHKA
# =========================
def check_stock_bershka(driver, sizes_to_check):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(2)

        size_elements = driver.find_elements(By.XPATH, "//button")

        for el in size_elements:
            text = el.text.strip().upper()

            for size in sizes_to_check:
                if size.upper() == text:
                    classes = el.get_attribute("class")

                    if "disabled" not in classes.lower():
                        return size

        return None

    except Exception as e:
        print("Bershka stock check error:", e)
        return None


# =========================
# MANGO
# =========================
def check_stock_mango(driver, sizes_to_check):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(2)

        size_elements = driver.find_elements(By.XPATH, "//button")

        for el in size_elements:
            text = el.text.strip().upper()

            for size in sizes_to_check:
                if size.upper() == text:
                    aria_disabled = el.get_attribute("aria-disabled")

                    if aria_disabled != "true":
                        return size

        return None

    except Exception as e:
        print("Mango stock check error:", e)
        return None


# =========================
# STRADIVARIUS
# =========================
def check_stock_stradivarius(driver, sizes_to_check):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(2)

        size_buttons = driver.find_elements(By.XPATH, "//button")

        for btn in size_buttons:
            text = btn.text.strip().upper()

            for size in sizes_to_check:
                if size.upper() == text:
                    disabled = btn.get_attribute("disabled")
                    aria_disabled = btn.get_attribute("aria-disabled")
                    classes = btn.get_attribute("class") or ""

                    if (
                        not disabled
                        and aria_disabled != "true"
                        and "disabled" not in classes.lower()
                    ):
                        return size

        return None

    except Exception as e:
        print("Stradivarius stock check error:", e)
        return None
