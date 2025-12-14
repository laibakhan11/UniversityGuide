# nust.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
from pudata import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
try:
    client.admin.command("ismaster")
    print("Connected to MongoDB successfully (NUST)")
except ConnectionFailure:
    print("Failed to connect to MongoDB (NUST)")
    exit()

db = client['university_db']
collection = db['universities']

# Scholarships & Deadlines
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

nust_deadlines = [
    EmbeddedDeadline(
        title="ENTER",
        deadline_date="ENTER"
    )
]

# Selenium Scraper for Islamabad Programs
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=chrome_options)
scraped_programs = []

# Function to decide notes based on program name
def get_notes(program_name):
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

# Fee assignment
FEES = {
    "engineering": 197050 + 500,  # Tuition + Misc
    "social_sciences": 275400 + 500
}

def assign_fees(program_name):
    name_lower = program_name.lower()
    if any(x in name_lower for x in ["engineering", "computer", "natural sciences", "applied sciences", "hnd"]):
        return FEES["engineering"]
    else:
        return FEES["social_sciences"]

# Scrape programs
try:
    print("Opening NUST UG programs page for scraping...")
    driver.get("https://nust.edu.pk/admissions/undergraduates/list-of-ug-programmes-and-institutions/")
    time.sleep(5)  # wait for JS content to load

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on page")

    for table in tables:
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue

            program_name = cols[0].get_text(strip=True)
            institute_name = cols[1].get_text(strip=True)

            if "Islamabad" not in institute_name:
                continue

            notes_text = get_notes(program_name)
            fee = assign_fees(program_name)

            # Assign notes ONLY to eligibility
            program_obj = Program(
                name=program_name,
                department=institute_name,
                fee_per_semester=fee,
                total_fee_first_year=fee*4,
                eligibility=Eligibility(
                    min_percentage_matric=60,
                    min_percentage_inter=60,
                    entry_test="NET/SAT/ACT",
                    notes=notes_text
                ),
                notes=None 
            )
            scraped_programs.append(program_obj)

    print(f"\nScraped {len(scraped_programs)} Islamabad programs with fees.")
    for p in scraped_programs[:5]:  
        print(f"- {p.name}: fee_per_semester = {p.fee_per_semester}, total_fee_first_year = {p.total_fee_first_year}, eligibility.notes = {p.eligibility.notes}")

finally:
    driver.quit()
    print("\nBrowser closed.")

# Insert into MongoDB
if scraped_programs:
    delete_result = collection.delete_many({"name": "NUST Islamabad"})
    if delete_result.deleted_count > 0:
        print(f"Deleted {delete_result.deleted_count} previous NUST document(s).")

    nust_data = University(
        name="NUST Islamabad",
        full_name="National University of Sciences and Technology",
        city="Islamabad",
        address="Scholars Ave, H-12, Islamabad",
        website="https://nust.edu.pk/",
        email="ugadmissions@nust.edu.pk",
        admission_link="https://nust.edu.pk/admissions/",
        application_fee=None,
        programs=scraped_programs,
        scholarships=nust_scholarships,
        deadlines=nust_deadlines
    )

    try:
        insert_result = collection.insert_one(nust_data.dict())
        print(f"\nInserted NUST document with {len(scraped_programs)} programs. Document ID: {insert_result.inserted_id}")
    except Exception as e:
        print("Error inserting NUST document:", e)
else:
    print("No programs scraped. Nothing inserted into MongoDB.")
