# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
# Import your existing db helpers
from config.db import get_universities_collection

app = FastAPI(title="University Guide API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="../public"), name="static")

@app.get("/")
async def root():
    return {"message": "University Guide API is running!", "docs": "/docs"}

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

# Optional: Serve home.html directly
@app.get("/home")
async def serve_home():
    with open("../public/home.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())
    
@app.get("/api/deadlines")
def get_all_deadlines():
    db = get_db()
    deadlines = list(db.deadlines.find({}, {"_id": 0, "university_name": 1, "title": 1, "deadline_date": 1}))
    deadlines.sort(key=lambda x: x.get("deadline_date", ""), reverse=True)
    return {"deadlines": deadlines}