import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pudata import University, Program, Scholarship, EmbeddedDeadline, Eligibility

# ---------------- MongoDB Connection ----------------
client = MongoClient("mongodb://localhost:27017/")
try:
    client.admin.command("ismaster")
    print("Connected to MongoDB successfully (IBA)")
except ConnectionFailure:
    print("Failed to connect to MongoDB (IBA)")
    exit()

db = client["university_db"]
collection = db["universities"]

# ---------------- Department mappings ----------------
department_keywords = {
    "Accounting & Finance": ["accounting", "finance"],
    "Accounting & Law": ["accounting & finance", "law", "accounting & law"],
    "Economics": ["economics"],
    "Finance": ["business analytics", "finance"],
    "Management": ["bba", "management"],
    "Marketing": ["marketing"],
    "Social Sciences & Liberal Arts": ["social sciences", "liberal arts"],
    "Computer Sciences": ["computer science"],
    "Mathematical Sciences": ["mathematics", "mathematical sciences"]
}

# ---------------- Scholarship dictionary ----------------
scholarship_dict = {
    "Punjab Educational Endowment Fund (PEEF) for the academic year 2025-26": {
        "type": "Need-based",
        "link": "https://www.iba.edu.pk/financialassistance/punjab-educational-endowment-fund2025-26.php"
    },
    "Sindh Educational Endowment Fund (SEEF) Trust Scholarship": {
        "type": "Need & Merit-based",
        "link": "https://form-seef.com/"
    },
    "IBA Need Based Financial Assistance": {
        "type": "Need-based",
        "link": "https://www.iba.edu.pk/financialassistance/needbased.php"
    }
}

# ---------------- Eligibility dictionary ----------------
eligibility_dict = {
    "BBA": Eligibility(
        min_percentage_matric=65.0,
        min_percentage_inter=65.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes=(
            "HSSC min 65% OR A Levels (2 B's, 1 C) OR American/Canadian High School Diploma (min 80%) "
            "OR International Baccalaureate (min 25/45). IBCC equivalency required."
        )
    ),
    "BS (Computer Science)": Eligibility(
        min_percentage_matric=60.0,
        min_percentage_inter=60.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC Pre-Engineering/General with Math OR A Levels (1 B, 2 C) including Math OR American/Canadian HS Diploma (min 80%) OR IB (min 24/45)."
    ),
    "BS (Economics & Mathematics)": Eligibility(
        min_percentage_matric=60.0,
        min_percentage_inter=60.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC Pre-Engineering/General with Math OR A Levels (1 B, 2 C) including Math OR American/Canadian HS Diploma (min 80%) OR IB (min 24/45)."
    ),
    "BS (Accounting & Finance)": Eligibility(
        min_percentage_matric=65.0,
        min_percentage_inter=65.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC any group min 65% OR A Levels (2 B's, 1 C) OR American/Canadian HS Diploma min 80% OR IB min 24/45."
    ),
    "BS (Social Sciences & Liberal Arts)": Eligibility(
        min_percentage_matric=60.0,
        min_percentage_inter=60.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC any group min 60% OR A Levels (1 B, 2 C) OR American/Canadian HS Diploma min 80% OR IB min 24/45."
    ),
    "BS (Economics)": Eligibility(
        min_percentage_matric=60.0,
        min_percentage_inter=60.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC any group min 60% OR A Levels (1 B, 2 C) OR American/Canadian HS Diploma min 80% OR IB min 24/45."
    ),
    "BS (Mathematics)": Eligibility(
        min_percentage_matric=60.0,
        min_percentage_inter=60.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="Mathematics background required at high school level. HSSC Pre-Engineering/General with Math OR A Levels (1 B, 2 C) OR American HS Diploma min 80% OR IB min 24/45."
    ),
    "BSBA (Business Analytics)": Eligibility(
        min_percentage_matric=65.0,
        min_percentage_inter=65.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC min 65% OR A Levels (2 B's, 1 C) OR American/Canadian HS Diploma min 80% OR IB min 25/45."
    ),
    "BS (Economics & Data Science)": Eligibility(
        min_percentage_matric=60.0,
        min_percentage_inter=60.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC Pre-Engineering/General with Math min 60% OR A Levels (1 B, 2 C) including Math OR American/Canadian HS Diploma min 80% OR IB min 24/45."
    ),
    "BSEDS": Eligibility(
        min_percentage_matric=60.0,
        min_percentage_inter=60.0,
        entry_test="IBA Aptitude Test (SAT-I level) or ACT",
        notes="HSSC Pre-Engineering/General with Math min 60% OR A Levels (1 B, 2 C) including Math OR American/Canadian HS Diploma min 80% OR IB min 24/45."
    )
}

# ---------------- Scrape Programs ----------------
URL_PROGRAMS = "https://www.iba.edu.pk/undergraduate.php"
headers = {"User-Agent": "Mozilla/5.0"}

print("Fetching IBA undergraduate programs page...")
response = requests.get(URL_PROGRAMS, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
main_div = soup.find("div", id="main")
uls = main_div.find_all("ul", class_="academic-programs")
programs_ul = uls[1]

iba_programs = []
for li in programs_ul.find_all("li"):
    img_tag = li.find("img")
    a_tag = li.find("a")
    span_tag = a_tag.find("span") if a_tag else None
    if not img_tag or not a_tag or not span_tag:
        continue

    program_name = span_tag.get_text(strip=True)
    dept_assigned = "TBD"
    for dept, keywords in department_keywords.items():
        if any(k.lower() in program_name.lower() for k in keywords):
            dept_assigned = dept
            break

    eligibility_obj = eligibility_dict.get(program_name, Eligibility(
        min_percentage_matric=0.0,
        min_percentage_inter=0.0,
        entry_test="TBD",
        notes=""
    ))

    program_obj = Program(
        name=program_name,
        department=dept_assigned,
        fee_per_semester=None,
        total_fee_first_year=None,
        eligibility=eligibility_obj,
        notes=""
    )
    iba_programs.append(program_obj)

print(f"Total programs scraped: {len(iba_programs)}")

# ---------------- Scrape Scholarships ----------------
URL_SCHOLARSHIPS = "https://www.iba.edu.pk/scholarships.php"
print("Fetching IBA scholarships page...")
response = requests.get(URL_SCHOLARSHIPS, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
ul = soup.find("ul", class_="iba-news iba-events")

scholarships = []
for li in ul.find_all("li"):
    a_tag = li.find("a")
    news_div = a_tag.find("div", class_="news-details") if a_tag else None
    h3_tag = news_div.find("h3") if news_div else None
    if not h3_tag:
        continue
    for strong in h3_tag.find_all("strong"):
        strong.decompose()
    scholarship_name = h3_tag.get_text(strip=True)
    if scholarship_name:
        s_type = scholarship_dict.get(scholarship_name, {}).get("type", "TBD")
        s_link = scholarship_dict.get(scholarship_name, {}).get("link", "#")
        scholarships.append(Scholarship(name=scholarship_name, type=s_type, link=s_link))

print(f"Total scholarships scraped: {len(scholarships)}")

# ---------------- Scrape Deadlines ----------------
URL_DEADLINES = "https://admissions.iba.edu.pk/admission-schedule-fall2025.php"
print("Fetching IBA admission schedule page...")
response = requests.get(URL_DEADLINES, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table", class_="w3-table w3-striped")
iba_deadlines = []

def extract_date(td):
    if not td:
        return None
    p = td.find("p")
    if not p:
        return None
    span = p.find("span")
    return span.get_text(strip=True) if span else None

for table_index, table in enumerate(tables, start=1):
    round_name = f"Round {table_index}"
    rows = table.find_all("tr")
    if len(rows) < 5:
        continue
    programs_row = rows[4]
    program_tds = programs_row.find_all("td")
    deadline_rows = rows[5:]

    for row in deadline_rows:
        tds = row.find_all("td")
        if not tds:
            continue
        strong = tds[0].find("strong")
        if not strong:
            continue
        title_text = " ".join(span.get_text(strip=True) for span in strong.find_all("span"))
        if not title_text.strip():
            continue
        full_title = f"{title_text} - {round_name}"

        date_columns = [1, 5, 7] if table_index == 1 else [1, 3, 5]
        deadline_text_parts = []
        date_counter = 1

        for col_index in date_columns:
            if col_index >= len(tds) or col_index >= len(program_tds):
                continue
            date_value = extract_date(tds[col_index])
            if not date_value:
                continue
            programs = program_tds[col_index].get_text(" ", strip=True)
            deadline_text_parts.append(f"Date {date_counter}: {date_value}\n       Programs: {programs}")
            date_counter += 1

        if deadline_text_parts:
            deadline_date_string = "\n".join(deadline_text_parts)
            iba_deadlines.append(EmbeddedDeadline(title=full_title, deadline_date=deadline_date_string))

print(f"Total deadlines scraped: {len(iba_deadlines)}")

# ---------------- Insert University Data ----------------
collection.delete_many({"name": "IBA Karachi"})

iba_data = University(
    name="IBA Karachi",
    full_name="Institute of Business Administration, Karachi",
    city="Karachi",
    address="University Road, Karachi, Pakistan",
    website="https://www.iba.edu.pk",
    email="admissions@iba.edu.pk",
    admission_link="https://admissions.iba.edu.pk",
    application_fee=None,
    programs=iba_programs,
    scholarships=scholarships,
    deadlines=iba_deadlines
)

try:
    insert_result = collection.insert_one(iba_data.dict())
    print(f"Inserted IBA document successfully. Programs: {len(iba_programs)}, Scholarships: {len(scholarships)}, Deadlines: {len(iba_deadlines)}, Document ID: {insert_result.inserted_id}")
except Exception as e:
    print("Error inserting IBA document:", e)
