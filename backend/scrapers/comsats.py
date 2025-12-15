import requests
from bs4 import BeautifulSoup
import sys
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import get_db
from models.university import University, EmbeddedDeadline, Scholarship, Eligibility, Program
from models.deadline import Deadline

print("COMSATS Lahore scraping started...")


def get_department(program_name: str) -> str:
    name = program_name.lower()

    if any(x in name for x in ["computer science", "software", "artificial intelligence"]):
        return "Department of Computer Sciences"
    if any(x in name for x in ["business", "accounting", "finance", "data analytics"]):
        return "Department of Management Sciences"
    if "economics" in name:
        return "Department of Economics"
    if "chemistry" in name:
        return "Department of Chemistry"
    if "physics" in name:
        return "Department of Physics"
    if "mathematics" in name or "statistics" in name:
        return "Department of Mathematics"
    if "pharmacy" in name or "pharm d" in name:
        return "Department of Pharmacy"
    if "chemical engineering" in name:
        return "Department of Chemical Engineering"
    if "electrical engineering" in name or "computer engineering" in name:
        return "Department of Electrical Engineering"
    if any(x in name for x in ["architecture", "design", "interior"]):
        return "Department of Architecture and Design"
    if any(x in name for x in ["english", "media", "psychology"]):
        return "Department of Humanities"

    return "Unknown Department"



url = "https://lahore.comsats.edu.pk/admissions/admissions-schedule.aspx"
response = requests.get(url, verify=False)
soup = BeautifulSoup(response.text, "html.parser")

alldeadlines = []
table = soup.find("table")

if table:
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            title = cols[0].get_text(strip=True)
            date = cols[1].get_text(strip=True)

            if title and date and title.lower() not in ["activity", "date"]:
                alldeadlines.append(
                    EmbeddedDeadline(title=title, deadline_date=date)
                )


scholarships = []
r = requests.get(
    "https://lahore.comsats.edu.pk/admissions/scholarships-financial-aid.aspx",
    verify=False
)
soup = BeautifulSoup(r.text, "html.parser")

ul = soup.find("ul", class_="list list-icons list-icons-sm ms-4")
if ul:
    for li in ul.find_all("li"):
        title = li.get_text(strip=True)
        a_tag = li.find("a")
        link = a_tag["href"] if a_tag else None

        title_lower = title.lower()
        if "merit" in title_lower:
            sch_type = "merit"
        elif any(w in title_lower for w in ["need", "aid", "loan", "benevolent", "endowment"]):
            sch_type = "need"
        else:
            sch_type = "unknown"

        scholarships.append(
            Scholarship(name=title, type=sch_type, link=link)
        )



r = requests.get(
    "https://lahore.comsats.edu.pk/admissions/undergraduate.aspx",
    verify=False
)
soup = BeautifulSoup(r.text, "html.parser")

table = soup.find("table")
rows = table.find_all("tr") if table else []

programs = []
admission_fee = 22000

for row in rows:
    cells = row.find_all("td")
    if len(cells) == 3:
        program_name = cells[0].get_text(strip=True)
        spring_offered = "Yes" if cells[1].find("i") else "No"
        fall_offered = "Yes" if cells[2].find("i") else "No"

        department = get_department(program_name)
        if department == "Department of Computer Sciences":
            fee_per_semester = 146000
            second_sem_fee = 160500
        elif department == "Department of Pharmacy":
            fee_per_semester = 143500
            second_sem_fee = 143500
        else:
            fee_per_semester = 135000
            second_sem_fee = 148500

        total_fee_first_year = admission_fee + fee_per_semester + second_sem_fee


        if department == "Department of Pharmacy":
            eligibility = Eligibility(
                min_percentage_matric=50.0,
                min_percentage_inter=60.0,
                entry_test="NTS test",
                notes="Intermediate (Medical group) required."
            )

        elif department == "Department of Computer Sciences":
            eligibility = Eligibility(
                min_percentage_matric=50.0,
                min_percentage_inter=50.0,
                entry_test="NTS test",
                notes="Intermediate with Mathematics or Pre-Medical (Math deficiency required)."
            )

        elif department == "Department of Electrical Engineering":
            eligibility = Eligibility(
                min_percentage_matric=50.0,
                min_percentage_inter=50.0,
                entry_test="NTS test",
                notes="Intermediate with Mathematics required."
            )

        else:
            eligibility = Eligibility(
                min_percentage_matric=50.0,
                min_percentage_inter=50.0,
                entry_test="NTS test",
                notes=""
            )

        programs.append(
            Program(
                name=program_name,
                department=department,
                fee_per_semester=fee_per_semester,
                total_fee_first_year=total_fee_first_year,
                eligibility=eligibility,
                notes=(
                    f"Offered in Spring: {spring_offered}, Fall: {fall_offered}. "
                    "Admission fee included. Fees are tentative."
                )
            )
        )


db = get_db()

db.universities.delete_many({"name": "COMSATS Lahore"})
db.deadlines.delete_many({"university_name": "COMSATS Lahore"})

comsats_university = University(
    name="COMSATS Lahore",
    full_name="COMSATS University Islamabad - Lahore Campus",
    city="Lahore",
    address="Defence Road, Off Raiwind Road, Lahore, Pakistan",
    website="https://lahore.comsats.edu.pk",
    email="admissions@cuilahore.edu.pk",
    admission_link=url,
    programs=programs,
    scholarships=scholarships,
    deadlines=alldeadlines
)

db.universities.insert_one(comsats_university.dict())

for d in alldeadlines:
    db.deadlines.insert_one(
        Deadline(
            university_name="COMSATS Lahore",
            title=d.title,
            deadline_date=d.deadline_date,
            url=url
        ).dict()
    )

print("COMSATS Lahore saved successfully!")

