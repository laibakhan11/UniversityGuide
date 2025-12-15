import sys
import time
sys.path.append('..')
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import models
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline

# Import DB config
from config.db import get_db, get_deadlines_collection

# Import selenium and beautifulsoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# =========================================================
# Scholarships
# =========================================================
nust_scholarships = [
    Scholarship(
        name="PUNJAB EDUCATIONAL ENDOWMENT FUND (PEEF) SCHOLARSHIPS 2024-25",
        type="Need-based",
        link="https://peef.org.pk/"
    ),
    Scholarship(
        name="CHIEF MINISTER'S HONHAAR UNDERGRADUATE SCHOLARSHIP PROGRAM FOR TALENTED STUDENTS OF PUNJAB - 2024",
        type="Merit & Need-based",
        link="https://honhaarscholarship.punjabhec.gov.pk/"
    ),
    Scholarship(
        name="PROVISION OF HIGHER EDUCATION OPPORTUNITIES FOR THE STUDENTS OF BALOCHISTAN & ERSTWHILE FATA (PHASE-III)",
        type="Area/Need-based",
        link="https://www.hec.gov.pk/english/scholarshipsgrants/BF-III/Pages/default.aspx"
    ),
    Scholarship(
        name="FINANCIAL ASSISTANCE FOR UNDERGRADUATE STUDENTS",
        type="Need-Based",
        link="https://nust.edu.pk/admissions/scholarships/financial-assistance-for-undergraduate-students/"
    ),
    Scholarship(
        name="NEED BASED FINANCIAL AID",
        type="Need-Based",
        link="https://nust.edu.pk/admissions/scholarships/need-based-financial-aid/"
    ),
    Scholarship(
        name="INTEREST FREE LOAN (IHSAN TRUST)",
        type="Condition/Need Based",
        link="https://nust.edu.pk/admissions/scholarships/interest-free-loan-ihsan-trust/"
    )
]

# =========================================================
# Helper Functions
# =========================================================
def get_notes(program_name):
    """Generate notes based on program name"""
    program_name = program_name.lower()
    
    if "engineering" in program_name:
        return ("HSSC Computer Science group must clear Chemistry as remedial course if not done. "
                "Pre-Medical group must complete condensed Mathematics course before admission.")
    elif any(x in program_name for x in ["computer science", "data science", "artificial intelligence", "bioinformatics"]):
        return ("Pre-Medical group must complete deficient Mathematics courses if not done in HSSC. "
                "Equivalence certificate from IBCC required for foreign qualifications.")
    elif any(x in program_name for x in ["biotechnology", "environmental science", "agriculture"]):
        return "HSSC Pre-Medical group required. Equivalence certificate from IBCC required for foreign qualifications."
    elif "food science" in program_name:
        return ("HSSC Pre-Engineering or Pre-Medical group required. "
                "Equivalence certificate from IBCC required for foreign qualifications.")
    elif "llb" in program_name:
        return "Valid HEC Law Admission Test (LAT) score required. Equivalence certificate from IBCC required for foreign qualifications."
    elif any(x in program_name for x in ["bba", "economics", "mass communication", "public administration", "psychology", "tourism", "liberal arts"]):
        return "Any combination of HSSC subjects allowed. Equivalence certificate from IBCC required for foreign qualifications."
    elif "accounting and finance" in program_name:
        return "Mathematics, Accounting or Accountancy must be one of the mandatory subjects."
    elif "mathematics" in program_name:
        return "Mathematics must be one of the mandatory subjects in HSSC or A Level."
    elif "physics" in program_name:
        return "Mathematics and Physics must be mandatory subjects in HSSC or A Level."
    elif "chemistry" in program_name:
        return "Chemistry along with Mathematics or Physics must be mandatory subjects in HSSC or A Level."
    elif any(x in program_name for x in ["architecture", "industrial design"]):
        return "Mathematics and Physics must be mandatory subjects in SSC and HSSC or O/A Levels."
    else:
        return ""

def assign_fees(program_name):
    """Assign fees based on program category"""
    FEES = {
        "engineering": 197050 + 500,  # Tuition + Misc
        "social_sciences": 275400 + 500
    }
    
    name_lower = program_name.lower()
    if any(x in name_lower for x in ["engineering", "computer", "natural sciences", "applied sciences", "hnd"]):
        return FEES["engineering"]
    else:
        return FEES["social_sciences"]

# =========================================================
# Selenium Setup
# =========================================================
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)

# =========================================================
# Scrape Programs
# =========================================================
scraped_programs = []

try:
    print("🔍 Opening NUST UG programs page for scraping...")
    driver.get("https://nust.edu.pk/admissions/undergraduates/list-of-ug-programmes-and-institutions/")
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    print(f"📋 Found {len(tables)} tables on page")

    for table in tables:
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue

            program_name = cols[0].get_text(strip=True)
            institute_name = cols[1].get_text(strip=True)

            # Only get Islamabad programs
            if "Islamabad" not in institute_name:
                continue

            notes_text = get_notes(program_name)
            fee = assign_fees(program_name)

            program_obj = Program(
                name=program_name,
                department=institute_name,
                fee_per_semester=fee,
                total_fee_first_year=fee * 2,  # 2 semesters per year
                eligibility=Eligibility(
                    min_percentage_matric=60,
                    min_percentage_inter=60,
                    entry_test="NET/SAT/ACT",
                    notes=notes_text
                )
            )
            scraped_programs.append(program_obj)

    print(f"✓ Scraped {len(scraped_programs)} Islamabad programs")
    
except Exception as e:
    print(f"❌ Error scraping programs: {str(e)}")

# =========================================================
# Scrape Deadlines
# =========================================================
embedded_deadlines = []
standalone_deadlines = []

try:
    print("\n🔍 Opening NUST deadlines page...")
    driver.get("https://nust.edu.pk/admissions/undergraduates/dates-to-remember/")
    time.sleep(5)

    main_div = driver.find_element(By.CLASS_NAME, "col-md-8")
    tables = main_div.find_elements(By.CLASS_NAME, "my-rteTable-default")[:2]

    # TABLE 1
    first_table = tables[0]
    rows = first_table.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        try:
            th = row.find_element(By.TAG_NAME, "th").text.strip()
            td = row.find_elements(By.TAG_NAME, "td")[0].text.strip()

            if th and td:
                embedded_deadlines.append(
                    EmbeddedDeadline(title=th, deadline_date=td)
                )
                standalone_deadlines.append(
                    Deadline(
                        university_name="NUST Islamabad",
                        title=th,
                        deadline_date=td,
                        url="https://nust.edu.pk/admissions/undergraduates/dates-to-remember/"
                    )
                )
        except:
            continue

    # TABLE 2 - Even columns
    second_table = tables[1]
    ths_even = second_table.find_elements(By.CLASS_NAME, "my-rteTableHeaderEvenCol-default")
    tds_even = second_table.find_elements(By.CLASS_NAME, "my-rteTableEvenCol-default")

    for th, td in zip(ths_even, tds_even):
        title = th.text.strip()
        date = td.text.strip()
        
        if title and date:
            embedded_deadlines.append(
                EmbeddedDeadline(title=title, deadline_date=date)
            )
            standalone_deadlines.append(
                Deadline(
                    university_name="NUST Islamabad",
                    title=title,
                    deadline_date=date,
                    url="https://nust.edu.pk/admissions/undergraduates/dates-to-remember/"
                )
            )

    # TABLE 2 - Last columns
    ths_last = second_table.find_elements(By.CLASS_NAME, "my-rteTableHeaderLastCol-default")
    tds_last = second_table.find_elements(By.CLASS_NAME, "my-rteTableLastCol-default")

    for th, td in zip(ths_last, tds_last):
        title = th.text.strip()
        date = td.text.strip()
        
        if title and date:
            embedded_deadlines.append(
                EmbeddedDeadline(title=title, deadline_date=date)
            )
            standalone_deadlines.append(
                Deadline(
                    university_name="NUST Islamabad",
                    title=title,
                    deadline_date=date,
                    url="https://nust.edu.pk/admissions/undergraduates/dates-to-remember/"
                )
            )

    print(f"✓ Scraped {len(embedded_deadlines)} deadlines")

except Exception as e:
    print(f"❌ Error scraping deadlines: {str(e)}")

finally:
    driver.quit()
    print("✓ Browser closed")

# =========================================================
# Save to MongoDB
# =========================================================
if scraped_programs:
    db = get_db()
    
    # Delete existing NUST data
    db.universities.delete_many({"name": "NUST Islamabad"})
    print("\n🗑️ Deleted previous NUST data from universities collection")

    # Create university document
    nust_data = University(
        name="NUST Islamabad",
        full_name="National University of Sciences and Technology",
        city="Islamabad",
        address="Scholars Ave, H-12, Islamabad",
        website="https://nust.edu.pk/",
        email="ugadmissions@nust.edu.pk",
        admission_link="https://nust.edu.pk/admissions/",
        programs=scraped_programs,
        scholarships=nust_scholarships,
        deadlines=embedded_deadlines
    )

    # Insert university
    try:
        insert_result = db.universities.insert_one(nust_data.dict())
        print(f"✅ Inserted NUST with {len(scraped_programs)} programs")
    except Exception as e:
        print(f"❌ Error inserting university: {e}")

    # Insert standalone deadlines
    if standalone_deadlines:
        get_deadlines_collection().delete_many({"university_name": "NUST Islamabad"})
        get_deadlines_collection().insert_many([d.dict() for d in standalone_deadlines])
        print(f"✅ Inserted {len(standalone_deadlines)} standalone deadlines")
