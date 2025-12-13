import requests
from bs4 import BeautifulSoup
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline
from config.db import get_db
db = get_db()

r = requests.get("https://itu.edu.pk/financial-assistance/")
soup = BeautifulSoup(r.text, "html.parser")
scholarships = []

table = soup.find("table", class_="table table-striped table-bordered table-hovered")
rows = table.find_all('tr')
in_undergrad_section = False

for row in rows:
    cells = row.find_all('td')
    
    if len(cells) == 0:
        continue
    
    if len(cells) == 1 and 'undergraduate' in cells[0].get_text().lower():
        in_undergrad_section = True
        continue

    if len(cells) == 1 and 'graduate' in cells[0].get_text().lower() and 'undergraduate' not in cells[0].get_text().lower():
        in_undergrad_section = False
        continue

    if in_undergrad_section and len(cells) == 4:
        name = cells[1].get_text(strip=True)
        category = cells[2].get_text(strip=True)
        notes = cells[3].get_text(strip=True)
        scholarships.append(Scholarship(  
        name=name,
        type=category,
        link="https://itu.edu.pk/financial-assistance/",
        notes=notes,
        ))

print(f"Found {len(scholarships)} undergraduate scholarships")


print("\n Scraping ITU Programs with Individual Fees and Eligibility...")
req = requests.get("https://itu.edu.pk/admissions/fee-structure/")
sp = BeautifulSoup(req.text, "html.parser")


dept_map = {
    "computer science": "Department of Computer Science",
    "artificial intelligence": "Department of Artificial Intelligence",
    "electrical engineering": "Faculty of Engineering",
    "software engineering": "Faculty of Engineering",
    "computer engineering": "Faculty of Engineering",
    "management": "Faculty of Business & Management Sciences",
    "fintech": "Faculty of Business & Management Sciences",
    "financial technology": "Faculty of Business & Management Sciences",
    "economics": "Faculty of Humanities & Social Sciences"
}

programs = []

data = sp.find('div', class_="fusion-text fusion-text-1 fusion-text-no-margin")
if data:
    headers = data.find_all('h4')
    
    for header in headers:
        if 'undergraduate' in header.get_text().lower():
            ul = header.find_next('ul')
            if ul:
                links = ul.find_all('li')
                
                
                for li in links:
                    link = li.find('a')
                    if link and link.get('href'):
                        program_name = link.get_text(strip=True)
                        program_url = link['href']
                        
                        
                        
                        try:
                            prog_req = requests.get(program_url, timeout=10)
                            prog_soup = BeautifulSoup(prog_req.text, "html.parser")
                            
                            # Get eligibility notes
                            eligibility_notes = []
                            elig_section = prog_soup.find('div', id='eligibility-criteria')
                            if elig_section:
                                for li in elig_section.find_all('li'):
                                    text = li.get_text(strip=True)
                                    if text:
                                        eligibility_notes.append(text)
                            
                            # Get fees from table
                            fee_per_semester = None
                            fee_first_year = None
                            
                            fee_heading = prog_soup.find('h3', string=re.compile("New Intake 2025", re.I))
                            if fee_heading:
                                table = fee_heading.find_next('table')
                                if table:
                                    rows = table.find_all('tr')
                                    for row in rows:
                                        cols = row.find_all('td')
                                        if len(cols) >= 2:
                                            text = cols[0].get_text(strip=True).lower()
                                            
                                            if 'first semester' in text:
                                                fee_text = cols[-1].get_text(strip=True)
                                                match = re.search(r'[\d,]+', fee_text)
                                                if match:
                                                    fee_per_semester = int(match.group().replace(',', ''))
                                            
                                            if 'second semester' in text:
                                                fee_text = cols[-1].get_text(strip=True)
                                                match = re.search(r'[\d,]+', fee_text)
                                                if match:
                                                    second_fee = int(match.group().replace(',', ''))
                                                    if fee_per_semester:
                                                        fee_first_year = fee_per_semester + second_fee
                            
                            # Determine department
                            dept = "Information Technology University"
                            for key, value in dept_map.items():
                                if key in program_name.lower():
                                    dept = value
                                    break
                            
                            # Create program
                            programs.append(Program(
                                name=program_name,
                                department=dept,
                                fee_per_semester=fee_per_semester if fee_per_semester else 202000,
                                total_fee_first_year=fee_first_year if fee_first_year else 397250,
                                eligibility=Eligibility(
                                    min_percentage_matric=50.0,
                                    min_percentage_inter=50.0,
                                    entry_test="ITU Admissions Test or SAT/USAT",
                                    notes=" | ".join(eligibility_notes[:3]) if eligibility_notes else ""
                                )
                            ))
                            
                        except Exception as e:
                            print(f"         ⚠ Error: {e}")
                            continue

print(f"   → Total: {len(programs)} programs scraped")



req = requests.get("https://itu.edu.pk/admissions/")
soup = BeautifulSoup(req.text, "html.parser")
table = soup.find('table', class_="table table-bordered table-hovered")
rows = table.find_all('tr')[1:] 
deadlines = []

undergrad_keywords = ["undergraduate", "bs", "sat", "usat", "nat", "ecat", 
                      "bseds", "bsm&t", "bscs", "bsai", "bsse", "bsce", "bsee"]
grad_only_keywords = ["graduate test", "ms interviews", "msdevs", "mspps", 
                      "gre", "gat", "phd"]
general_keywords = ["online admissions", "merit list", "commencement", "classes"]

in_undergrad_section = False
current_context = ""  

for row in rows:
    cols = row.find_all('td')
    
    if len(cols) >= 3:
        title = cols[1].get_text(strip=True)
        date = cols[2].get_text(strip=True)
        
        if not date or date == "&nbsp;" or not date.strip():
            if "undergraduate" in title.lower():
                in_undergrad_section = True
                current_context = ""
            elif "graduate" in title.lower() and "undergraduate" not in title.lower():
                in_undergrad_section = False
                current_context = ""
            elif "test" in title.lower() and in_undergrad_section:
                current_context = "Undergraduate Admissions Test - "
            elif "interview" in title.lower() and "bs" in title.lower():
                current_context = "Undergraduate Interview - "
            continue
        
        title_lower = title.lower()
        is_general = any(keyword in title_lower for keyword in general_keywords)
        is_undergrad_specific = any(keyword in title_lower for keyword in undergrad_keywords)
        is_grad_only = any(keyword in title_lower for keyword in grad_only_keywords)
        
        if (is_general or is_undergrad_specific or in_undergrad_section) and not is_grad_only:

            display_title = title
        
            if any(code in title_lower for code in ["bscs", "bsai", "bsse", "bsce", "bsee", "bseds", "bsm&t"]):
                if current_context and current_context not in display_title:
                    display_title = current_context + title
            deadlines.append(EmbeddedDeadline(title=display_title, deadline_date=date))

print(f"\nTotal undergraduate deadlines: {len(deadlines)}")

itu = University(
    name="ITU",
    full_name="Information Technology University of the Punjab",
    city="Lahore",
    address="Arfa Software Technology Park, Lahore, Pakistan",
    website="https://itu.edu.pk",
    email="admissions@itu.edu.pk",
    admission_link="https://itu.edu.pk/admissions/",
    programs=programs,                 
    scholarships=scholarships,        
    deadlines=deadlines                
)


standalone_deadlines = []
for d in deadlines:
    deadline_obj = Deadline(
        university_name="ITU",
        title=d.title,
        deadline_date=d.deadline_date,
        url="https://itu.edu.pk/admissions/"
    )
    standalone_deadlines.append(deadline_obj)

def save_to_database():
    db = get_db()
    db.universities.delete_many({"name": "ITU"})
    db.deadlines.delete_many({"university_name": "Information Technology University of the Punjab"})
    db.universities.insert_one(itu.dict())
    db.deadlines.insert_many([d.dict() for d in standalone_deadlines])

if __name__ == "__main__":
    save_to_database()
    print("ITU data saved to database.")