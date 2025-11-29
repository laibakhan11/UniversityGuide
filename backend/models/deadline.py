from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Deadline(BaseModel):
    university_name: str
    title: str
    deadline_date: str  
    url: Optional[str] = ""  