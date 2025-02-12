from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import csv
import os
import uuid
import json
from scipy.stats import norm

app = FastAPI()

class TrainingDataRequest(BaseModel):
    user_token: int
    run_id: str = None
    training_data: list[list[float]]

class DataPoint(BaseModel):
    user_token: int
    run_id: str
    values: list[float]



@app.post("/fit")
def fit_model(request: TrainingDataRequest):
    """
    Fit the anomaly detection model to training data and store separately for each user and run ID.
    """
    if not request.training_data or not all(isinstance(row, list) and all(isinstance(val, (int, float)) for val in row) for row in request.training_data):
        raise HTTPException(status_code=400, detail="Invalid training data format.")
    
    data = np.array(request.training_data)
    metric_mean = np.mean(data, axis=0)
    metric_stds = np.std(data, axis=0, ddof=1)
    metric_cov = np.cov(data, rowvar=False).tolist() if len(data) > 1 else None
    
    run_id = request.run_id if request.run_id else str(uuid.uuid4())[:8]
    filename = f"{request.user_token}_{run_id}.json"
    
    model_data = {
        "means": metric_mean.tolist(),
        "stds": metric_stds.tolist(),
        "cov": metric_cov,
        "data_points": request.training_data
    }
    
    with open(filename, "w") as file:
        json.dump(model_data, file)
    
    return {"message": "Model fitted and saved.", "run_id": run_id}

@app.post("/update-model")
def update_model(request: TrainingDataRequest):
    filename = f"{request.user_token}_{request.run_id}.json"
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="No fitted model found for the given user and run ID.")
    
    if not request.training_data or not all(
        isinstance(row, list) and all(isinstance(val, (int, float)) for val in row)
        for row in request.training_data
    ):
        raise HTTPException(status_code=400, detail="Invalid training data format.")

    with open(filename, "r") as file:
        model_data = json.load(file)

    existing_data = np.array(model_data["data_points"])
    new_data = np.array(request.training_data)
    combined_data = np.vstack((existing_data, new_data))

    metric_mean = np.mean(combined_data, axis=0)
    metric_stds = np.std(combined_data, axis=0, ddof=1)
    metric_cov = np.cov(combined_data, rowvar=False).tolist() if len(combined_data) > 1 else None

    model_data.update({
        "means": metric_mean.tolist(),
        "stds": metric_stds.tolist(),
        "cov": metric_cov,
        "data_points": combined_data.tolist()
    })

    with open(filename, "w") as file:
        json.dump(model_data, file)

    return {"message": "Model updated successfully."}

@app.post("/detect-anomalies")
def detect_anomalies(request: DataPoint):
    """
    Compute anomaly score for a given data point using stored models.
    """
    filename = f"{request.user_token}_{request.run_id}.json"
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="No fitted model found for the given user and run ID.")
    
    with open(filename, "r") as file:
        model_data = json.load(file)
    
    metric_mean = np.array(model_data["means"])
    metric_stds = np.array(model_data["stds"])
    metric_cov = np.array(model_data["cov"]) if model_data["cov"] else None
    
    if not request.values or not all(isinstance(val, (int, float)) for val in request.values):
        raise HTTPException(status_code=400, detail="Invalid input data format.")
    
    x = np.array(request.values)
    
    if len(x) != len(metric_mean):
        raise HTTPException(status_code=400, detail="Input data dimensions do not match training data.")
    
    """
        -------------------------| Metrics |---------------------------------
    """
    # Z Score 
    z_scores = (x - metric_mean) / metric_stds
    anomaly_score_z = np.max(np.abs(z_scores))
    
    # Gaussian Probability
    prob = norm(metric_mean, metric_stds).pdf(x)
    anomaly_score_prob = np.min(prob)
    
    # Mahalanobis Distance
    """
    if metric_cov is not None:
        inv_cov = np.linalg.inv(metric_cov)
        diff = model_data - metric_mean
        mahalanobis_distance = np.sqrt(diff @ inv_cov @ diff)
    else:
        mahalanobis_distance = float(anomaly_score_z)
    """
    
    # Normalised Probs - P() over P(u)
    normalized_probability = anomaly_score_prob / norm(metric_mean, metric_stds).pdf(metric_mean)
    

    # Sample anomaly estimate
    anomaly_detected = (anomaly_score_z > 3) or (anomaly_score_prob < 0.01) #or (mahalanobis_distance and mahalanobis_distance > 3)
    
    result = {
        "z_score_anomaly": anomaly_score_z,
        "gaussian_probability": anomaly_score_prob,
        #"mahalanobis_distance": mahalanobis_distance,
        "normalized_probability": normalized_probability,
        "anomaly_detected": anomaly_detected
    }
    
    return {"result": result}

@app.delete("/delete-data/{user_token}/{run_id}")
def delete_data(user_token: int, run_id: str):
    """
    Delete stored model and data for a given user and run ID.
    """
    filename = f"{user_token}_{run_id}.json"
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="No stored data found for the given user and run ID.")
    
    os.remove(filename)
    return {"message": "Data successfully deleted."}
