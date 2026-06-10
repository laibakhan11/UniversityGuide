import sys
from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.db import get_universities_collection

# -------------------------------
# MongoDB
# -------------------------------
universities_collection = get_universities_collection()
universities = list(universities_collection.find({}))

print(f"Connected to MongoDB. Found {len(universities)} universities.\n")

# -------------------------------
# Name Mapping
# -------------------------------
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
}

# -------------------------------
# Selenium
# -------------------------------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

try:

    driver.get(
        "https://www.timeshighereducation.com/world-university-rankings/2026/regional-ranking"
    )

    print("Website opened.\n")

    # Cookie popup
    try:
        cookie_btn = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable(
                (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            )
        )
        cookie_btn.click()
        print("Cookie popup closed.")
    except:
        print("No cookie popup.")

    print(
        "\nIMPORTANT:\n"
        "1. Select Pakistan filter manually\n"
        "2. Wait until Pakistani universities appear\n"
        "3. Press ENTER here\n"
    )

    input("Press ENTER after filtering Pakistan...")

    # Wait for rows
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "tbody tr.group")
        )
    )

    time.sleep(3)

    # -------------------------------
    # Scroll until all rows loaded
    # -------------------------------
    previous_count = 0

    while True:

        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr.group")

        current_count = len(rows)

        print(f"Rows currently loaded: {current_count}")

        if current_count == previous_count:
            break

        previous_count = current_count

        driver.execute_script(
            """
            let tbody = document.querySelector('tbody');
            if(tbody){
                tbody.scrollTop = tbody.scrollHeight;
            }
            """
        )

        time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr.group")

    print(f"\nFinal rows found: {len(rows)}\n")

    scraped_data = {}

    # -------------------------------
    # Scrape Table
    # -------------------------------
    for row in rows:

        try:

            tds = row.find_elements(By.TAG_NAME, "td")

            if len(tds) < 3:
                continue

            # Rank
            rank = tds[0].text.strip()

            # Name
            uni_name = row.find_element(
                By.CSS_SELECTOR,
                "a.institution-link span.chakra-link"
            ).text.strip()

            # Overall Score
            overall = tds[2].text.strip()

            scraped_data[uni_name] = {
                "rank": rank,
                "overall": overall
            }

            print(
                f"{uni_name} | Rank: {rank} | Overall: {overall}"
            )

        except Exception as e:
            print("Skipping row:", e)

    print(f"\nScraped {len(scraped_data)} universities.\n")

    # -------------------------------
    # Update MongoDB
    # -------------------------------
    assigned = 0
    unranked = 0

    for uni in universities:

        db_name = uni["name"].lower()

        mapped_name = name_mapping.get(db_name)

        if mapped_name and mapped_name in scraped_data:

            rank = scraped_data[mapped_name]["rank"]
            overall = scraped_data[mapped_name]["overall"]

            ranking_text = (
                f"Ranked {rank} in THE Asia Rankings 2026 "
                f"| Overall Score: {overall}"
            )

            universities_collection.update_one(
                {"_id": uni["_id"]},
                {"$set": {"ranking": ranking_text}}
            )

            assigned += 1

            print(
                f"[ASSIGNED] {uni['name']} -> {ranking_text}"
            )

        else:

            ranking_text = (
                "Doesn't hold a rank in THE Asia Rankings 2026"
            )

            universities_collection.update_one(
                {"_id": uni["_id"]},
                {"$set": {"ranking": ranking_text}}
            )

            unranked += 1

            print(
                f"[UNRANKED] {uni['name']}"
            )

    print(
        f"\nDone.\nAssigned: {assigned}\nUnranked: {unranked}"
    )

finally:

    driver.quit()
    print("\nBrowser closed.")