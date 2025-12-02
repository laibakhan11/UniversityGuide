import requests
from bs4 import BeautifulSoup
import sys
import os
requests.packages.urllib3.disable_warnings()
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_db
from models.university import University, EmbeddedDeadline
from models.deadline import Deadline

print("COMSATS Lahore deadlines scrapping")

url = "https://lahore.comsats.edu.pk/admissions/admissions-schedule.aspx"

response = requests.get(url, verify=False)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")
alldeadlines = []

if table:
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            title = cols[0].get_text(strip=True)
            date = cols[1].get_text(strip=True)
            if title and date and "Activity" not in title and "Date" not in title:
                alldeadlines.append({
                    "title": title,
                    "deadline_date": date
                })

print(f"\n{len(alldeadlines)} deadlines found:")
for d in alldeadlines:
    print(f"• {d['title']} → {d['deadline_date']}")

comsats_university = University(
    name="COMSATS Lahore",
    full_name="COMSATS University Islamabad - Lahore Campus",
    city="Lahore",
    address="Defence Road, Off Raiwind Road, Lahore, Pakistan",
    website="https://lahore.comsats.edu.pk",
    email="admissions@cuilahore.edu.pk",
    admission_link=url,
    application_fee=None,
    programs=[],
    scholarships=[],
    deadlines=[
        EmbeddedDeadline(title=d["title"], deadline_date=d["deadline_date"])
        for d in alldeadlines
    ]
)

db = get_db()

db.universities.delete_many({"name": "COMSATS Lahore"})
db.deadlines.delete_many({"university_name": "COMSATS Lahore"})

db.universities.insert_one(comsats_university.model_dump())

for d in alldeadlines:
    deadline_doc = Deadline(
        university_name="COMSATS Lahore",
        title=d["title"],
        deadline_date=d["deadline_date"],
        url=url
    )
    db.deadlines.insert_one(deadline_doc.model_dump())

print("\nCOMSATS Lahore successfully saved to cloud database!")
print(f"Total universities in DB: {db.universities.count_documents({})}")