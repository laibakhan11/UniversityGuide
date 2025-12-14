# nust_deadline_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pudata import EmbeddedDeadline
import time

#   MongoDB CONNECTION

client = MongoClient("mongodb://localhost:27017/")
try:
    client.admin.command("ismaster")
    print("Connected to MongoDB (Deadline Scraper)")
except ConnectionFailure:
    print("MongoDB connection failed.")
    exit()

db = client["university_db"]
collection = db["universities"]

#   SELENIUM DRIVER SETUP

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)

#   SCRAPE DEADLINES

print("Opening NUST deadlines page...")
driver.get("https://nust.edu.pk/admissions/undergraduates/dates-to-remember/")
time.sleep(5)

main_div = driver.find_element(By.CLASS_NAME, "col-md-8")
tables = main_div.find_elements(By.CLASS_NAME, "my-rteTable-default")[:2]

deadlines_list = []

#   TABLE 1

first_table = tables[0]
rows = first_table.find_elements(By.TAG_NAME, "tr")

for row in rows:
    try:
        th = row.find_element(By.TAG_NAME, "th").text.strip()
        td = row.find_elements(By.TAG_NAME, "td")[0].text.strip()

        deadlines_list.append(
            EmbeddedDeadline(title=th, deadline_date=td)
        )
    except:
        continue

#   TABLE 2

second_table = tables[1]

# Even columns
ths_even = second_table.find_elements(By.CLASS_NAME, "my-rteTableHeaderEvenCol-default")
tds_even = second_table.find_elements(By.CLASS_NAME, "my-rteTableEvenCol-default")

for th, td in zip(ths_even, tds_even):
    deadlines_list.append(
        EmbeddedDeadline(title=th.text.strip(), deadline_date=td.text.strip())
    )

# Last columns
ths_last = second_table.find_elements(By.CLASS_NAME, "my-rteTableHeaderLastCol-default")
tds_last = second_table.find_elements(By.CLASS_NAME, "my-rteTableLastCol-default")

for th, td in zip(ths_last, tds_last):
    deadlines_list.append(
        EmbeddedDeadline(title=th.text.strip(), deadline_date=td.text.strip())
    )

driver.quit()
print("\nScraped", len(deadlines_list), "deadlines successfully.")

update_result = collection.update_one(
    {"name": "NUST Islamabad"},
    {"$set": {"deadlines": [d.dict() for d in deadlines_list]}}
)

if update_result.modified_count > 0:
    print("NUST deadlines updated successfully in MongoDB.")
else:
    print("NUST document not updated — possibly not found.")
