import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.db import get_db
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline

# Get PDF URL
page = requests.get("https://www.au.edu.pk/pages/admission/admission_schedule.aspx")
soup = BeautifulSoup(page.content, 'html.parser')
pdfPath = soup.find('iframe')['src']

if not pdfPath.startswith('http'):
    pdfPath = "https://www.au.edu.pk/pages/admission/" + pdfPath

# Read PDF
pdf = requests.get(pdfPath)
pdfReader = PyPDF2.PdfReader(io.BytesIO(pdf.content))

allText = ""
for page in pdfReader.pages:
    allText += page.extract_text()

# Extract U/G deadlines only
lines = allText.split('\n')
ugLines = []

for line in lines:
    line = line.strip()
    if not line or 'MS' in line or 'PhD' in line:
        continue
    if 'U/G' in line:
        ugLines.append(line)

deadlines = []
for line in ugLines:
    match = re.search(r'(\d{1,2}(?:st|nd|rd|th)\s+[A-Za-z]+,?\s+(?:\d\s*){4})', line)
    if not match:
        continue
    
    date = match.group(1)
    while '  ' in date or re.search(r'(\d)\s+(\d)', date):
        date = re.sub(r'(\d)\s+(\d)', r'\1\2', date)
    
    title = line
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day in title:
            title = title.split(day)[0]
            break
    
    title = title.strip()
    if len(title) > 5:
        deadlines.append(EmbeddedDeadline(title=title, deadline_date=date))

# Deadline objects for separate collection
deadlinedb = []
for d in deadlines:
    deadlinedb.append(Deadline(
        university_name="AU",
        title=d.title,
        deadline_date=d.deadline_date,
        url="https://www.au.edu.pk/pages/admission/admission_schedule.aspx"
    ))

scholarships = [
    Scholarship(name="Merit Scholarship", type="merit", notes="Top 3 position holders"),
    Scholarship(name="Ehsaas Undergraduate Scholarship", type="need-based"),
    Scholarship(name="HEC Need Based Grant", type="need-based"),
    Scholarship(name="PEEF", type="need-based"),
    Scholarship(name="PAF Wards Discount", type="other", notes="25% rebate"),
    Scholarship(name="AU Employee Ward Discount", type="other", notes="Up to 50% rebate"),
]

# Get fees
pf = requests.get("https://www.au.edu.pk/pages/admission/fees_financial.aspx")
soup = BeautifulSoup(pf.content, 'html.parser')
table = soup.find('table', class_='table table-responsive table-hover table-striped table-bordered')
rows = table.find_all('tr')[1:]

programs_dict = {}
for row in rows:
    cols = row.find_all('td')
    if len(cols) < 4:
        continue
    
    name = cols[0].text.strip()
    
    if any(word in name for word in ['MS', 'PhD', 'MBA', 'MPhil', 'M.Phil']):
        continue
    
    if not any(word in name for word in ['BS', 'BBA', 'Bachelor']):
        continue
    
    fee_text = cols[3].text.strip().replace(',', '')
    programs_dict[name] = {"fee": int(fee_text) if fee_text.isdigit() else None}

# Department mapping function
def get_department(program_name):
    name_lower = program_name.lower()
    
    if any(word in name_lower for word in ['computer', 'software', 'cyber', 'data science', 'artificial intelligence', 'ai', 'information technology', 'games']):
        return "Faculty of Computing & AI"
    elif any(word in name_lower for word in ['electrical', 'mechanical', 'civil', 'avionics', 'aerospace', 'mechatronics', 'biomedical']):
        return "Faculty of Engineering"
    elif any(word in name_lower for word in ['business', 'management', 'accounting', 'finance', 'marketing', 'bba', 'economics', 'aviation management']):
        return "Air University School of Management"
    elif any(word in name_lower for word in ['english', 'psychology', 'international relations', 'media', 'communication', 'strategic studies']):
        return "Faculty of Social Sciences"
    elif any(word in name_lower for word in ['math', 'physics', 'statistics', 'bioinformatics', 'computational']):
        return "Faculty of Basic & Applied Sciences"
    elif any(word in name_lower for word in ['health', 'tourism', 'hospitality']):
        return "Faculty of Health Sciences"
    elif any(word in name_lower for word in ['education']):
        return "Faculty of Social Sciences"
    else:
        return "Other"

# Get eligibility
elig = requests.get("https://au.edu.pk/pages/Admission/eligibility_criteria.aspx")
soup = BeautifulSoup(elig.content, 'html.parser')
items = soup.find('ul', class_='list-group').find_all('li', class_='list-group-item')

for item in items:
    name = item.find('span').text.strip()
    
    if any(word in name for word in ['MS', 'PhD', 'MBA', 'MPhil', 'M.Phil']):
        continue
    
    if not any(word in name for word in ['BS', 'BBA', 'Bachelor']):
        continue
    
    text = ""
    for div in item.find_all('div'):
        text += div.text.strip() + " "
    
    # Extract percentage
    inter = 50.0
    if '60%' in text or '≥60%' in text:
        inter = 60.0
    elif '55%' in text:
        inter = 55.0
    elif '50%' in text:
        inter = 50.0
    
    # Extract entry test info
    test = "AU Admission Test"
    text_lower = text.lower()
    
    if 'pec' in text_lower:
        test = "AU Admission Test (PEC Approved - Min 33%)"
    elif 'nts' in text_lower or 'hec' in text_lower:
        test = "AU Admission Test/NTS/HEC Test"
    else:
        test = "AU Admission Test"
    
    # Match with fee data
    matched_key = None
    for key in programs_dict.keys():
        if name in key or key in name:
            matched_key = key
            break
    
    if matched_key:
        programs_dict[matched_key]["eligibility"] = Eligibility(
            min_percentage_matric=0.0,
            min_percentage_inter=inter,
            entry_test=test,
            notes=text.strip()
        )

# Create programs
final_programs = []
for name, data in programs_dict.items():
    if "eligibility" not in data:
        data["eligibility"] = Eligibility(
            min_percentage_matric=0.0,
            min_percentage_inter=50.0,
            entry_test="AU Admission Test",
            notes=""
        )
    
    program = Program(
        name=name,
        department=get_department(name),
        fee_per_semester=data["fee"],
        total_fee_first_year=None,
        eligibility=data["eligibility"],
        notes=""
    )
    final_programs.append(program)

print(f"Found {len(final_programs)} BS programs")
print(f"Found {len(deadlines)} deadlines")

# Create University
au = University(
    name="AU",
    full_name="Air University",
    city="Islamabad",
    address="PAF Complex E-9, Islamabad, Pakistan",
    website="https://www.au.edu.pk",
    email="admissions@au.edu.pk",
    admission_link="https://portals.au.edu.pk/admissions/",
    programs=final_programs,
    scholarships=scholarships,
    deadlines=deadlines
)

def save_to_database():
    db = get_db()
    db.universities.delete_many({"name": "AU"})
    db.deadlines.delete_many({"university_name": "AU"})
    db.universities.insert_one(au.dict())
    if deadlinedb:
        db.deadlines.insert_many([d.dict() for d in deadlinedb])
    print("✓ AU data saved to database")

if __name__ == "__main__":
    save_to_database()