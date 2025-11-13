import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random


# === CONFIG ===
TXT_FILES = [
    "smiths_pl.txt",
]
OUTPUT_FILE = "scraped_products.jsonl"

# === SETUP SELENIUM ===
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
#options.add_argument("--headless=new")  # Use new headless mode in Chrome 109+
options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# === HELPERS ===
def scrape_urls_from_files(txt_files):
    all_urls = []
    for file in txt_files:
        with open(file, "r") as f:
            urls = [clean_url(line) for line in f if line.strip()]
            all_urls.extend(urls)
    return all_urls

def clean_url(line):
    # Remove trailing XML tags and whitespace
    return line.strip().replace("</loc>", "")

# === MAIN ===
def scrape_all(index):
    urls = scrape_urls_from_files(TXT_FILES)
    print(f"🔍 Found {len(urls)} URLs to scrape")
    with open(OUTPUT_FILE, "a", encoding="utf-8") as out:
        for i, url in enumerate(urls, 1):
            if i < index or url == "":
                continue
            try:
                driver.get(url)
                time.sleep(random.uniform(1.5, 3.5))
                try:
                    button = driver.find_element(By.XPATH,"//button[@aria-label='Close pop-up']")
                    button.click()
                except:
                    print("No Button")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,"//div[@data-testid='auto-grid-cell']"))
                )
                def get_data():
                    elements = driver.find_elements(By.XPATH,"//div[@data-testid='auto-grid-cell']")
                    data = []
                    for element in elements:
                        price = element.find_element(By.XPATH, ".//data[@data-testid='product-item-unit-price']")
                        quantity = element.find_element(By.XPATH, ".//span[@data-testid='product-item-sizing']")
                        title = element.find_element(By.XPATH, ".//span[@data-testid='cart-page-item-description']")
                        data.append({
                            "title": title.text.strip(),
                            "price": price.get_attribute("value"),
                            "quantity": quantity.text.strip(),
                        })
                    for entry in data:
                        out.write(json.dumps(entry) + "\n")
                    print(f"[{i}/{len(urls)}] ✅ Scraped: {len(data)} items")
                    try:
                        button = driver.find_element(By.CSS_SELECTOR,"#content > div > div > div > div.flex.flex-col.Products__container.pb-64 > div.Grid.flex.flex-wrap.list-none.p-0.Grid--full > div.flex.flex-col.gap-24.GridCell.GridCell--grow.max-w-full > div.ProductGridContainer.md\:px-0 > div > div.flex.flex-col.content-center.items-center.mt-32 > button.kds-Button.interactive.palette-accent.kind-prominent.variant-border.my-12.px-32.LoadMore__load-more-button")
                        button.click()
                        get_data()
                    except:
                        print("End of page data")
                get_data()
                
            except Exception as e:
                print(f"[{i}/{len(urls)}] ❌ Failed: {url} — {e}")
            time.sleep(random.uniform(1.5, 3.5))

    driver.quit()

if __name__ == "__main__":
    scrape_all(1) #1414 next item to scrape