
import os
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print(" ERROR: Can't find MONGO_URI in .env file!")
    exit()

#Connect to MongoDB 
try:
    client = MongoClient(MONGO_URI)
    # Test if connection works
    client.admin.command('ping')
    print(" Connected to MongoDB successfully!")
except Exception as e:
    print(f" Connection failed: {e}")
    exit()

db = client['UniversityGuide']


universities_collection = db['Universities']
deadlines_collection = db['deadlines']


# Helper functions
def get_db():
    return db

def get_universities_collection():
    return universities_collection

def get_deadlines_collection():
    return deadlines_collection


if __name__ == "__main__":
    collections = db.list_collection_names()
    print(f" Collections in database: {collections}")
    uni_count = universities_collection.count_documents({})
    deadline_count = deadlines_collection.count_documents({})
    print(f"Universities in database: {uni_count}")
    print(f"Deadlines in database: {deadline_count}")
 