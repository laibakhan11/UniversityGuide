import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.db import get_db
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline

url = "https://admission.lums.edu.pk/critical-dates-all-programmes"
r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")
deadlines = soup.find(id="quicktabs-tabpage-admissions-calendar-0")
UGdeadlines = deadlines.find_all("div", class_="col-custom views-row")
alldeadlines = []

for deadline in UGdeadlines:
    date = deadline.find("div", class_="views-field-field-activity-date")
    date = date.get_text(strip=True) if date else ""

    title_div = deadline.find("div", class_="views-field views-field-field-calendar-activity")
    title = title_div.find("div", class_="field-content").get_text(strip=True) if title_div else ""

    if title and date:
        alldeadlines.append({
            "title": title,
            "deadline_date": date
        })

lums = University(
    name="LUMS",
    full_name="Lahore University of Management Sciences",
    city="Lahore",
    address="DHA, Lahore Cantt. 54792, Lahore, Pakistan",
    website="https://lums.edu.pk",
    email="admissions@lums.edu.pk",
    admission_link="https://admission.lums.edu.pk",
    introduction="Lahore University of Management Sciences (LUMS), established in 1984, is Pakistan's most prestigious private university and is internationally recognized for academic excellence, research, and leadership development. It is most famous for its highly competitive admissions process, generous need-based financial aid program, and the renowned Suleman Dawood School of Business, which ranks among Asia's top business schools. LUMS offers undergraduate and graduate programs in business, economics, computer science, engineering, law, social sciences, and humanities. Located in Lahore, its 100-acre purpose-built campus hosts students from diverse socioeconomic backgrounds and promotes critical thinking, innovation, and interdisciplinary learning. LUMS graduates consistently secure top positions in multinational companies, global consulting firms, tech giants, and policy institutions.",
    programs=[
        # Business School Programs
        Program(
            name="BSc (Honours) Accounting and Finance",
            department="Suleman Dawood School of Business",
            total_fee_first_year=1706860,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Management Science",
            department="Suleman Dawood School of Business",
            total_fee_first_year=1706860,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),

        # Humanities & Social Sciences Programs
        Program(
            name="BA (Honours) English",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BA (Honours) History",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Anthropology and Sociology",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Economics",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Economics and Mathematics (Joint Major)",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Economics, Data and Computer Science (Joint Major)",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Psychology",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Political Science",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BSc (Honours) Politics and Economics",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
        Program(
            name="BA (Honours) Comparative Literature and Creative Arts",
            department="Mushtaq Ahmad Gurmani School of Humanities & Social Sciences",
            total_fee_first_year=1665160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),

        # Science & Engineering Programs
        Program(
            name="BSc (Honours) Biology",
            department="Syed Babar Ali School of Science and Engineering",
            total_fee_first_year=1998760,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=70.0,
                entry_test="SAT / ACT / LCAT",
                notes="FSc Pre-Medical or Pre-Engineering. O/A-Levels with science subjects"
            )
        ),
        Program(
            name="BSc (Honours) Chemistry",
            department="Syed Babar Ali School of Science and Engineering",
            total_fee_first_year=1998760,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=70.0,
                entry_test="SAT / ACT / LCAT",
                notes="FSc Pre-Engineering. O/A-Levels with science subjects"
            )
        ),
        Program(
            name="BSc (Honours) Chemical Engineering",
            department="Syed Babar Ali School of Science and Engineering",
            total_fee_first_year=1998760,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=70.0,
                entry_test="SAT / ACT / LCAT",
                notes="FSc Pre-Engineering. O/A-Levels with science subjects"
            )
        ),
        Program(
            name="BSc (Honours) Computer Science",
            department="Syed Babar Ali School of Science and Engineering",
            total_fee_first_year=1998760,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=70.0,
                entry_test="SAT / ACT / LCAT",
                notes="FSc Pre-Engineering or ICS. O/A-Levels with science/math subjects"
            )
        ),
        Program(
            name="BSc (Honours) Electrical Engineering",
            department="Syed Babar Ali School of Science and Engineering",
            total_fee_first_year=1998760,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=70.0,
                entry_test="SAT / ACT / LCAT",
                notes="FSc Pre-Engineering. O/A-Levels with science subjects"
            )
        ),
        Program(
            name="BSc (Honours) Mathematics",
            department="Syed Babar Ali School of Science and Engineering",
            total_fee_first_year=1998760,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=70.0,
                entry_test="SAT / ACT / LCAT",
                notes="FSc Pre-Engineering or ICS. O/A-Levels with math subjects"
            )
        ),
        Program(
            name="BSc (Honours) Physics",
            department="Syed Babar Ali School of Science and Engineering",
            total_fee_first_year=1998760,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=70.0,
                entry_test="SAT / ACT / LCAT",
                notes="FSc Pre-Engineering. O/A-Levels with science subjects"
            )
        ),

        # Law School
        Program(
            name="BA-LL.B (Honours)",
            department="Shaikh Ahmad Hassan School of Law",
            total_fee_first_year=1668160,
            eligibility=Eligibility(
                min_percentage_matric=70.0,
                min_percentage_inter=65.0,
                entry_test="SAT / ACT / LCAT",
                notes="O/A-Levels: B average in 8 O-Level subjects, 2Bs+1C in A-Levels"
            )
        ),
    ],

    scholarships=[
        Scholarship(
            name="LUMS Financial Aid",
            type="need-based",
            link="https://financial-aid.lums.edu.pk/financial-aid-options-fa"
        ),
        Scholarship(
            name="National Outreach Programme (NOP)",
            type="need-based",
            link="https://financial-aid.lums.edu.pk/national-outreach-programme"
        ),
        Scholarship(
            name="LUMS - PHEC Honhaar Scholarship",
            type="need-based",
            link="https://financial-aid.lums.edu.pk/honhaar-scholarship"
        ),
        Scholarship(
            name="LUMS - Sekha Scholarship",
            type="merit",
            link="https://sbasse.lums.edu.pk/sekha-scholarship"
        ),
        Scholarship(
            name="LUMS - Punjab Educational Endowment Fund (PEEF)",
            type="need-based",
            link="https://financial-aid.lums.edu.pk/"
        ),
        Scholarship(
            name="Shahid Hussain Foundation Scholarships for International Students",
            type="merit",
            link="https://financial-aid.lums.edu.pk/international-students-scholarship"
        ),
    ],

    deadlines=[
        EmbeddedDeadline(
            title=d["title"],
            deadline_date=d["deadline_date"]
        ) for d in alldeadlines
    ]
)


def save_to_database():
    db = get_db()

    db.universities.delete_many({"name": "LUMS"})
    db.deadlines.delete_many({"university_name": "LUMS"})

    db.universities.insert_one(lums.model_dump())

    for d in alldeadlines:
        deadline_obj = Deadline(
            university_name="LUMS",
            title=d["title"],
            deadline_date=d["deadline_date"],
        )
        db.deadlines.insert_one(deadline_obj.model_dump())

    print("LUMS data saved successfully")


if __name__ == "__main__":
    save_to_database()