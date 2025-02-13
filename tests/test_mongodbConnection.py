import os
import random
import time
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection string (update with your credentials)
MONGO_URI = "mongodb+srv://ncarcasc:<db_password>@maincluster.g70a1.mongodb.net/anomalydetection?retryWrites=true&w=majority&appName=maincluster"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["anomalydetection"]  # Database name
collection = db["test_collection"]  # Test collection

def create_random_document():
    """Generate a test document with random data."""
    return {
        "run_id": f"test_run_{random.randint(1000, 9999)}",
        "user_token": random.randint(1, 100),
        "timestamp": datetime.utcnow(),
        "data": [random.randint(0, 100) for _ in range(5)]
    }

def insert_document():
    """Insert a document into MongoDB."""
    doc = create_random_document()
    start_time = time.time()
    result = collection.insert_one(doc)
    end_time = time.time()
    
    print(f"✅ Inserted document with _id: {result.inserted_id} (Took {end_time - start_time:.3f}s)")
    return doc["run_id"]

def fetch_document(run_id):
    """Retrieve the inserted document from MongoDB."""
    start_time = time.time()
    doc = collection.find_one({"run_id": run_id})
    end_time = time.time()
    
    if doc:
        print(f"📌 Retrieved document (Took {end_time - start_time:.3f}s):\n{doc}")
    else:
        print("❌ No document found!")

if __name__ == "__main__":
    print("🔄 Testing MongoDB Atlas connection...")
    test_run_id = insert_document()
    fetch_document(test_run_id)