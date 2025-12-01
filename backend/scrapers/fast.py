import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.db import get_db
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline

r=requests.get("https://nu.edu.pk/admissions/schedule")
soup=BeautifulSoup(r.text,'html.parser')
emdeadlines=[]
deadline=[]
table=soup.find('table',class_="edu-table-responsive table-condensed table-bordered table-hover table-striped")
for row in table.find('tbody',class_="table-body").find_all('tr'):
    dd=row.find_all('td')[:2]
    e = EmbeddedDeadline(
    title = dd[0].text.strip(),
    deadline_date = dd[1].text.strip())
    emdeadlines.append(e)
    d=Deadline(
    university_name="NUST",
    title = dd[0].text.strip(),
    deadline_date = dd[1].text.strip())
    deadline.append(d)


req = requests.get("https://nu.edu.pk/Admissions/Scholarship")
soup = BeautifulSoup(req.text, 'html.parser')

scholarships = []
scholar = soup.find_all('div', class_="group-title-index")

for title in scholar:
    h2_tag = title.find('h2', class_="underline center-title") or title.find('h2')
    if not h2_tag:
        continue
    
    current = h2_tag.text.strip()

    if "scholarship" not in current.lower():
        continue
    
    if any(keyword in current for keyword in ['MSc', 'MS', 'PhD', 'Master']):
        continue

    # Get the notes from the NEXT <p> tag AFTER the div (not inside it)
    p_tag = title.find_next_sibling('p', class_="text-justify") or title.find_next_sibling('p')
    notes = p_tag.text.strip() if p_tag else ""

    current_lower = current.lower()
    notes_lower = notes.lower()
    
    if "merit" in current_lower and "need" not in current_lower and "need" not in notes_lower:
        scholarship_type = "merit"
    elif "need" in current_lower or "need" in notes_lower:
        scholarship_type = "need-based"
    else:
        scholarship_type = "other"

    s = Scholarship(
        name=current,
        type=scholarship_type,
        notes=notes
    )
    scholarships.append(s)


ADMISSION_FEE = 30000
SECURITY_DEPOSIT = 20000
TUITION_PER_CREDIT = 11000
ACTIVITIES_PER_SEM = 2500

def calculate_first_year_fee(credits: int) -> int:
    return ADMISSION_FEE + SECURITY_DEPOSIT + (credits * TUITION_PER_CREDIT) + (ACTIVITIES_PER_SEM * 2)

FEE_NOTES = "Rs. 11,000 per credit hour + Rs. 2,500 activities per semester. First-year includes one-time Rs. 30,000 admission + Rs. 20,000 refundable security."

computing_eligibility = Eligibility(
    min_percentage_matric=60.0,
    min_percentage_inter=50.0,
    entry_test="FAST-NUCES / SAT / NTS NAT-IE or NAT-ICS",
    notes="Mathematics required in Intermediate. Pre-Medical with Additional Maths accepted."
)

engineering_eligibility = Eligibility(
    min_percentage_matric=60.0,
    min_percentage_inter=60.0,
    entry_test="FAST-NUCES / SAT / NTS NAT-IE",
    notes="Pre-Engineering (Physics, Chemistry, Maths) or ICS (Physics, Maths, Computer Science)"
)

business_eligibility = Eligibility(
    min_percentage_matric=60.0,
    min_percentage_inter=50.0,
    entry_test="FAST-NUCES / SAT / NTS NAT-IE/ICS/ICOM/IGS",
    notes="Any Intermediate discipline"
)

programs = [
    Program(
        name="BS Electrical Engineering",
        department="Faculty of Engineering",
        total_fee_first_year=calculate_first_year_fee(37),
        eligibility=engineering_eligibility,
        notes=FEE_NOTES
    ),
    Program(name="BS Artificial Intelligence",  department="School of Computing", total_fee_first_year=calculate_first_year_fee(36), eligibility=computing_eligibility, notes=FEE_NOTES),
    Program(name="BS Computer Science",         department="School of Computing", total_fee_first_year=calculate_first_year_fee(36), eligibility=computing_eligibility, notes=FEE_NOTES),
    Program(name="BS Cyber Security",           department="School of Computing", total_fee_first_year=calculate_first_year_fee(36), eligibility=computing_eligibility, notes=FEE_NOTES),
    Program(name="BS Data Science",             department="School of Computing", total_fee_first_year=calculate_first_year_fee(36), eligibility=computing_eligibility, notes=FEE_NOTES),
    Program(name="BS Software Engineering",    department="School of Computing", total_fee_first_year=calculate_first_year_fee(36), eligibility=computing_eligibility, notes=FEE_NOTES),


    Program(name="BBA",                               department="Faculty of Management Sciences", total_fee_first_year=calculate_first_year_fee(35), eligibility=business_eligibility, notes=FEE_NOTES),
    Program(name="BS Accounting & Finance",           department="Faculty of Management Sciences", total_fee_first_year=calculate_first_year_fee(35), eligibility=business_eligibility, notes=FEE_NOTES),
    Program(name="BS Business Analytics",             department="Faculty of Management Sciences", total_fee_first_year=calculate_first_year_fee(35), eligibility=business_eligibility, notes=FEE_NOTES),
    Program(name="BS Financial Technology",           department="Faculty of Management Sciences", total_fee_first_year=calculate_first_year_fee(37), eligibility=business_eligibility, notes=FEE_NOTES),
]

fast = University(
    name="FAST-NU Lahore",
    full_name="National University of Computer and Emerging Sciences - Lahore Campus",
    city="Lahore",
    address="FAST-NUCES, Akbar Chowk, Moulana Shoukat Ali Road, Faisal Town, Lahore",
    website="https://lhr.nu.edu.pk",
    email="admissions@nu.edu.pk",
    admission_link="https://www.nu.edu.pk/Admissions",
    programs=programs,
    scholarships=scholarships,  
    deadlines=emdeadlines        
)

def save_to_database():
    db = get_db()
    db.universities.delete_many({"name": "FAST-NU Lahore"})
    db.deadlines.delete_many({"university_name": "FAST-NU Lahore"})
    db.universities.insert_one(fast.dict())
    db.deadlines.insert_many([d.dict() for d in deadline])



if __name__ == "__main__":
    save_to_database()