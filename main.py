from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import uuid
import json
from scipy.stats import norm
from pymongo import MongoClient
import os

# ----------------------[ MongoDB Configuration ]----------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Use env variable or local MongoDB
client = MongoClient(MONGO_URI)
db = client["anomalydetection"]  # Database name
models_collection = db["models"]  # Collection to store models


# Initialize FastAPI app
app = FastAPI()

# ----------------------[ Data Models ]----------------------
class TrainingDataRequest(BaseModel):
    user_token: int
    run_id: str = None
    training_data: list[list[float]]

class DataPoint(BaseModel):
    user_token: int
    run_id: str
    values: list[float]

# ----------------------| MongoDB Model Handling |----------------------
def save_model(user_token: int, run_id: str, model_data: dict):
    """Save model to MongoDB with user access control."""
    try:
        models_collection.update_one(
            {"run_id": run_id},  # Find document by run_id
            {"$set": {"model_data": model_data}, "$addToSet": {"access": user_token}},  # Add user if not already in access
            upsert=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save model to MongoDB: {str(e)}")

def load_model(user_token: int, run_id: str) -> dict:
    """Load model from MongoDB with access control."""
    model = models_collection.find_one({"run_id": run_id, "access": user_token})  # Ensure user has access
    if not model:
        raise HTTPException(status_code=403, detail="Unauthorized or model not found.")
    return model["model_data"]

def delete_model(user_token: int, run_id: str):
    """Delete model from MongoDB (only if user has access)."""
    result = models_collection.delete_one({"run_id": run_id, "access": user_token})
    if result.deleted_count == 0:
        raise HTTPException(status_code=403, detail="Unauthorized or model not found.")

# ----------------------| API Endpoints |----------------------
@app.post("/fit")
def fit_model(request: TrainingDataRequest):
    """Fit an anomaly detection model and store it with access control."""
    if not request.training_data or not all(isinstance(row, list) and all(isinstance(val, (int, float)) for val in row) for row in request.training_data):
        raise HTTPException(status_code=400, detail="Invalid training data format.")

    data = np.array(request.training_data)
    metric_mean = np.mean(data, axis=0)
    metric_stds = np.std(data, axis=0, ddof=1)

    run_id = request.run_id if request.run_id else str(uuid.uuid4())[:8]

    model_data = {
        "means": metric_mean.tolist(),
        "stds": metric_stds.tolist(),
        "data_points": request.training_data
    }

    save_model(request.user_token, run_id, model_data)

    return {"message": "Model fitted and saved.", "run_id": run_id}

@app.post("/detect-anomalies")
def detect_anomalies(request: DataPoint):
    """Compute anomaly score for a given data point using stored models."""
    model_data = load_model(request.user_token, request.run_id)

    metric_mean = np.array(model_data["means"])
    metric_stds = np.array(model_data["stds"])

    if not request.values or not all(isinstance(val, (int, float)) for val in request.values):
        raise HTTPException(status_code=400, detail="Invalid input data format.")

    x = np.array(request.values)

    if len(x) != len(metric_mean):
        raise HTTPException(status_code=400, detail="Input data dimensions do not match training data.")

    # Compute Z-Score
    z_scores = (x - metric_mean) / metric_stds
    anomaly_score_z = np.max(np.abs(z_scores))

    # Compute Gaussian Probability
    prob = norm(metric_mean, metric_stds).pdf(x)
    anomaly_score_prob = np.min(prob)

    # Compute Normalized Probability
    normalized_probability = anomaly_score_prob / norm(metric_mean, metric_stds).pdf(metric_mean)

    # Determine if anomaly is detected
    anomaly_detected = (anomaly_score_z > 3) or (anomaly_score_prob < 0.01)

    return {"result": {
        "z_score_anomaly": float(anomaly_score_z),
        "gaussian_probability": float(anomaly_score_prob),
        "normalized_probability": float(normalized_probability),
        "anomaly_detected": bool(anomaly_detected)
    }}

@app.delete("/delete-data/{user_token}/{run_id}")
def delete_data(user_token: int, run_id: str):
    """Delete stored model and data for a given user and run ID (only if user has access)."""
    delete_model(user_token, run_id)
    return {"message": "Data successfully deleted."}