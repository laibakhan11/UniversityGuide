from pydantic import BaseModel
from typing import List, Optional

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
    programs: List[Program] = []
    scholarships: List[Scholarship] = []
    deadlines: List[EmbeddedDeadline] = [] 