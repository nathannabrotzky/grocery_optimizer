import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome (non-headless to bypass bot detection)
options = Options()
# options.add_argument("--headless")  # Keep this off for now
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Load the disguised sitemap
sitemap_url = "https://www.allrecipes.com/sitemap_1.xml"
driver.get(sitemap_url)

# Get raw page content
html_content = driver.page_source

# Extract product URLs using regex
urls = re.findall(r"https://www\.allrecipes\.com/recipe/[^\s\"']+", html_content)

print(f"✅ Extracted {len(urls)} product URLs")

# Load the disguised sitemap
sitemap_url = "https://www.allrecipes.com/sitemap_2.xml"
driver.get(sitemap_url)

# Get raw page content
html_content = driver.page_source

# Extract product URLs using regex
new_urls = re.findall(r"https://www\.allrecipes\.com/recipe/[^\s\"']+", html_content)
urls = urls + new_urls

print(f"✅ Extracted {len(urls)} product URLs")

# Load the disguised sitemap
sitemap_url = "https://www.allrecipes.com/sitemap_3.xml"
driver.get(sitemap_url)

# Get raw page content
html_content = driver.page_source

# Extract product URLs using regex
new_urls = re.findall(r"https://www\.allrecipes\.com/recipe/[^\s\"']+", html_content)
urls = urls + new_urls

# Load the disguised sitemap
sitemap_url = "https://www.allrecipes.com/sitemap_4.xml"
driver.get(sitemap_url)

# Get raw page content
html_content = driver.page_source

# Extract product URLs using regex
new_urls = re.findall(r"https://www\.allrecipes\.com/recipe/[^\s\"']+", html_content)
urls = urls + new_urls

# Save to file
with open("allrecipes_urls.txt", "w") as f:
    for url in urls:
        url = str(url).replace("</loc>","")
        f.write(url + "\n")

print(f"✅ Extracted {len(urls)} product URLs")

driver.quit()