from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path so we can import from config folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our database connection
from config.db import get_universities_collection, get_deadlines_collection

# Create FastAPI app 
app = FastAPI(
    title="University Guide API",
    description="API for university information, deadlines, and programs",
    version="1.0.0"
)

# Allow frontend to talk to backend 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the University Guide API!"}



