from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime

# --- Pydantic Models ---
class Eligibility(BaseModel):
    min_percentage_matric: float
    min_percentage_inter: float
    entry_test: str
    notes: Optional[str] = ""

class Program(BaseModel):
    name: str
    department: Optional[str] = ""
    fee_per_semester: Optional[int] = None
    total_fee_first_year: Optional[int] = None
    eligibility: Eligibility
    notes: Optional[str] = ""

class Scholarship(BaseModel):
    name: str
    type: str
    link: Optional[str] = ""

class EmbeddedDeadline(BaseModel):
    title: str
    deadline_date: str

class University(BaseModel):
    name: str
    full_name: str
    city: str
    address: Optional[str] = ""
    website: str
    email: str
    admission_link: str
    application_fee: Optional[int] = None
    programs: List[Program] = []
    scholarships: List[Scholarship] = []
    deadlines: List[EmbeddedDeadline] = []

# --- MongoDB Connection ---
client = MongoClient("mongodb://localhost:27017/")
try:
    client.admin.command('ismaster')
    print("Connected to MongoDB successfully")
except ConnectionFailure:
    print("Failed to connect to MongoDB")

db = client['university_db']
collection = db['universities']


pu_programs = [
#  Quaid-i-Azam Campus
# --- Faculty of Agricultural Sciences (Morning/Replica -> Regular/Self-Supporting) ---
Program(name="B.Sc. (Hons.) Agriculture (Agronomy) (Regular)", department="Department of Agronomy", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Agriculture (Agronomy) (Self-Supporting)", department="Department of Agronomy", fee_per_semester=61600, total_fee_first_year=123200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Agriculture (Entomology) (Regular)", department="Department of Entomology", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Agriculture (Entomology) (Self-Supporting)", department="Department of Entomology", fee_per_semester=61600, total_fee_first_year=123200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Food Science and Technology (Self-Supporting)", department="Department of Food Sciences", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Food Science and Technology (Regular)", department="Department of Food Sciences", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Agriculture (Horticulture) (Regular)", department="Department of Horticulture", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Agriculture (Horticulture) (Self-Supporting)", department="Department of Horticulture", fee_per_semester=61600, total_fee_first_year=123200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Agriculture (Plant Pathology) (Regular)", department="Department of Plant Pathology", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Hons.) Agriculture (Plant Pathology) (Self-Supporting)", department="Department of Plant Pathology", fee_per_semester=61600, total_fee_first_year=123200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-GS'), notes="Offered in Quaid-i-Azam Campus"),

# --- Faculty of Arts and Humanities / Social Sciences (Standardizing Names) ---
Program(name="BS Archaeology (4 Years) (Regular)", department="Department of Archaeology", fee_per_semester=22450, total_fee_first_year=44900, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS French (Regular)", department="Department of French", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS History (Regular)", department="Department of History & Pakistan Studies", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Pakistan Studies (1st Semester) (Self-Supporting)", department="Department of History & Pakistan Studies", fee_per_semester=43000, total_fee_first_year=86000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Philosophy 1st Semester (Regular)", department="Department of Philosophy", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Philosophy 1st Semester (Self-Supporting)", department="Department of Philosophy", fee_per_semester=43000, total_fee_first_year=86000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Physical Education (4 Years) (Regular)", department="Department of Sports Sciences & Physical Education", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS English (Literature) (Self-Supporting)", department="Institute of English Studies", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS English (Literature) (Regular)", department="Institute of English Studies", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Clinical Psychology (Regular)", department="Centre for Clinical Psychology", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Clinical Psychology (Self-Supporting)", department="Centre for Clinical Psychology", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (Hons) Gender Studies (Regular)", department="Department of Gender Studies", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (Hons) Gender Studies (Self-Supporting)", department="Department of Gender Studies", fee_per_semester=43000, total_fee_first_year=86000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Gender and Climate Change (Regular)", department="Department of Gender Studies", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Gender and Climate Change (Self-Supporting)", department="Department of Gender Studies", fee_per_semester=43000, total_fee_first_year=86000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Political Science (4 Years) (Regular)", department="Department of Political Science", fee_per_semester=22450, total_fee_first_year=44900, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS International Relations (4 Years) (Self-Supporting)", department="Department of Political Science", fee_per_semester=49500, total_fee_first_year=99000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Social Work (Self-Supporting)", department="Department of Social Work", fee_per_semester=49500, total_fee_first_year=99000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Social Work (Regular)", department="Department of Social Work", fee_per_semester=22450, total_fee_first_year=44900, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Social Entrepreneurship (Regular)", department="Department of Social Work", fee_per_semester=22450, total_fee_first_year=44900, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Social Entrepreneurship (Self-Supporting)", department="Department of Social Work", fee_per_semester=49500, total_fee_first_year=99000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-years.) in Applied Psychology (Regular)", department="Institute of Applied Psychology", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-years.) in Applied Psychology (Self-Supporting)", department="Institute of Applied Psychology", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Years) Sociology (Regular)", department="Institute of Social & Cultural Studies", fee_per_semester=22450, total_fee_first_year=44900, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Years) Sociology (Self-Supporting)", department="Institute of Social & Cultural Studies", fee_per_semester=49500, total_fee_first_year=99000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Years) Criminology (Regular)", department="Institute of Social & Cultural Studies", fee_per_semester=22450, total_fee_first_year=44900, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Years) Criminology (Self-Supporting)", department="Institute of Social & Cultural Studies", fee_per_semester=49500, total_fee_first_year=99000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Years) Demography (Self-Supporting)", department="Institute of Social & Cultural Studies", fee_per_semester=49500, total_fee_first_year=99000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Years) Demography (Regular)", department="Institute of Social & Cultural Studies", fee_per_semester=22450, total_fee_first_year=44900, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),

# --- Faculty of Business, Economics and Administrative Sciences (Standardizing Names) ---
Program(name="B.S. Management (Regular)", department="Institute of Administrative Sciences", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.S. Management (Self-Supporting)", department="Institute of Administrative Sciences", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Management 5th Semester - Lateral Entry (Regular)", department="Institute of Administrative Sciences", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Management 5th Semester - Lateral Entry (Self-Supporting)", department="Institute of Administrative Sciences", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BBIT (Hons.) (Regular)", department="Institute of Business & Information Technology", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BBA (Hons.) (Regular)", department="Institute of Business Administration (IBA)", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BBA (Hons.) (Self-Supporting)", department="Institute of Business Administration (IBA)", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Yrs) Economics (Regular)", department="School of Economics", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS (4-Yrs) Economics (Self-Supporting)", department="School of Economics", fee_per_semester=61600, total_fee_first_year=123200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Business Economics (Regular)", department="Department of Business Economics", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),

# --- Faculty of Engineering & Technology (Consolidating Old/New to Regular) ---
Program(name="B.Sc. (Engg) Chemical Engineering (Regular)", department="Institute of Chemical Engineering & Technology", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-E'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc. (Engg) Chemical Engineering with Specialization in Petroleum & Gas (Regular)", department="Institute of Chemical Engineering & Technology", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-E'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc (Engg.) Metallurgy & Materials Engineering (Regular)", department="Institute of Metallurgy & Materials Engineering", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-E'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Sc (Engg.) Metallurgy & Materials Engineering (Self-Supporting)", department="Institute of Metallurgy & Materials Engineering", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-E'), notes="Offered in Quaid-i-Azam Campus"),

# --- Faculty of Commerce (Standardizing Names) ---
Program(name="BS Commerce (Regular)", department="Hailey College of Commerce", fee_per_semester=27225, total_fee_first_year=54450, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS E-Commerce (Regular)", department="Hailey College of Commerce", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Commerce (Self-Supporting)", department="Hailey College of Commerce", fee_per_semester=43000, total_fee_first_year=86000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Accounting and Finance (Regular)", department="Hailey College of Commerce", fee_per_semester=41800, total_fee_first_year=83600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Accounting and Finance (Self-Supporting)", department="Hailey College of Commerce", fee_per_semester=61600, total_fee_first_year=123200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS E-Commerce (Self-Supporting)", department="Hailey College of Commerce", fee_per_semester=55000, total_fee_first_year=110000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Accounting and Taxation (Regular)", department="Hailey College of Commerce", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Accounting and Taxation (Self-Supporting)", department="Hailey College of Commerce", fee_per_semester=55000, total_fee_first_year=110000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Quaid-i-Azam Campus"),

# --- Faculty of Education (Standardizing Names) ---
Program(name="B.Ed (1.5 Year) (Regular)", department="Institute of Education & Research", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.Ed (1.5 Year) (Self-Supporting)", department="Institute of Education & Research", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Business Education (4 years) (Regular)", department="Department of Business Education", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Business Education (4 years) (Self-Supporting)", department="Department of Business Education", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.S Hons Elementary (4 years) Program (Regular)", department="Department of Elementary Education", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.S Hons Elementary (4 years) Program (Self-Supporting)", department="Department of Elementary Education", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.S.Ed (Hons) (Regular)", department="Department of Science Education", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="B.S.Ed (Hons) (Self-Supporting)", department="Department of Science Education", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Technology Education 1st Semester (Regular)", department="Department of Technology Education", fee_per_semester=32340, total_fee_first_year=64680, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),
Program(name="BS Technology Education 1st Semester (Self-Supporting)", department="Department of Technology Education", fee_per_semester=71500, total_fee_first_year=143000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Quaid-i-Azam Campus"),

#ALLAMA IQBAL CAMPUS
# --- Faculty of Arts and Humanities (College of Art & Design) ---
Program(name="B. Architecture (Regular)", department="Department of Architecture", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-E'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Fine Arts (Regular)", department="Department of Fine Arts", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Fine Arts (Self-Supporting)", department="Department of Fine Arts", fee_per_semester=78100, total_fee_first_year=156200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="Fine Arts AD Program (Regular)", department="Department of Fine Arts", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="Fine Arts AD Program (Self-Supporting)", department="Department of Fine Arts", fee_per_semester=78100, total_fee_first_year=156200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Graphic Arts (Print Making) (Regular)", department="Department of Graphic Arts (Printmaking)", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Graphic Arts (Print Making) (Self-Supporting)", department="Department of Graphic Arts (Printmaking)", fee_per_semester=78100, total_fee_first_year=156200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Graphic Design (Regular)", department="Department of Graphic Design", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Graphic Design (Self-Supporting)", department="Department of Graphic Design", fee_per_semester=78100, total_fee_first_year=156200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Performing Arts & Musicalogy (Regular)", department="Department of Performing Arts & Musicology", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Sculpture (Regular)", department="Department of Sculpture", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Sculpture (Self-Supporting)", department="Department of Sculpture", fee_per_semester=78100, total_fee_first_year=156200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Textile Design (Self-Supporting)", department="Department of Textile Design", fee_per_semester=78100, total_fee_first_year=156200, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BFA Textile Design (Regular)", department="Department of Textile Design", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),

# --- Faculty of Commerce (Hailey College of Banking & Finance) ---
Program(name="BBA (4-Years) Insurance & Risk Management (Regular)", department="Hailey College of Banking & Finance", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Allama Iqbal Campus"),
Program(name="BBA (4-Years) Insurance & Risk Management (Self-Supporting)", department="Hailey College of Banking & Finance", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Allama Iqbal Campus"),
Program(name="BBA (4-Years) Banking & Finance (Regular)", department="Hailey College of Banking & Finance", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Allama Iqbal Campus"),
Program(name="BBA (4-Years) Banking & Finance (Self-Supporting)", department="Hailey College of Banking & Finance", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-COM'), notes="Offered in Allama Iqbal Campus"),

# --- Faculty of Computing & Information Technology ---
Program(name="BS Computer Science (Regular)", department="Department of Computer Science", fee_per_semester=50000, total_fee_first_year=100000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Computer Science (Self-Supporting)", department="Department of Computer Science", fee_per_semester=120500, total_fee_first_year=241000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS (Data Science) (Regular)", department="Department of Data Science", fee_per_semester=50000, total_fee_first_year=100000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS (Data Science) (Self-Supporting)", department="Department of Data Science", fee_per_semester=120500, total_fee_first_year=241000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Cyber Security (Regular)", department="Department of Data Science", fee_per_semester=50000, total_fee_first_year=100000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Information Technology (IT) (Regular)", department="Department of Information Technology", fee_per_semester=50000, total_fee_first_year=100000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Artificial Intelligence (Regular)", department="Department of Information Technology", fee_per_semester=50000, total_fee_first_year=100000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Software Engineering (Regular)", department="Department of Software Engineering", fee_per_semester=50000, total_fee_first_year=100000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Software Engineering (Self-Supporting)", department="Department of Software Engineering", fee_per_semester=120500, total_fee_first_year=241000, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-CSP'), notes="Offered in Allama Iqbal Campus"),

# --- Faculty of Oriental Learning ---
Program(name="BS Kashmiryat (Regular)", department="Department of Kashmiriat", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS (Persian) (Regular)", department="Department of Persian", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Punjabi (Regular)", department="Institute of Punjabi and Cultural Studies", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),
Program(name="BS Urdu (Regular)", department="Institute of Urdu Language & Literature", fee_per_semester=19150, total_fee_first_year=38300, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-AHS'), notes="Offered in Allama Iqbal Campus"),

# --- Faculty of Pharmacy ---
Program(name="Pharm.D (Self-Supporting)", department="Punjab University College of Pharmacy", fee_per_semester=85800, total_fee_first_year=171600, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-M'), notes="Offered in Allama Iqbal Campus"),
Program(name="Pharm.D (Regular)", department="Punjab University College of Pharmacy", fee_per_semester=38900, total_fee_first_year=77800, eligibility=Eligibility(min_percentage_matric=33.0, min_percentage_inter=60.0, entry_test='PU-M'), notes="Offered in Allama Iqbal Campus")
]

pu_scholarships = [
    Scholarship(name="Honhaar Scholarships", type="Merit & Need-based", link="https://honhaarscholarship.punjabhec.gov.pk/"),
    Scholarship(name="Pakistan Bait-Ul-Mal Scholarship", type="Need-based", link="https://pu.edu.pk/images/image/Scholarships/Pakistan%20Bait%20ul%20Mal%20Scholarship.pdf"),
    Scholarship(name="HEC Need Based Scholarships", type="Need-based", link="https://pu.edu.pk/images/image/Scholarships/PEEF-HEC/1Application%20Form.pdf"),
    Scholarship(name="Fulbright Scholarship", type="Merit-based", link="https://pu.edu.pk/page/detail/fulbright_scholarship.html"),
    Scholarship(name="PEEF Special Quota Scholarship", type="Need-based", link="https://peef.org.pk/"),
    Scholarship(name="Scholarship for Students of GB", type="Area/Need-based", link="https://pu.edu.pk/images/image/Scholarships/Undergraduate-Scholarship_GB.jpg"),
    Scholarship(name="Pakistan Science Foundation Scholarship", type="Merit-based", link="https://pu.edu.pk/images/image/Scholarships/PSF.jpg"),
    Scholarship(name="Momina Cheema Foundation Need Based Scholarship", type="Need-based", link="https://pu.edu.pk/images/image/Scholarships/Momina%20Cheema%20Foundation%20Need%20Based%20Scholarship%20(Eligibility%20Criteria).pdf"),
    Scholarship(name="Allah Walay Trust Scholarship", type="Need-based", link="https://pu.edu.pk/images/image/Scholarships/Application%20Form%20for%20Scholarship%20(Allah%20Walay%20Trust).pdf"),
    Scholarship(name="Higher Education Commission Scholarships", type="Varies", link="https://pu.edu.pk/images/image/Scholarships/KNB%20Scholarship%202023.pdf"),
    Scholarship(name="Chinese Government Scholarship Programme", type="Merit-based", link="https://pu.edu.pk/page/show/Chinese-Govt-Scholarship.html"),
    Scholarship(name="Chevening Scholarships", type="Merit-based", link="https://pu.edu.pk/images/image/Scholarships/Chevening-Scholarships.pdf"),
    Scholarship(name="Zakat and Ushr Scholarship", type="Need-based", link="https://zakat.punjab.gov.pk/educationgeneral"),
    Scholarship(name="Advanced Education Program aep Scholarships", type="Varies", link="https://pu.edu.pk/images/image/Scholarships/Educational-Scholarships-for-Pakistani-Students.pdf"), 
    Scholarship(name="Central European University Scholarships", type="Varies/Merit-based", link="https://www.pbm.gov.pk/forms.html"),
    Scholarship(name="USAID Funded Merit and Need Based Scholarships", type="Merit & Need-based", link="https://usaidmnbsp-fas.hec.gov.pk/#/auth/login"),
]

# --- Create University Object ---
try:
    pu_data = University(
        name="PU",
        full_name="University of the Punjab, Lahore",
        city="Lahore",
        address="New Campus: F7H8+HFV, Canal Rd, Quaid-i-Azam Campus, Lahore | Old Campus: H895+MGV, Shahrah-e-Quaid-e-Azam, Anarkali Bazaar, Lahore",
        website="https://pu.edu.pk/#intro",
        email="infocell@pu.edu.pk",
        admission_link="https://pu.edu.pk//home/more/4",
        application_fee=None,  # Placeholder for missing fee
        programs=pu_programs,
        scholarships=pu_scholarships,
        deadlines=[EmbeddedDeadline(title="Test & Admission Form Portal Open Date", deadline_date="18 September, 2025, Thursday"),EmbeddedDeadline(title="Test & Admission Form Portal Close Date", deadline_date="25 September, 2025, Thursday"),EmbeddedDeadline(title="Last Date of Fee Deposit Final Merit List", deadline_date="13 October, 2025, Monday")]
    )

    # --- Insert into MongoDB ---
    insert_result = collection.insert_one(pu_data.dict())
    print(f"Inserted PU University document with ID: {insert_result.inserted_id}")
except Exception as e:
    print("Error inserting PU data:", e)


