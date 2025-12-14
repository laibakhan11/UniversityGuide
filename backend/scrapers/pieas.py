import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.db import get_db, get_deadlines_collection
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ADMISSION_FEE = 25000
SECURITY_FEE = 25000  

TUITION_FEE_PER_CREDIT = 3500
CREDITS_PER_SEMESTER = 18
TUITION_FEE_PER_SEMESTER = TUITION_FEE_PER_CREDIT * CREDITS_PER_SEMESTER  # 63,000

REGISTRATION_FEE = 2000
PERN_DIGITAL_LIBRARY = 10000
LIBRARY_DEV_FUND = 1000
HOSTEL_TRANSPORT_CONSERVATION = 2000
STUDENTS_CLUBS_FEE = 3000
EXAMINATION_FEE = 3000
TRANSPORT_CHARGES = 15000

TOTAL_RECURRING_PER_SEMESTER = (
    TUITION_FEE_PER_SEMESTER + 
    REGISTRATION_FEE + 
    PERN_DIGITAL_LIBRARY + 
    LIBRARY_DEV_FUND + 
    HOSTEL_TRANSPORT_CONSERVATION + 
    STUDENTS_CLUBS_FEE + 
    EXAMINATION_FEE + 
    TRANSPORT_CHARGES
) 

FIRST_YEAR_TOTAL = ADMISSION_FEE + SECURITY_FEE + (TOTAL_RECURRING_PER_SEMESTER * 2)  # 248,000

FEE_NOTES = (
    f"First year total includes one-time Admission Fee (Rs. {ADMISSION_FEE:,}) and "
    f"refundable Security Deposit (Rs. {SECURITY_FEE:,}). "
    f"Per semester fee breakdown: Tuition Rs. {TUITION_FEE_PER_SEMESTER:,}, "
    f"Registration Rs. {REGISTRATION_FEE:,}, PERN/Digital Library Rs. {PERN_DIGITAL_LIBRARY:,}, "
    f"Library Fund Rs. {LIBRARY_DEV_FUND:,}, Transport Rs. {TRANSPORT_CHARGES:,}, "
    f"Examination Rs. {EXAMINATION_FEE:,}, and other charges."
)


pieas_scholarships = []

url_scholarships = "https://www.pieas.edu.pk/scholarships/"
r = requests.get(url_scholarships)
soup = BeautifulSoup(r.text, "html.parser")

menu_div = soup.find("div", id="menu1")

if menu_div:
    strongs = menu_div.find_all("strong")
    
    for strong in strongs:
        text = strong.get_text(strip=True)
        
        
        if "PIEAS Need Based Scholarships" in text or "Qarz-e-Hasna Program" in text:
            parent = strong.parent
            notes_text = ""
            for sibling in parent.find_next_siblings():
                if sibling.name == "strong":
                    break
                if sibling.name == "br":
                    continue
                notes_text += sibling.get_text(" ", strip=True) + " "
                if len(notes_text) > 300:
                    break
            
            pieas_scholarships.append(
                Scholarship(
                    name="PIEAS Need Based Scholarships/Qarz-e-Hasna Program",
                    type="Need-based",
                    link="https://www.pieas.edu.pk/scholarships/",
                    notes=notes_text.strip()[:300]
                )
            )
        
        
        elif "PIEAS Education Support fund" in text or "Education Support Fund" in text:
            parent = strong.parent
            notes_text = ""
            for sibling in parent.find_next_siblings():
                if sibling.name == "strong":
                    break
                if sibling.name == "br":
                    continue
                notes_text += sibling.get_text(" ", strip=True) + " "
                if len(notes_text) > 300:
                    break
            
            pieas_scholarships.append(
                Scholarship(
                    name="PIEAS Education Support Fund (ESF)",
                    type="Need-based",
                    link="https://www.pieas.edu.pk/scholarships/",
                    notes=notes_text.strip()[:300]
                )
            )
        
       
        elif "Ehsaas" in text or "Benazir Undergraduate" in text:
            parent = strong.parent
            notes_text = ""
            link = "http://ehsaas.hec.gov.pk"
            
            for sibling in parent.find_next_siblings():
                if sibling.name == "strong":
                    break
                if sibling.name == "br":
                    continue
                notes_text += sibling.get_text(" ", strip=True) + " "
                if len(notes_text) > 300:
                    break
            
            pieas_scholarships.append(
                Scholarship(
                    name="Ehsaas / Benazir Undergraduate Scholarship Program",
                    type="Need-based",
                    link=link,
                    notes=notes_text.strip()[:300]
                )
            )
        
       
        elif "PEEF" in text and "Punjab Educational Endowment Fund" in text:
            parent = strong.parent
            notes_text = ""
            link = "https://www.peef.org.pk/peef-scholarships"
            
            for sibling in parent.find_next_siblings():
                if sibling.name == "strong":
                    break
                if sibling.name == "br":
                    continue
                notes_text += sibling.get_text(" ", strip=True) + " "
                if len(notes_text) > 300:
                    break
            
            pieas_scholarships.append(
                Scholarship(
                    name="PEEF - Punjab Educational Endowment Fund",
                    type="Need & Merit-based",
                    link=link,
                    notes=notes_text.strip()[:300]
                )
            )
        
       
        elif "Fellowships" in text and "BS programs" in text:
            parent = strong.parent
            notes_text = ""
            
            for sibling in parent.find_next_siblings():
                if sibling.name == "strong":
                    break
                if sibling.name == "br":
                    continue
                notes_text += sibling.get_text(" ", strip=True) + " "
                if len(notes_text) > 300:
                    break
            
            pieas_scholarships.append(
                Scholarship(
                    name="Fellowships from R&D and Public Sector Organizations",
                    type="Merit-based",
                    link="https://www.pieas.edu.pk/scholarships/",
                    notes=notes_text.strip()[:300]
                )
            )
        
        
        elif "USAID" in text:
            parent = strong.parent
            notes_text = ""
            link = "http://scholarship.hec.gov.pk"
            
            for sibling in parent.find_next_siblings():
                if sibling.name == "strong":
                    break
                if sibling.name == "br":
                    continue
                notes_text += sibling.get_text(" ", strip=True) + " "
                if len(notes_text) > 300:
                    break
            
            pieas_scholarships.append(
                Scholarship(
                    name="USAID Funded Merit and Needs Based Scholarship Program (MNBSP)",
                    type="Merit & Need-based",
                    link=link,
                    notes=notes_text.strip()[:300]
                )
            )



embedded_deadlines = []
standalone_deadlines = []

url = "https://admissions.pieas.edu.pk/Admissions/schedule.html"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

content = soup.find("div", class_="blog-content")

if content:
    headings = content.find_all("h2", class_="blogpost-title")

    for h2 in headings:
        heading_text = h2.get_text(strip=True).lower()
        if "bs admissions" in heading_text or "undergraduate" in heading_text:
            table = h2.find_next_sibling("table")
            if not table:
                continue

            rows = table.find_all("tr")

            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue

                title = cells[0].get_text(" ", strip=True)
                date = cells[1].get_text(" ", strip=True)
                
                if title and date:
                    embedded_deadlines.append(
                        EmbeddedDeadline(title=title, deadline_date=date)
                    )
                    standalone_deadlines.append(
                        Deadline(
                            university_name="PIEAS Islamabad",
                            title=title,
                            deadline_date=date,
                            url=url
                        )
                    )


programs = []
url_programs = "https://admissions.pieas.edu.pk/Admissions/BS.html"
r = requests.get(url_programs)
soup = BeautifulSoup(r.text, "html.parser")

table = soup.find("table", class_="table table-bordered")
headers = table.find("thead").find_all("th")
dept1 = headers[0].get_text(strip=True) if len(headers) > 0 else "Engineering"
dept2 = headers[1].get_text(strip=True) if len(headers) > 1 else "Sciences"

rows = table.find("tbody").find_all("tr")

for row in rows:
    cells = row.find_all("td")
    

    if len(cells) > 0:
        name1 = cells[0].get_text(" ", strip=True)
        if name1 and name1 != "":
            prog_lower = name1.lower()
            
            if "engineering" in prog_lower or dept1 == "Engineering":
                eligibility_notes = "Pre-Engineering or equivalent with Physics, Chemistry, and Mathematics required. Minimum 60% marks in FSc or equivalent."
            elif "computer" in prog_lower:
                eligibility_notes = "Pre-Engineering or Computer Science with Mathematics, Physics required. Minimum 60% marks in FSc or equivalent."
            elif "physics" in prog_lower:
                eligibility_notes = "Pre-Engineering or Pre-Medical with Physics and Mathematics required. Minimum 60% marks in FSc or equivalent."
            elif "mathematics" in prog_lower or "statistics" in prog_lower:
                eligibility_notes = "Pre-Engineering, Computer Science, or Science group with Mathematics required. Minimum 60% marks in FSc or equivalent."
            elif any(x in prog_lower for x in ["chemistry", "environmental", "materials"]):
                eligibility_notes = "Pre-Engineering or Pre-Medical with Chemistry required. Minimum 60% marks in FSc or equivalent."
            else:
                eligibility_notes = "Pre-Engineering or Pre-Medical with relevant subjects. Minimum 60% marks in FSc or equivalent."
            
            programs.append(
                Program(
                    name=name1,
                    department=dept1,
                    fee_per_semester=TOTAL_RECURRING_PER_SEMESTER,
                    total_fee_first_year=FIRST_YEAR_TOTAL,
                    eligibility=Eligibility(
                        min_percentage_matric=60,
                        min_percentage_inter=60,
                        entry_test="PIEAS GRE Equivalent Test or GRE/NTS GAT (Subject) Test",
                        notes=eligibility_notes
                    ),
                    notes=FEE_NOTES
                )
            )


    if len(cells) > 1:
        name2 = cells[1].get_text(" ", strip=True)
        if name2 and name2 != "":
            prog_lower = name2.lower()
            
            if "engineering" in prog_lower:
                eligibility_notes = "Pre-Engineering or equivalent with Physics, Chemistry, and Mathematics required. Minimum 60% marks in FSc or equivalent."
            elif "computer" in prog_lower:
                eligibility_notes = "Pre-Engineering or Computer Science with Mathematics, Physics required. Minimum 60% marks in FSc or equivalent."
            elif "physics" in prog_lower:
                eligibility_notes = "Pre-Engineering or Pre-Medical with Physics and Mathematics required. Minimum 60% marks in FSc or equivalent."
            elif "mathematics" in prog_lower or "statistics" in prog_lower:
                eligibility_notes = "Pre-Engineering, Computer Science, or Science group with Mathematics required. Minimum 60% marks in FSc or equivalent."
            elif any(x in prog_lower for x in ["chemistry", "environmental", "materials"]):
                eligibility_notes = "Pre-Engineering or Pre-Medical with Chemistry required. Minimum 60% marks in FSc or equivalent."
            else:
                eligibility_notes = "Pre-Engineering or Pre-Medical with relevant subjects. Minimum 60% marks in FSc or equivalent."
            
            programs.append(
                Program(
                    name=name2,
                    department=dept2,
                    fee_per_semester=TOTAL_RECURRING_PER_SEMESTER,
                    total_fee_first_year=FIRST_YEAR_TOTAL,
                    eligibility=Eligibility(
                        min_percentage_matric=60,
                        min_percentage_inter=60,
                        entry_test="PIEAS GRE Equivalent Test or GRE/NTS GAT (Subject) Test",
                        notes=eligibility_notes
                    ),
                    notes=FEE_NOTES
                )
            )


db = get_db()
db.universities.delete_many({"name": "PIEAS Islamabad"})

db.universities.insert_one(
    University(
        name="PIEAS Islamabad",
        full_name="Pakistan Institute of Engineering and Applied Sciences",
        city="Islamabad",
        address="Nilore, Islamabad, Pakistan",
        website="https://www.pieas.edu.pk",
        email="admissions@pieas.edu.pk",
        admission_link="https://admissions.pieas.edu.pk",
        programs=programs,
        scholarships=pieas_scholarships,
        deadlines=embedded_deadlines
    ).dict()
)

get_deadlines_collection().delete_many({"university_name": "PIEAS Islamabad"})
get_deadlines_collection().insert_many([d.dict() for d in standalone_deadlines])

print("PIEAS data scraped & saved successfully")