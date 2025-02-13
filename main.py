from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import uuid
import json
from scipy.stats import norm
from minio import Minio


# Initialize FastAPI app
app = FastAPI()

# MinIO Configuration
MINIO_CLIENT = Minio(
    "minio-service:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False  # Change to True if using TLS
)
BUCKET_NAME = "anomaly-models"

# -----------------------| Data Models |-----------------------
class TrainingDataRequest(BaseModel):
    user_token: int
    run_id: str = None
    training_data: list[list[float]]

class DataPoint(BaseModel):
    user_token: int
    run_id: str
    values: list[float]

# ----------------------| File Handling |----------------------
# Ensure minio is aliv
try:
    MINIO_CLIENT.list_buckets()
    print("- MinIO connection successful")
except Exception as e:
    print(f"- MinIO connection failed: {e}")
    raise RuntimeError("MinIO is unreachable! Make sure it is running.")
if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_NAME)

def save_model(user_token: int, run_id: str, model_data: dict):
    """Save model to MinIO."""
    object_name = f"{user_token}/{run_id}.json"
    json_data = json.dumps(model_data).encode("utf-8")
    try:
        MINIO_CLIENT.put_object(BUCKET_NAME, object_name, data=json_data, length=len(json_data), content_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save model to MinIO: {str(e)}")

def load_model(user_token: int, run_id: str) -> dict:
    """Load model from MinIO."""
    object_name = f"{user_token}/{run_id}.json"
    try:
        response = MINIO_CLIENT.get_object(BUCKET_NAME, object_name)
        model_data = json.loads(response.read().decode("utf-8"))  
        response.close()
        response.release_conn() 
        return model_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error loading model: {str(e)}")
    
def delete_model(user_token: int, run_id: str):
    """Delete model from MinIO."""
    object_name = f"{user_token}/{run_id}.json"
    try:
        MINIO_CLIENT.remove_object(BUCKET_NAME, object_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete model from MinIO: {str(e)}")
# -----------------------| API Endpoints |-----------------------

@app.post("/fit")
def fit_model(request: TrainingDataRequest):
    """Fit an anomaly detection model to training data and store it."""
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

    result = {
        "z_score_anomaly": float(anomaly_score_z),
        "gaussian_probability": float(anomaly_score_prob),
        "normalized_probability": float(normalized_probability),
        "anomaly_detected": bool(anomaly_detected)  
    }

    return {"result": result}

@app.delete("/delete-data/{user_token}/{run_id}")
def delete_data(user_token: int, run_id: str):
    """Delete stored model and data for a given user and run ID."""
    delete_model(user_token, run_id)
    return {"message": "Data successfully deleted."}