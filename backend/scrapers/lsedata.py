import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.db import get_db
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# STEP 1: DELETE EXISTING LSE DATA FROM BOTH COLLECTIONS
db = get_db()

# Delete from universities collection
uni_collection = db["universities"]
uni_delete_result = uni_collection.delete_one({"name": "LSE"})

# Delete from deadlines collection
deadline_collection = db["deadlines"]
deadline_delete_result = deadline_collection.delete_many({"university_name": "LSE"})

# Scrape Programs
program_url = "https://lahoreschoolofeconomics.edu.pk/getAcademicProgramsListings/1"
response = requests.get(program_url)
soup = BeautifulSoup(response.text, "html.parser")

program_objects = []

# Eligibility Object (shared for all programs)
lse_eligibility = Eligibility(
    min_percentage_matric=60.0,
    min_percentage_inter=60.0,
    entry_test="SAT I (min 1200/1600, Math ≥600) OR LSE Entrance Exam + Interview",
    notes="Applicants must have 12–13 years of formal education with a maximum of one gap year. Accepted qualifications include Matric & Intermediate, American High School Diploma, International Baccalaureate, and GCE O/A Levels with IBCC equivalence of at least 60%. Art aptitude test is mandatory for BFA programs."
)

# Find the main container
container_div = soup.select_one("section.inner-page .col-lg-9")
if container_div:
    # Find all h3 department headings
    departments = container_div.find_all("h3", class_="custom_degree_headings")
    
    for dept_h3 in departments:
        # Clean department name
        department_name = dept_h3.get_text(strip=True)
        
        dept_programs = []
        
        # Get all siblings until the next h3
        current = dept_h3.find_next_sibling()
        
        while current:
            # Check if current itself is an h3 heading
            if current.name == "h3" and "custom_degree_headings" in current.get("class", []):
                break
            
            # Look for program links in this sibling
            if current.name == "div" and "row" in current.get("class", []):
                # Find all columns
                cols = current.find_all("div", class_="col-sm-6", recursive=False)
                for col in cols:
                    # Check if this col contains an h3 (next department marker)
                    if col.find("h3", class_="custom_degree_headings"):
                        break
                    
                    # Find links in this column only
                    links = col.find_all("a", href=lambda x: x and "getAcademicDegree" in x)
                    for link in links:
                        program_name = link.get_text(strip=True)
                        if program_name and program_name not in dept_programs:
                            dept_programs.append(program_name)
                            prog_obj = Program(
                                name=program_name,
                                department=department_name,
                                fee_per_semester=None,
                                total_fee_first_year=None,
                                eligibility=lse_eligibility,
                                notes=""
                            )
                            program_objects.append(prog_obj)
            
            # Check if this element contains an h3 (next department)
            next_dept_heading = current.find("h3", class_="custom_degree_headings")
            if next_dept_heading:
                break
            
            current = current.find_next_sibling()

# Scrape Deadlines
deadline_url = "https://lahoreschoolofeconomics.edu.pk/getProgramsAdmission/1"
deadline_response = requests.get(deadline_url)
deadline_soup = BeautifulSoup(deadline_response.text, "html.parser")

lse_deadlines = []
table = deadline_soup.find("table", class_="custom_table_class table")
if table:
    tbody = table.find("tbody")
    if tbody:
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 2:
                try:
                    title_span = tds[0].find("span")
                    date_span = tds[1].find("span")
                    if title_span and date_span:
                        title_inner = title_span.find("span")
                        date_inner = date_span.find("span")
                        title = title_inner.get_text(strip=True) if title_inner else title_span.get_text(strip=True)
                        date = date_inner.get_text(strip=True) if date_inner else date_span.get_text(strip=True)
                        lse_deadlines.append(EmbeddedDeadline(title=title, deadline_date=date))
                except:
                    pass

# Scholarships
lse_scholarships = [
    Scholarship(name="LSE Need Based Scholarship", type="Need-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1", notes=""),
    Scholarship(name="Undergraduate Major Merit Scholarship", type="Merit-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1", notes=""),
    Scholarship(name="Undergraduate Minor Merit Scholarship", type="Merit-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1", notes=""),
    Scholarship(name="Student TA Ships", type="Merit-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1", notes="")
]

# Scrape Fee Structure
fee_url = "https://www.eduvision.edu.pk/lahore-school-of-economics-lse-lahore-ins-60"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
fee_response = requests.get(fee_url, headers=headers)
fee_soup = BeautifulSoup(fee_response.text, "html.parser")

default_fee = 341000

fee_table = fee_soup.find("table")
if fee_table:
    tbody = fee_table.find("tbody", class_="para")
    if tbody and tbody.find_all("tr"):
        first_tr = tbody.find("tr")
        if first_tr:
            tds = first_tr.find_all("td")
            if len(tds) >= 3:
                program_fee_str = tds[2].get_text(strip=True).replace(",", "")
                try:
                    default_fee = int(program_fee_str)
                except ValueError:
                    pass

# Assign uniform fee to all programs
for prog in program_objects:
    prog.fee_per_semester = default_fee
    prog.total_fee_first_year = default_fee * 4

# Create University object
lse_data = University(
    name="LSE",
    full_name="Lahore School Of Economics",
    city="Lahore",
    address="GF2F+XXW, Barki Rd, Sector P Phase 7, Lahore, 54000",
    website="https://www.lahoreschoolofeconomics.edu.pk/",
    email="mahjabeen@lahoreschool.edu.pk",
    admission_link="https://admissions.lahoreschool.edu.pk/",
    introduction="Lahore School of Economics (LSE), established in 1993, is Pakistan's premier institution for economics, finance, and social sciences education. It is famous for producing top economists, policy analysts, and development professionals working in government, international organizations, and financial institutions. LSE offers undergraduate and graduate programs in economics, finance, business administration, and social sciences. Located in Lahore, the university emphasizes analytical thinking, research methodology, and small interactive classes. Its rigorous academic environment and highly qualified faculty make it a leading choice for students interested in economics and public policy careers.",
    programs=program_objects,
    scholarships=lse_scholarships,
    deadlines=lse_deadlines
)

# Save to database - universities collection
result = uni_collection.insert_one(lse_data.dict())

# Save to deadlines collection (separate deadline documents)
for deadline in lse_deadlines:
    deadline_doc = {
        "university_name": "LSE",
        "title": deadline.title,
        "deadline_date": deadline.deadline_date,
        "url": ""
    }
    deadline_collection.insert_one(deadline_doc)