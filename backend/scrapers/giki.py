import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.db import get_db
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get("https://giki.edu.pk/admissions/admissions-undergraduates/scholarships-fa/", verify=False)
soup=BeautifulSoup(r.text,'html.parser')
scholarships=[]
tables=soup.find('div',class_="gdlr-core-text-box-item-content").find_all('table')
rows=tables[0].find_all('tr')[1:]
for row in rows:
    cols=row.find_all('td')
    name=cols[0].text.strip()
    type_="merit" if "merit" in cols[1].text.strip().lower() else "need-based" if "need" in cols[1].text.strip().lower() else "other"
    link_tag=cols[0].find('a')
    link=link_tag['href'].strip() if link_tag else ""
    title=cols[1].text.strip()
    notes=f"{title}-{cols[4].text.strip()}"
    scholarship=Scholarship(
            name=name,
            type=type_,
            link=link,
            notes=notes
    )
    scholarships.append(scholarship)

rows=tables[1].find_all('tr')[1:]
for row in rows:
    cols=row.find_all('td')
    name=cols[0].text.strip()
    type="merit" if "merit" in cols[1].text.strip().lower() else "need-based" if "need" in cols[1].text.strip().lower() else "other"
    link_tag=cols[0].find('a')
    link=link_tag['href'].strip() if link_tag else ""
    title = cols[1].get_text(strip=True)
    imp = cols[4].get_text(strip=True)
    notes = f"{title} - {imp}"   
    scholarship=Scholarship(
            name=name,
            type=type,
            link=link,
            notes=notes
    )
    scholarships.append(scholarship)


req= requests.get("https://giki.edu.pk/admissions/admissions-undergraduates/", verify=False)
soup=BeautifulSoup(req.text,'html.parser')
deadlines=[]
tablediv=soup.find('div',class_="gdlr-core-text-box-item gdlr-core-item-pdlr gdlr-core-item-pdb gdlr-core-left-align gdlr-core-no-p-space").find('div',class_="gdlr-core-text-box-item-content")
table=tablediv.find('table')
rows=table.find_all('tr')
for row in rows:
    tds=row.find_all('td')
    title=tds[0].text.strip()
    deadline=tds[1].text.strip()
    d=EmbeddedDeadline(
       title=title,
       deadline_date=deadline
    )
    deadlines.append(d)


request = requests.get("https://giki.edu.pk/admissions/admissions-undergraduates/ugrad-fees-and-expenses/", verify=False)
soup = BeautifulSoup(request.text, 'html.parser')
table=soup.find('div',class_="gdlr-core-text-box-item gdlr-core-item-pdlr gdlr-core-item-pdb gdlr-core-left-align").find('div',class_="gdlr-core-text-box-item-content").find('table')
rows = table.find_all('tr')
main_fee_row = rows[2]  
cols = main_fee_row.find_all('td')
engineering_semester = int(cols[2].text.strip().replace(',', ''))
management_semester = int(cols[3].text.strip().replace(',', ''))
engineering_annual = int(cols[4].text.strip().replace(',', ''))
management_annual = int(cols[5].text.strip().replace(',', ''))


# For BS Engineering Programs (Chemical, Electrical, Mechanical, Materials, Civil, Textile, etc.)
engineering_eligibility = Eligibility(
    min_percentage_matric=60.0,
    min_percentage_inter=60.0,
    entry_test="GIKI Admission Test",
    notes="HSSC Pre-Engineering/ICS with 60%+ in Math, Physics & Overall. A-Level: D+ in Math & Physics. Merit: 85% test, 15% academics"
)

# For BS Computing Programs (AI, Computer Science, Cyber Security, Data Science, Software Engineering)
computing_eligibility = Eligibility(
    min_percentage_matric=60.0,
    min_percentage_inter=60.0,
    entry_test="GIKI Admission Test",
    notes="HSSC with Math, Physics & any subject with 60%+ in Math, Physics & Overall. A-Level: D+ in Math & Physics. Merit: 85% test, 15% academics"
)

# For BS Management Sciences
management_eligibility = Eligibility(
    min_percentage_matric=60.0,
    min_percentage_inter=60.0,
    entry_test="GIKI Admission Test",
    notes="HSSC any group with 60%+ overall. A-Level: D+ in 2 principal subjects. Merit: 85% test, 15% academics"
)

common_notes = "Non-refundable admission fee: Rs. 75,000. Security deposit: Rs. 40,000 (refundable), 5% admin charges on semester payment. Annual payment waives admin charges."
prg=requests.get("https://giki.edu.pk/programs/", verify=False)
soup=BeautifulSoup(prg.text,'html.parser')
programs=[]
program_div=soup.find('div',class_="gdlr-core-feature-box-item-content").find('p').find_all('a')

for p in program_div:
    program_name=p.text.strip()
    

    if any(word in program_name.upper() for word in ['MS', 'PHD', 'MPHIL', 'M.PHIL']):
        continue
    

    name_lower = program_name.lower()
    

    if any(word in name_lower for word in ['chemical', 'electrical', 'mechanical', 'materials', 'civil', 'textile', 'engineering']):
        program=Program(
            name=program_name,
            department="Faculty of Engineering Sciences",
            fee_per_semester=engineering_semester,
            total_fee_first_year=engineering_annual,
            eligibility=engineering_eligibility,
            notes=common_notes
        )
        programs.append(program)
    

    elif any(word in name_lower for word in ['computer', 'artificial intelligence', 'ai', 'cyber', 'data science', 'software']):
        program=Program(
            name=program_name,
            department="Faculty of Computer Science & Engineering",
            fee_per_semester=engineering_semester,
            total_fee_first_year=engineering_annual,
            eligibility=computing_eligibility,
            notes=common_notes
        )
        programs.append(program)
    
    elif 'management' in name_lower:
        program=Program(
            name=program_name,
            department="Faculty of Management Sciences",
            fee_per_semester=management_semester,
            total_fee_first_year=management_annual,
            eligibility=management_eligibility,
            notes=common_notes
        )
        programs.append(program)

print(f"Found {len(programs)} programs")

basicinfo=University(
    name="GIKI",
    full_name="Ghulam Ishaq Khan Institute of Engineering Sciences and Technology",
    city="Topi Khyber Pakhtunkhwa",
    address="Topi 23640, District Swabi, Khyber Pakhtunkhwa, Pakistan",
    website="https://giki.edu.pk/",
    email="admissions@giki.edu.pk",
    admission_link="https://admissions.giki.edu.pk/register/?_gl=1*asglo0*_ga*MTUyMjkxNTYzNi4xNzY0OTI4NDMw*_ga_8XS4Z2GJ4Z*czE3NjQ5NjA5ODckbzUkZzEkdDE3NjQ5NjI3NDckajYwJGwwJGgw&_ga=2.247546063.990410628.1764928432-1522915636.1764928430",
    programs=programs,
    scholarships=scholarships,
    deadlines=deadlines
)
standalone_deadlines = []
for d in deadlines:
    deadline_obj = Deadline(
        university_name="GIKI",
        title=d.title,
        deadline_date=d.deadline_date,
        url="https://giki.edu.pk/admissions/admissions-undergraduates/"
    )
    standalone_deadlines.append(deadline_obj)

def save_to_database():
    db = get_db()
    db.universities.delete_many({"name": "GIKI"})
    db.deadlines.delete_many({"university_name": "GIKI"})
    db.universities.insert_one(basicinfo.dict())
    db.deadlines.insert_many([d.dict() for d in standalone_deadlines])

if __name__ == "__main__":
    save_to_database()
    print("GIKI data saved to database.")