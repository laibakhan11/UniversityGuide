import sys
import time
sys.path.append('..')
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Now you can import config and models
from config.db import get_db, get_deadlines_collection
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline

import requests
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================================================
# Department mapping
# =========================================================
department_keywords = {
    "Accounting & Finance": ["accounting", "finance"],
    "Accounting & Law": ["accounting & finance", "law"],
    "Economics": ["economics"],
    "Finance": ["business analytics"],
    "Management": ["bba", "management"],
    "Marketing": ["marketing"],
    "Social Sciences & Liberal Arts": ["social sciences", "liberal arts"],
    "Computer Sciences": ["computer science"],
    "Mathematical Sciences": ["mathematics"]
}

# =========================================================
# Scholarship dictionary
# =========================================================
scholarship_dict = {
    "Punjab Educational Endowment Fund (PEEF) for the academic year 2025-26": {
        "type": "Need-based",
        "link": "https://www.iba.edu.pk/financialassistance/punjab-educational-endowment-fund2025-26.php"
    },
    "Sindh Educational Endowment Fund (SEEF) Trust Scholarship": {
        "type": "Need & Merit-based",
        "link": "https://form-seef.com/"
    },
    "IBA Need Based Financial Assistance": {
        "type": "Need-based",
        "link": "https://www.iba.edu.pk/financialassistance/needbased.php"
    }
}

# =========================================================
# Eligibility dictionary
# =========================================================
eligibility_dict = {
    "BBA": Eligibility(
        min_percentage_matric=65,
        min_percentage_inter=65,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BS (Computer Science)": Eligibility(
        min_percentage_matric=60,
        min_percentage_inter=60,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BS (Economics & Mathematics)": Eligibility(
        min_percentage_matric=60,
        min_percentage_inter=60,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BS (Accounting & Finance)": Eligibility(
        min_percentage_matric=65,
        min_percentage_inter=65,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BS (Social Sciences & Liberal Arts)": Eligibility(
        min_percentage_matric=60,
        min_percentage_inter=60,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BS (Economics)": Eligibility(
        min_percentage_matric=60,
        min_percentage_inter=60,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BS (Mathematics)": Eligibility(
        min_percentage_matric=60,
        min_percentage_inter=60,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BSBA (Business Analytics)": Eligibility(
        min_percentage_matric=65,
        min_percentage_inter=65,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BS (Economics & Data Science)": Eligibility(
        min_percentage_matric=60,
        min_percentage_inter=60,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
    "BSEDS": Eligibility(
        min_percentage_matric=60,
        min_percentage_inter=60,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT"
    ),
}

# =========================================================
# Scrape Programs
# =========================================================
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(
    "https://www.iba.edu.pk/undergraduate.php",
    headers=headers,
    verify=False
)
soup = BeautifulSoup(response.text, "html.parser")

programs_ul = soup.find("div", id="main") \
    .find_all("ul", class_="academic-programs")[1]

iba_programs = []

for li in programs_ul.find_all("li"):
    span = li.find("span")
    if not span:
        continue

    name = span.get_text(strip=True)

    dept = "TBD"
    for d, keys in department_keywords.items():
        if any(k in name.lower() for k in keys):
            dept = d
            break

    eligibility = eligibility_dict.get(
        name,
        Eligibility(min_percentage_matric=0, min_percentage_inter=0, entry_test="TBD")
    )

    iba_programs.append(
        Program(
            name=name,
            department=dept,
            eligibility=eligibility
        )
    )

print(f"✓ Scraped {len(iba_programs)} programs")

# =========================================================
# Scrape Scholarships
# =========================================================
response = requests.get(
    "https://www.iba.edu.pk/scholarships.php",
    headers=headers,
    verify=False
)
soup = BeautifulSoup(response.text, "html.parser")

scholarships = []

for li in soup.select("ul.iba-news li"):
    h3 = li.find("h3")
    if not h3:
        continue

    for strong in h3.find_all("strong"):
        strong.decompose()

    name = h3.get_text(strip=True)
    meta = scholarship_dict.get(name, {})

    scholarships.append(
        Scholarship(
            name=name,
            type=meta.get("type", "TBD"),
            link=meta.get("link", "")
        )
    )

print(f"✓ Scraped {len(scholarships)} scholarships")

# =========================================================
# Scrape Deadlines
# =========================================================
response = requests.get(
    "https://admissions.iba.edu.pk/admission-schedule-fall2025.php",
    headers=headers,
    verify=False
)
soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table", class_="w3-table")
embedded_deadlines = []
standalone_deadlines = []

def extract_date(td):
    span = td.find("span") if td else None
    return span.get_text(strip=True) if span else None

for i, table in enumerate(tables, start=1):
    rows = table.find_all("tr")
    if len(rows) < 6:
        continue

    program_row = rows[4].find_all("td")

    for row in rows[5:]:
        tds = row.find_all("td")
        if not tds:
            continue

        strong = tds[0].find("strong")
        if not strong:
            continue

        title = f"{strong.get_text(strip=True)} - Round {i}"
        text_parts = []

        for idx in [1, 3, 5]:
            if idx >= len(tds) or idx >= len(program_row):
                continue

            date = extract_date(tds[idx])
            if not date:
                continue

            programs = program_row[idx].get_text(strip=True)
            text_parts.append(f"{date} → {programs}")

            standalone_deadlines.append(
                Deadline(
                    university_name="IBA Karachi",
                    title=title,
                    deadline_date=date,
                    url="https://admissions.iba.edu.pk"
                )
            )

        if text_parts:
            embedded_deadlines.append(
                EmbeddedDeadline(
                    title=title,
                    deadline_date="\n".join(text_parts)
                )
            )

print(f"✓ Scraped {len(embedded_deadlines)} embedded deadlines")
print(f"✓ Scraped {len(standalone_deadlines)} standalone deadlines")

# =========================================================
# Selenium Fee Scraper
# =========================================================
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(), options=chrome_options)

def normalize(name):
    """Normalize program names for better matching"""
    return name.lower().replace("&", "and").replace("-", " ").replace("(", "").replace(")", "").strip()

def best_match(scraped_name, programs):
    """Find the best matching program using fuzzy matching"""
    s = normalize(scraped_name)
    best, best_score = None, 0
    
    # Special case mappings for exact matches
    special_mappings = {
        "bsba": "business analytics",
        "bs business analytics": "business analytics"
    }
    
    # Check special mappings first
    for key, value in special_mappings.items():
        if key in s:
            for p in programs:
                if value in normalize(p.name):
                    return p
    
    for p in programs:
        p_normalized = normalize(p.name)
        
        # Exact match (highest priority)
        if s == p_normalized:
            return p
        
        # Direct substring match - but prefer longer matches
        if s in p_normalized or p_normalized in s:
            # Calculate how much of the program name is matched
            match_length = min(len(s), len(p_normalized))
            score = match_length / max(len(s), len(p_normalized))
            if score > best_score:
                best_score = score
                best = p
            continue
        
        # Word-based matching
        scraped_words = set(s.split())
        program_words = set(p_normalized.split())
        
        if not program_words:
            continue
            
        # Calculate match score
        common_words = scraped_words & program_words
        score = len(common_words) / len(program_words)
        
        if score > best_score:
            best_score = score
            best = p
    
    return best if best_score >= 0.4 else None

try:
    print("\n🔍 Scraping fees from IBA website...")
    driver.get("https://www.iba.edu.pk/fee-structure.php")
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Find the undergraduate section
    undergrad_div = soup.find("div", id="Undergraduate")
    if not undergrad_div:
        print("⚠️ Could not find Undergraduate section")
    else:
        tbody = undergrad_div.find("tbody")
        if not tbody:
            print("⚠️ Could not find tbody in Undergraduate section")
        else:
            rows = tbody.find_all("tr")[2:]  # Skip header rows
            print(f"📋 Found {len(rows)} fee rows")
            
            matched_count = 0
            matched_programs = set()  # Track which programs we've matched
            
            for r in rows:
                cols = r.find_all("td")
                if len(cols) < 2:
                    continue

                scraped_program = cols[0].get_text(strip=True)
                fee_text = cols[1].get_text(strip=True).replace(",", "")
                
                try:
                    fee = float(fee_text)
                except:
                    print(f"⚠️ Could not parse fee for '{scraped_program}': {fee_text}")
                    continue

                prog = best_match(scraped_program, iba_programs)
                if prog and prog.name not in matched_programs:  # Only match once
                    prog.fee_per_semester = int(fee)
                    prog.total_fee_first_year = int(fee * 2)
                    matched_programs.add(prog.name)
                    matched_count += 1
                    print(f"✓ Matched '{scraped_program}' → '{prog.name}' (Fee: {fee})")
                elif prog:
                    print(f"⚠️ '{scraped_program}' already matched to '{prog.name}', skipping")
                else:
                    print(f"✗ No match found for '{scraped_program}'")
            
            print(f"\n✓ Successfully matched fees for {matched_count}/{len(rows)} programs")

except Exception as e:
    print(f"❌ Error scraping fees: {str(e)}")
finally:
    driver.quit()

# =========================================================
# Display programs with/without fees
# =========================================================
print("\n" + "="*60)
print("PROGRAM FEE STATUS:")
print("="*60)
programs_with_fees = [p for p in iba_programs if p.fee_per_semester]
programs_without_fees = [p for p in iba_programs if not p.fee_per_semester]

print(f"\n✓ Programs WITH fees ({len(programs_with_fees)}):")
for p in programs_with_fees:
    print(f"  • {p.name}: {p.fee_per_semester}/semester")

print(f"\n✗ Programs WITHOUT fees ({len(programs_without_fees)}):")
for p in programs_without_fees:
    print(f"  • {p.name}")

# =========================================================
# Save to MongoDB
# =========================================================
db = get_db()
db.universities.delete_many({"name": "IBA Karachi"})

db.universities.insert_one(
    University(
        name="IBA Karachi",
        full_name="Institute of Business Administration, Karachi",
        city="Karachi",
        address="University Road, Karachi, Pakistan",
        website="https://www.iba.edu.pk",
        email="admissions@iba.edu.pk",
        admission_link="https://admissions.iba.edu.pk",
        programs=iba_programs,
        scholarships=scholarships,
        deadlines=embedded_deadlines
    ).dict()
)

get_deadlines_collection().delete_many({"university_name": "IBA Karachi"})
get_deadlines_collection().insert_many(
    [d.dict() for d in standalone_deadlines]
)

print("\n✅ IBA data scraped & saved successfully to MongoDB!")