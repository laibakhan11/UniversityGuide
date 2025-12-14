from pathlib import Path
import sys
from pydantic import BaseModel
sys.path.append(str(Path(__file__).resolve().parent.parent))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from config.db import get_universities_collection
from datetime import datetime
from typing import Optional
from pathlib import Path
import subprocess
import sys
from pathlib import Path
import os

app = FastAPI(title="University Guide API", version="1.0.0")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "University Guide API is running!", "docs": "/docs"}


@app.post("/api/scrape-all")
async def scrape_all_universities():
    try:
        # Get the backend directory (parent of app.py)
        backend_dir = Path(__file__).parent
        scraper_path = backend_dir / "scrapers" / "uni.py"
        
        print(f"Looking for scraper at: {scraper_path}")  # Debug log
        
        if not scraper_path.exists():
            return {
                "status": "error", 
                "message": f"Scraper not found at {scraper_path}"
            }
        
        result = subprocess.run(
            [sys.executable, str(scraper_path)],
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        
        return {
            "status": "success",
            "message": "All scrapers completed",
            "output": result.stdout,
            "errors": result.stderr if result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Scraping timeout (10 minutes)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# All universities - for homepage cards
@app.get("/api/universities")
def get_all_universities():
    collection = get_universities_collection()
    universities = []
    for uni in collection.find({}, {"shortName": 1, "name": 1, "fullName": 1, "location": 1}):
        universities.append({
            "shortName": uni.get("shortName") or uni.get("name", "Unknown"),
            "name": uni.get("name") or uni.get("fullName"),
            "fullName": uni.get("fullName") or uni.get("name"),
            "location": uni.get("location", "Pakistan")
        })
    return universities

# Single university - for university.html?name=UMT
@app.get("/api/university/{name}")
def get_university(name: str):
    collection = get_universities_collection()

    # Search by ANY of these fields (case-insensitive)
    uni = collection.find_one({
        "$or": [
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            {"shortName": {"$regex": f"^{name}$", "$options": "i"}},
            {"short_name": {"$regex": f"^{name}$", "$options": "i"}}
        ]
    })

    if not uni:
        return {"error": "University not found"}

    # Convert ObjectId to string so JSON works
    uni["_id"] = str(uni["_id"])
    return uni

'''
# Optional: Serve home.html directly
@app.get("/home")
async def serve_home():
    with open("../public/home.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())
'''

@app.get("/health")
async def health():
    return {"status": "healthy"}
    
@app.get("/api/cities/{city}")
def get_universities_by_city(city: str):
    collection = get_universities_collection()
    
    universities = []
    for uni in collection.find({"city": {"$regex": f"^{city}$", "$options": "i"}}):
        universities.append({
            "name": uni.get("name"),
            "full_name": uni.get("full_name"),
            "city": uni.get("city"),
            "address": uni.get("address", ""),
            "website": uni.get("website", ""),
            "total_programs": len(uni.get("programs", [])),
            "has_scholarships": len(uni.get("scholarships", [])) > 0
        })
    
    if not universities:
        return {"error": f"No universities found in {city}", "universities": []}
    
    return {
        "city": city,
        "count": len(universities),
        "universities": universities
    }


@app.get("/api/compare")
def compare_universities(uni1: str, uni2: str):
    collection = get_universities_collection()
    
    university1 = collection.find_one({
        "$or": [
            {"name": {"$regex": f"^{uni1}$", "$options": "i"}},
            {"shortName": {"$regex": f"^{uni1}$", "$options": "i"}}
        ]
    })
    
    university2 = collection.find_one({
        "$or": [
            {"name": {"$regex": f"^{uni2}$", "$options": "i"}},
            {"shortName": {"$regex": f"^{uni2}$", "$options": "i"}}
        ]
    })
    
    if not university1:
        return {"error": f"University '{uni1}' not found"}
    if not university2:
        return {"error": f"University '{uni2}' not found"}
    
    def get_fee_stats(programs):
        fees = [p.get("total_fee_first_year") for p in programs if p.get("total_fee_first_year")]
        if not fees:
            return {"min": 0, "max": 0, "avg": 0}
        return {
            "min": min(fees),
            "max": max(fees),
            "avg": round(sum(fees) / len(fees))
        }
    
    def get_departments(programs):
        depts = set()
        for p in programs:
            dept = p.get("department", "").strip()
            if dept:
                depts.add(dept)
        return sorted(list(depts))
    
    comparison = {
        "university1": {
            "name": university1.get("name"),
            "full_name": university1.get("full_name"),
            "city": university1.get("city"),
            "address": university1.get("address", ""),
            "website": university1.get("website", ""),
            "total_programs": len(university1.get("programs", [])),
            "departments": get_departments(university1.get("programs", [])),
            "fee_range": get_fee_stats(university1.get("programs", [])),
            "scholarships_count": len(university1.get("scholarships", [])),
            "upcoming_deadlines": len(university1.get("deadlines", []))
        },
        "university2": {
            "name": university2.get("name"),
            "full_name": university2.get("full_name"),
            "city": university2.get("city"),
            "address": university2.get("address", ""),
            "website": university2.get("website", ""),
            "total_programs": len(university2.get("programs", [])),
            "departments": get_departments(university2.get("programs", [])),
            "fee_range": get_fee_stats(university2.get("programs", [])),
            "scholarships_count": len(university2.get("scholarships", [])),
            "upcoming_deadlines": len(university2.get("deadlines", []))
        }
    }
    
    return comparison


@app.get("/api/search")
def search_all(q: str):
    if not q or len(q) < 2:
        return {"error": "Search query must be at least 2 characters", "results": []}
    
    collection = get_universities_collection()
    query_lower = q.lower()
    
    results = {
        "universities": [],
        "programs": [],
        "scholarships": [],
        "total_results": 0
    }
    
    for uni in collection.find():
        uni_name = uni.get("name", "")
        uni_full = uni.get("full_name", "")
        
        if query_lower in uni_name.lower() or query_lower in uni_full.lower():
            results["universities"].append({
                "name": uni_name,
                "full_name": uni_full,
                "city": uni.get("city"),
                "type": "university"
            })
        
        for program in uni.get("programs", []):
            prog_name = program.get("name", "")
            prog_dept = program.get("department", "")
            
            if query_lower in prog_name.lower() or query_lower in prog_dept.lower():
                results["programs"].append({
                    "name": prog_name,
                    "department": prog_dept,
                    "university": uni_name,
                    "fee": program.get("total_fee_first_year"),
                    "eligibility": program.get("eligibility", {}),
                    "type": "program"
                })
        
        for scholarship in uni.get("scholarships", []):
            scholar_name = scholarship.get("name", "")
            scholar_type = scholarship.get("type", "")
            
            if query_lower in scholar_name.lower() or query_lower in scholar_type.lower():
                results["scholarships"].append({
                    "name": scholar_name,
                    "type": scholar_type,
                    "university": uni_name,
                    "link": scholarship.get("link", ""),
                    "type_label": "scholarship"
                })
    
    results["universities"] = results["universities"][:10]
    results["programs"] = results["programs"][:30]
    results["scholarships"] = results["scholarships"][:15]
    
    results["total_results"] = (
        len(results["universities"]) + 
        len(results["programs"]) + 
        len(results["scholarships"])
    )
    
    return results


@app.get("/api/deadlines")
def get_all_deadlines():
    collection = get_universities_collection()
    
    all_deadlines = []
    
    for uni in collection.find():
        uni_name = uni.get("name", "Unknown")
        deadlines = uni.get("deadlines", [])
        
        for deadline in deadlines:
            all_deadlines.append({
                "university_name": uni_name,
                "title": deadline.get("title", ""),
                "deadline_date": deadline.get("deadline_date", ""),
                "university_city": uni.get("city", "")
            })
    
    all_deadlines.sort(key=lambda x: x.get("deadline_date", ""), reverse=True)
    
    return {
        "total_deadlines": len(all_deadlines),
        "deadlines": all_deadlines
    }

