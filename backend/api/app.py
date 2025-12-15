from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.db import get_universities_collection
from datetime import datetime
from typing import Optional, Dict, Any
import subprocess
import os
import re
from pydantic import BaseModel

# Import calculators from utils
from utils.aggregate_calculators import UNIVERSITY_CALCULATORS

app = FastAPI(title="University Guide API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ PYDANTIC MODELS ============

class AggregateRequest(BaseModel):
    university: str
    ssc_obtained: float
    ssc_total: float = 1100
    hssc_obtained: float
    hssc_total: float = 1100
    entry_test_obtained: float
    entry_test_total: float = 200
    is_engineering: bool = False
    additional_options: Optional[Dict[str, Any]] = None

# ============ HELPER FUNCTIONS ============

def parse_deadline_date(date_str):
    """Parse various date formats and return a datetime object."""
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip()
    
    # Remove weekday names
    date_str = re.sub(
        r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s*',
        '',
        date_str,
        flags=re.IGNORECASE
    )
    
    formats = [
        "%B %d, %Y", "%b %d, %Y", "%d-%m-%Y", "%d/%m/%Y",
        "%Y-%m-%d", "%m/%d/%Y", "%d %B %Y", "%d %b %Y",
    ]
    
    # Try extracting date range
    range_pattern = r'([A-Za-z]+)\s+(\d{1,2})\s*-\s*(\d{1,2}),?\s*(\d{4})'
    range_match = re.search(range_pattern, date_str)
    if range_match:
        month, day1, day2, year = range_match.groups()
        date_str = f"{month} {day2}, {year}"
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try extracting "Month Day, Year"
    month_day_year = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s*(\d{4})'
    match = re.search(month_day_year, date_str, re.IGNORECASE)
    if match:
        try:
            extracted = f"{match.group(1)} {match.group(2)}, {match.group(3)}"
            return datetime.strptime(extracted, "%B %d, %Y")
        except ValueError:
            pass
    
    return None

# ============ API ENDPOINTS ============

@app.get("/")
async def root():
    return {"message": "University Guide API is running!", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============ SCRAPER ENDPOINT ============

@app.post("/api/scrape-all")
async def scrape_all_universities():
    try:
        backend_dir = Path(__file__).parent
        scraper_path = backend_dir / "scrapers" / "uni.py"
        
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

# ============ AGGREGATE CALCULATOR ENDPOINTS ============

@app.get("/api/aggregate/universities")
def get_aggregate_universities():
    """Get list of universities with aggregate calculator support"""
    universities = []
    for code, data in UNIVERSITY_CALCULATORS.items():
        universities.append({
            "code": code,
            "name": data["name"],
            "formula": data["formula"],
            "has_options": len(data["options"]) > 0,
            "options": data["options"]
        })
    return {"universities": universities}

@app.post("/api/aggregate/calculate")
def calculate_aggregate(request: AggregateRequest):
    """Calculate aggregate for a university"""
    uni_code = request.university.upper().strip()
    
    if uni_code not in UNIVERSITY_CALCULATORS:
        raise HTTPException(status_code=404, detail=f"Calculator not available for {request.university}")
    
    calculator = UNIVERSITY_CALCULATORS[uni_code]["calculator"]
    
    try:
        result = calculator(
            request.ssc_obtained,
            request.ssc_total,
            request.hssc_obtained,
            request.hssc_total,
            request.entry_test_obtained,
            request.entry_test_total,
            is_engineering=request.is_engineering,
            additionalcategoryselected=request.additional_options or {},
            gap_years=request.additional_options.get('gap_years', 0) if request.additional_options else 0
        )
        
        if isinstance(result, dict) and "error" in result:
            return {"success": False, "error": result["error"], "aggregate": None}
        
        return {
            "success": True,
            "aggregate": result,
            "university": UNIVERSITY_CALCULATORS[uni_code]["name"],
            "formula": UNIVERSITY_CALCULATORS[uni_code]["formula"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ UNIVERSITY DATA ENDPOINTS ============

@app.get("/api/universities")
def get_all_universities():
    """Get all universities for homepage"""
    collection = get_universities_collection()
    universities = []

    for uni in collection.find({}, {"name": 1, "full_name": 1, "city": 1}):
        universities.append({
            "name": uni.get("name", "Unknown"),
            "full_name": uni.get("full_name", ""),
            "city": uni.get("city", "Pakistan")
        })

    return universities

@app.get("/api/university/{name}")
def get_university(name: str):
    """Get single university details"""
    collection = get_universities_collection()

    uni = collection.find_one({
        "$or": [
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            {"shortName": {"$regex": f"^{name}$", "$options": "i"}},
            {"short_name": {"$regex": f"^{name}$", "$options": "i"}}
        ]
    })

    if not uni:
        return {"error": "University not found"}

    uni["_id"] = str(uni["_id"])
    return uni

@app.get("/api/cities/{city}")
def get_universities_by_city(city: str):
    """Get universities in a specific city"""
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
    """Compare two universities"""
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
    """Search across universities, programs, and scholarships"""
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
    """Get all deadlines sorted by date"""
    collection = get_universities_collection()
    all_deadlines = []
    
    # Get current date at midnight for accurate comparison
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for uni in collection.find():
        uni_name = uni.get("name", "Unknown")
        deadlines = uni.get("deadlines", [])
        
        for deadline in deadlines:
            original_date_str = deadline.get("deadline_date", "")
            parsed_date = parse_deadline_date(original_date_str)
            
            # Only include deadlines that could be parsed successfully
            if parsed_date:
                # Set to end of day (23:59:59) for deadline comparison
                # This way, a deadline on "today" is still considered upcoming
                deadline_end_of_day = parsed_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                all_deadlines.append({
                    "university_name": uni_name,
                    "title": deadline.get("title", ""),
                    "deadline_date": original_date_str,
                    "parsed_date": parsed_date.strftime("%Y-%m-%d"),
                    "timestamp": parsed_date.timestamp(),
                    "university_city": uni.get("city", ""),
                    # A deadline is past if the end of that day has passed
                    "is_past": deadline_end_of_day < current_date
                })
    
    # Sort by timestamp (earliest first)
    all_deadlines.sort(key=lambda x: x.get("timestamp", 0))
    
    # Separate into upcoming and past
    upcoming_deadlines = [d for d in all_deadlines if not d.get("is_past", False)]
    past_deadlines = [d for d in all_deadlines if d.get("is_past", False)]
    past_deadlines.reverse()  # Most recent past deadlines first
    
    return {
        "total_deadlines": len(all_deadlines),
        "upcoming_count": len(upcoming_deadlines),
        "past_count": len(past_deadlines),
        "deadlines": upcoming_deadlines + past_deadlines,  # Upcoming first, then past
        "upcoming_deadlines": upcoming_deadlines,
        "past_deadlines": past_deadlines
    }