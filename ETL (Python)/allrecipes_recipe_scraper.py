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
    "allrecipes_urls.txt",
]
OUTPUT_FILE = "recipes.jsonl"

# === SETUP SELENIUM ===
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
options.add_argument("--headless=new")
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
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,"#mm-recipes-details_1-0 > div.mm-recipes-details__content"))
                )
                script = """
                return {
                title: document.querySelector('#article-header--recipe_1-0 > h1')?.innerText,
                ingredients: document.querySelector('#mm-recipes-structured-ingredients_1-0 > ul')?.innerText,
                details: document.querySelector('#mm-recipes-details_1-0 > div.mm-recipes-details__content')?.innerText,
                quantity: document.querySelector('#mm-recipes-serving-size-adjuster_1-0 > p')?.innerText
                };
                """
                data = driver.execute_script(script)
                out.write(json.dumps(data) + "\n")
                print(f"[{i}/{len(urls)}] ✅ Scraped: {data['title']}")
            except Exception as e:
                print(f"[{i}/{len(urls)}] ❌ Failed: {url} — {e}")
            time.sleep(random.uniform(1.5, 3.5))

    driver.quit()

if __name__ == "__main__":
    scrape_all(1) #1546 next item to scrape