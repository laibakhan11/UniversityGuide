import sys
from pathlib import Path
import re
import time
from difflib import get_close_matches

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add backend folder to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.db import get_universities_collection

# MongoDB
universities_collection = get_universities_collection()
universities = list(universities_collection.find({}))
print(f"Connected to MongoDB. Found {len(universities)} universities in DB.\n")


# Selenium setup
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # uncomment to run headless
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# Manual mapping: DB name -> scraped full name

name_mapping = {
    "nust islamabad": "National University of Sciences and Technology",
    "comsats lahore": "COMSATS University Islamabad",
    "fast-nu lahore": "National University of Computer and Emerging Sciences",
    "giki": "Ghulam Ishaq Khan Institute of Engineering Sciences and Technology",
    "lums": "Lahore University of Management Sciences",
    "umt": "University of Management and Technology",
    "au": "Air University",
    "itu": "Information Technology University of the Punjab",
    "iba karachi": "Institute of Business Administration",
    "pieas islamabad": "Pakistan Institute of Engineering and Applied Sciences",
    "pu": "University of the Punjab",
    # add more mappings as needed
}

# Helper: normalize university names

def normalize_name(name: str) -> str:
    """Normalize university names for matching: lowercase, remove punctuation and common words."""
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)  # remove punctuation
    for word in [
        "university", "of", "the", "and", "institute", "sciences",
        "technology", "management", "academy", "college", "pakistan"
    ]:
        name = name.replace(word, "")
    name = re.sub(r"\s+", " ", name).strip()
    return name

try:

    # Open THE website
    driver.get(
        "https://www.timeshighereducation.com/world-university-rankings/2025/regional-ranking#!/length/25/sort_by/rank/sort_order/asc/cols/scores"
    )
    print("Website opened.\n")

    # Handle cookie popup
    try:
        cookie_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Allow All') or contains(text(),'Reject')]")
            )
        )
        cookie_button.click()
        print("Cookie popup handled.\n")
    except:
        print("No cookie popup detected.\n")

    # Apply Pakistan filter
    region_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.default")))
    region_input.clear()
    region_input.send_keys("Pakistan")
    region_input.send_keys(Keys.ENTER)
    print("Pakistan filter applied.\n")
    time.sleep(2)

    # Scraping universities
    scraped_data = {}
    db_matches = {}    

    while True:
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not rows:
            print("No rows found on this page. Ending scrape.")
            break

        for row in rows:
            uni_name_site = row.find_element(By.CSS_SELECTOR, "a.ranking-institution-title").text.strip()
            rank = row.find_element(By.CSS_SELECTOR, "td.rank").text.strip()
            overall = row.find_element(By.CSS_SELECTOR, "td.overall-score").text.strip()
            scraped_data[uni_name_site] = (rank, overall)

            # Check if it matches a DB university for terminal display (manual mapping only)
            matched_db = None
            for db_short, mapped_name in name_mapping.items():
                if uni_name_site == mapped_name:
                    matched_db = db_short.upper()
                    break
            if matched_db:
                db_matches[uni_name_site] = matched_db

        # Check next button
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "span.dataTables_paginate__next-button")
            if "disabled" in next_button.get_attribute("class"):
                print("Next button disabled. Scraping finished.\n")
                break
            else:
                current_first_row = rows[0].text
                next_button.click()
                wait.until(lambda d: d.find_element(By.CSS_SELECTOR, "tbody tr").text != current_first_row)
                time.sleep(1)
        except:
            print("Next button not found. Scraping finished.\n")
            break

    # Display scraped universities with DB matches
    print("Universities scraped from website:")
    for name, (rank, overall) in scraped_data.items():
        matched = f" (DB: {db_matches[name]})" if name in db_matches else ""
        print(f"  {name} → Rank: {rank}, Overall: {overall}{matched}")
    print("\n")

    # Assign ranking to DB universities
    total_assigned = 0
    total_unranked = 0
    print("Database universities and assigned ranking:")

    for uni in universities:
        uni_name_db = uni['name'].lower()
        current_ranking = uni.get('ranking')

        # Manual mapping first
        mapped_scraped_name = name_mapping.get(uni_name_db)
        if mapped_scraped_name and mapped_scraped_name in scraped_data:
            rank, overall = scraped_data[mapped_scraped_name]
            ranking_text = (
                f"Ranked {rank} Asia University Rankings 2025 Overall Score {overall}"
                if rank.lower() not in ["reporter", "n/a", ""] and overall.lower() not in ["n/a", ""]
                else "Ranked in Asia University Rankings 2025"
            )
            uni['ranking'] = ranking_text
            universities_collection.update_one({"_id": uni["_id"]}, {"$set": {"ranking": uni['ranking']}})
            print(f"[Assigned] {uni['name']} → {uni['ranking']}")
            total_assigned += 1
        else:
            # No fuzzy fallback: strictly mark as unranked
            uni['ranking'] = "Doesn't hold a rank in Asia University Rankings 2025"
            universities_collection.update_one({"_id": uni["_id"]}, {"$set": {"ranking": uni['ranking']}})
            print(f"[Unranked] {uni['name']} → {uni['ranking']}")
            total_unranked += 1

    print(f"\nScraping completed! Total assigned: {total_assigned}, Total unranked: {total_unranked}")

finally:
    driver.quit()
    print("\nBrowser closed (finally).")
