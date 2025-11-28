from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class Contact(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class Program(BaseModel):
    name: str
    department: str
    duration: str
    fee_per_semester: int
    degree_type: str = "undergraduate"  # undergraduate, graduate, phd

class Announcement(BaseModel):
    title: str
    date: str
    url: str
    description: Optional[str] = ""
    scraped_at: datetime = Field(default_factory=datetime.now)

class University(BaseModel):
    name: str
    full_name: str
    website: str
    programs: List[Program] = []
    announcements: List[Announcement] = []
    contact: Optional[Contact] = None
    last_scraped: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Helper functions
def insert_university(db, uni: University):
    """Insert university to MongoDB"""
    if db.universities.find_one({"name": uni.name}):
        print(f"⚠️  {uni.name} already exists!")
        return None
    
    result = db.universities.insert_one(uni.model_dump())
    print(f"✅ Inserted {uni.name}")
    return result.inserted_id

def get_university(db, name: str):
    """Get university by name"""
    data = db.universities.find_one({"name": name})
    if data:
        return University(**data)
    return None

def get_all_universities(db):
    """Get all universities"""
    return [University(**uni) for uni in db.universities.find()]