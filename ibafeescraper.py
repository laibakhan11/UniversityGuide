from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from ibadata import iba_programs 
from pymongo import MongoClient

#  Selenium Setup
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)

# Helper functions
def normalize_name(name):
    return name.lower().replace("(", "").replace(")", "").replace("-", " ").replace("&", "and").strip()

def best_match(scraped_name, programs):
    scraped_norm = normalize_name(scraped_name)
    best_prog = None
    best_score = 0
    for prog in programs:
        prog_name_norm = normalize_name(prog.name)
        if prog_name_norm == "bs business analytics":
            prog_words = prog_name_norm.split() + ["bsba"]
        else:
            prog_words = prog_name_norm.split()
        if not prog_words:
            continue
        matched_words = sum(1 for w in prog_words if w in scraped_norm)
        score = matched_words / len(prog_words)
        if score > best_score:
            best_score = score
            best_prog = prog
    return best_prog if best_score >= 0.5 else None

try:
    print("Opening IBA fee structure page...")
    driver.get("https://www.iba.edu.pk/fee-structure.php")
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    undergrad_div = soup.find("div", id="Undergraduate")
    if not undergrad_div:
        print("Undergraduate div not found!")
        exit()

    table = undergrad_div.find("table", class_="global-table")
    if not table:
        print("Table not found!")
        exit()

    tbody = table.find("tbody")
    if not tbody:
        print("Table body not found!")
        exit()

    rows = tbody.find_all("tr")[2:]  # skip headers

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        scraped_name = cols[0].get_text(strip=True)
        fee_text = cols[1].get_text(strip=True).replace(",", "").strip()

        try:
            fee_per_credit = float(fee_text)
        except ValueError:
            continue

        prog = best_match(scraped_name, iba_programs)
        if prog:
            prog.fee_per_semester = fee_per_credit * 12
            prog.total_fee_first_year = prog.fee_per_semester * 4

finally:
    driver.quit()
    print("Browser closed.\n")

client = MongoClient("mongodb://localhost:27017/")
db = client["university_db"]
collection = db["universities"]

# Convert programs to dictionaries
programs_dict_list = [prog.dict() for prog in iba_programs]

try:
    result = collection.update_one(
        {"name": "IBA Karachi"},         
        {"$set": {"programs": programs_dict_list}}  # update only programs
    )
    if result.matched_count:
        print(f"IBA programs updated successfully. Modified count: {result.modified_count}")
    else:
        print("No existing IBA document found. Consider inserting it first.")
except Exception as e:
    print("Error updating IBA document:", e)


for prog in iba_programs:
    print(f"{prog.name}: Fee per semester = {prog.fee_per_semester}, Total first year = {prog.total_fee_first_year}")
