import requests
from bs4 import BeautifulSoup
from pudata import University, Program, Eligibility, Scholarship, EmbeddedDeadline, collection

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
    notes=(
        "Applicants must have 12–13 years of formal education with a maximum of one gap year. "
        "Accepted qualifications include Matric & Intermediate, American High School Diploma, "
        "International Baccalaureate, and GCE O/A Levels with IBCC equivalence of at least 60%. "
        "Art aptitude test is mandatory for BFA programs."
    )
)

container_div = soup.select_one("section.inner-page .col-lg-9")
if container_div:
    departments = container_div.find_all("h3", class_="custom_degree_headings")
    for dept in departments:
        department_name = dept.get_text(strip=True)
        sibling = dept.find_next_sibling()
        while sibling and sibling.name != "h3":
            for a_tag in sibling.find_all("a"):
                program_name = a_tag.get_text(strip=True)
                prog_obj = Program(
                    name=program_name,
                    department=department_name,
                    fee_per_semester=None,
                    total_fee_first_year=None,
                    eligibility=lse_eligibility,
                    notes=""
                )
                program_objects.append(prog_obj)
            sibling = sibling.find_next_sibling()

# Scrape Deadlines
deadline_url = "https://lahoreschoolofeconomics.edu.pk/getProgramsAdmission/1"
deadline_response = requests.get(deadline_url)
deadline_soup = BeautifulSoup(deadline_response.text, "html.parser")

lse_deadlines = []
table = deadline_soup.find("table", class_="custom_table_class table")
if table:
    tbody = table.find("tbody")
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            title_span = tds[0].find("span").find("span")
            date_span = tds[1].find("span").find("span")
            title = title_span.get_text(strip=True)
            date = date_span.get_text(strip=True)
            print(f"{title} → {date}")
            lse_deadlines.append(EmbeddedDeadline(title=title, deadline_date=date))

# Scholarships
lse_scholarships = [
    Scholarship(name="LSE Need Based Scholarship", type="Need-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1"),
    Scholarship(name="Undergraduate Major Merit Scholarship", type="Merit-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1"),
    Scholarship(name="Undergraduate Minor Merit Scholarship", type="Merit-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1"),
    Scholarship(name="Student TA Ships", type="Merit-Based", link="https://lahoreschoolofeconomics.edu.pk/getProgramsScholarship/1")
]

# Scrape Fee Structure
fee_url = "https://www.eduvision.edu.pk/lahore-school-of-economics-lse-lahore-ins-60"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
fee_response = requests.get(fee_url, headers=headers)
fee_soup = BeautifulSoup(fee_response.text, "html.parser")

fee_table = fee_soup.find("table")
if fee_table:
    tbody = fee_table.find("tbody", class_="para")
    fees_by_department = {}
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 3:
            program_tag = tds[0].find("a")
            program_name = program_tag.get_text(strip=True) if program_tag else tds[0].get_text(strip=True)
            program_fee_str = tds[2].get_text(strip=True).replace(",", "")
            try:
                program_fee = int(program_fee_str)
            except ValueError:
                program_fee = None

            # Determine department from program name only if needed
            # Otherwise we assign fees directly by department later
            if program_fee:
                # Attempt to find the department in the existing programs
                for prog in program_objects:
                    if prog.department in program_name or prog.department.lower() in program_name.lower():
                        fees_by_department[prog.department] = program_fee

            print(f"Scraped Fee: {program_name} → {program_fee}")

# Assign Fee to Program Objs
print("\nAssigned Fees to Programs:\n")
for prog in program_objects:
    fee = fees_by_department.get(prog.department)
    if fee:
        prog.fee_per_semester = fee
        prog.total_fee_first_year = fee * 4
    else:
        prog.fee_per_semester = None
        prog.total_fee_first_year = None
    print(f"{prog.name} ({prog.department}) → Fee per semester: {prog.fee_per_semester}, Total fee/year: {prog.total_fee_first_year}")

lse_data = University(
    name="LSE",
    full_name="Lahore School Of Economics",
    city="Lahore",
    address="GF2F+XXW, Barki Rd, Sector P Phase 7, Lahore, 54000",
    website="https://www.lahoreschoolofeconomics.edu.pk/",
    email="mahjabeen@lahoreschool.edu.pk",
    admission_link="https://admissions.lahoreschool.edu.pk/",
    application_fee=None,
    programs=program_objects,
    scholarships=lse_scholarships,
    deadlines=lse_deadlines
)

result = collection.replace_one(
    {"name": lse_data.name},
    lse_data.dict(),
    upsert=True
)

if result.matched_count > 0:
    print("\nUniversity programs updated with fees in the database.")
else:
    print("\nUniversity document inserted with fees in the database.")

print("Eligibility assigned")
