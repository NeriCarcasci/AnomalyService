from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
models_collection = db[COLLECTION_NAME]

def save_model(user_token: int, run_id: str, model_data: dict):
    models_collection.update_one(
        {"run_id": run_id},
        {"$set": {"model_data": model_data}, "$addToSet": {"access": user_token}},
        upsert=True
    )

def load_model(user_token: int, run_id: str) -> dict:
    model = models_collection.find_one({"run_id": run_id, "access": user_token})
    if not model:
        return None
    return model["model_data"]

def delete_model(user_token: int, run_id: str):
    result = models_collection.delete_one({"run_id": run_id, "access": user_token})
    return result.deleted_count > 0
