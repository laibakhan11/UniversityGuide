import requests
from bs4 import BeautifulSoup
import sys
import os
import re
import urllib3

requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import get_db
from models.university import (
    University, Program, Eligibility, Scholarship, EmbeddedDeadline
)
from models.deadline import Deadline

# ==================================================
# DATABASE
# ==================================================
db = get_db()
print(f"Collections: {db.list_collection_names()}")
print("UMT Web Scraper Started...\n")

# ==================================================
# GLOBAL FILTERS & HELPERS
# ==================================================

POSTGRAD_KEYWORDS = [
    "ms ", "m.s", "mphil", "phd", "mba", "executive",
    "postgraduate", "graduate", "doctoral",
    "masters", "master"
]


def get_department_category(program_name: str) -> str:
    name = program_name.lower()

    if any(k in name for k in ["engineering", "electrical", "mechanical", "civil"]):
        return "Engineering"

    if any(k in name for k in ["computer", "software", "data", "artificial intelligence", "ai"]):
        return "Computing & IT"

    if any(k in name for k in ["business", "bba", "management", "accounting", "finance", "economics"]):
        return "Business & Management"

    if any(k in name for k in ["pharmacy", "physical therapy", "dpt", "health", "medical"]):
        return "Health Sciences"

    if any(k in name for k in ["law", "llb"]):
        return "Law"

    if any(k in name for k in ["media", "film", "design", "fashion", "fine arts"]):
        return "Arts & Design"

    if any(k in name for k in ["education", "teaching"]):
        return "Education"

    return "General"


# ==================================================
# 1. SCRAPE PROGRAMS & FEES (UNDERGRAD ONLY)
# ==================================================
print("1. Scraping Programs and Fee Structure...")


def scrape_fee_structure():
    url = "https://admissions.umt.edu.pk/fee.aspx"
    programs = []

    try:
        response = requests.get(url, verify=False, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")

        rows = soup.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            program_name = cells[0].get_text(strip=True)
            program_name_lower = program_name.lower()

            if not program_name or "school of" in program_name_lower:
                continue

            # ❌ Skip MS / Postgraduate programs
            if any(k in program_name_lower for k in POSTGRAD_KEYWORDS):
                continue

            fee_text = cells[2].get_text(strip=True)
            try:
                total_fee = int(re.sub(r"[^\d]", "", fee_text))
            except:
                total_fee = 0

            if total_fee <= 0:
                continue

            department = get_department_category(program_name)

            program = Program(
                name=program_name,
                department=department,
                total_fee_first_year=total_fee,
                eligibility=Eligibility(
                    min_percentage_matric=60.0,
                    min_percentage_inter=50.0,
                    entry_test="UMT Entry Test / NAT / SAT",
                    notes="Minimum 50% marks in Intermediate or equivalent"
                )
            )

            programs.append(program)

        print(f"   → Scraped {len(programs)} undergraduate programs")
        return programs

    except Exception as e:
        print(f"   ✗ Error scraping fee structure: {e}")
        return []


programs = scrape_fee_structure()

# ==================================================
# FALLBACK DATA (SAFE & MODEL-COMPATIBLE)
# ==================================================
if len(programs) < 10:
    print("   → Using fallback undergraduate programs...")
    programs = [
        Program(
            name="BS Computer Science",
            department="Computing & IT",
            total_fee_first_year=2090000,
            eligibility=Eligibility(60, 50, "UMT Entry Test / NAT / SAT", "Minimum 50% in Intermediate")
        ),
        Program(
            name="BS Software Engineering",
            department="Computing & IT",
            total_fee_first_year=1990000,
            eligibility=Eligibility(60, 50, "UMT Entry Test / NAT / SAT", "Minimum 50% in Intermediate")
        ),
        Program(
            name="BS Artificial Intelligence",
            department="Computing & IT",
            total_fee_first_year=1890000,
            eligibility=Eligibility(60, 50, "UMT Entry Test / NAT / SAT", "Minimum 50% in Intermediate")
        ),
        Program(
            name="BBA (Hons)",
            department="Business & Management",
            total_fee_first_year=2090000,
            eligibility=Eligibility(60, 50, "UMT Entry Test / NAT / SAT", "Minimum 50% in Intermediate")
        ),
        Program(
            name="Doctor of Pharmacy",
            department="Health Sciences",
            total_fee_first_year=2690000,
            eligibility=Eligibility(60, 60, "UMT Entry Test / NAT / SAT", "FSc Pre-Medical required")
        )
    ]

print(f"   → Total programs saved: {len(programs)}\n")

# ==================================================
# 2. SCHOLARSHIPS
# ==================================================
print("2. Scraping Scholarships...")


def scrape_scholarships():
    url = "https://admissions.umt.edu.pk/Scholarships.aspx"
    data = [
        ("Merit Scholarship", "merit"),
        ("Need Based Financial Assistance", "need-based"),
        ("Kinship / Sibling Scholarship", "need-based"),
        ("Women Empowerment Scholarship", "need-based"),
        ("Sports Talent Scholarship", "merit"),
    ]

    return [Scholarship(name=n, type=t, link=url) for n, t in data]


scholarships = scrape_scholarships()
print(f"   → Scholarships: {len(scholarships)}\n")

# ==================================================
# 3. DEADLINES
# ==================================================
print("3. Adding Admission Deadlines...")

deadlines = [
    EmbeddedDeadline(
        title="Fall Admissions Open",
        deadline_date="November onwards"
    ),
    EmbeddedDeadline(
        title="Application Deadline",
        deadline_date="15 August"
    ),
    EmbeddedDeadline(
        title="Entry Test",
        deadline_date="April – July"
    ),
    EmbeddedDeadline(
        title="Classes Begin",
        deadline_date="August"
    )
]


# ==================================================
# 4. SAVE TO DATABASE (MODEL SAFE)
# ==================================================
print("4. Saving to Database...")

umt = University(
    name="UMT",
    full_name="University of Management and Technology",
    city="Lahore",
    address="C-II, Johar Town, Lahore, Pakistan",
    website="https://umt.edu.pk",
    email="admissions@umt.edu.pk",
    admission_link="https://admissions.umt.edu.pk",
    programs=programs,
    scholarships=scholarships,
    deadlines=deadlines
)

# Clean old data
db.Universities.delete_many({"name": "UMT"})
db.deadlines.delete_many({"university_name": "UMT"})

# Insert fresh data
db.Universities.insert_one(umt.dict())

standalone_deadlines = []
for d in deadlines:
    deadline_obj= Deadline(
    university_name="UMT",
    title=d.title,
    deadline_date=d.deadline_date,
    url="https://admissions.umt.edu.pk/Admissions-Schedule.aspx"
        )
    standalone_deadlines.append(deadline_obj)
    



def save_to_database():
    db = get_db()
    db.universities.delete_many({"name": "UMT"})
    db.deadlines.delete_many({"university_name": "University of Management and Technology"})
    db.universities.insert_one(umt.dict())
    db.deadlines.insert_many([d.dict() for d in standalone_deadlines])

if __name__ == "__main__":
    save_to_database()
    print("UMT data saved to database.")