import numpy as np
import uuid
from scipy.stats import norm
from db import save_model, load_model

def fit_anomaly_model(user_token: int, run_id: str, training_data: list):
    data = np.array(training_data)
    metric_mean = np.mean(data, axis=0)
    metric_stds = np.std(data, axis=0, ddof=1)

    run_id = run_id if run_id else str(uuid.uuid4())[:8]
    model_data = {"means": metric_mean.tolist(), "stds": metric_stds.tolist(), "data_points": training_data}
    
    save_model(user_token, run_id, model_data)
    return run_id

def detect_anomaly(user_token: int, run_id: str, values: list):
    model_data = load_model(user_token, run_id)
    if not model_data:
        return None

    metric_mean = np.array(model_data["means"])
    metric_stds = np.array(model_data["stds"])
    x = np.array(values)

    if len(x) != len(metric_mean):
        return "Dimension mismatch"

    z_scores = np.where(metric_stds > 0, (x - metric_mean) / metric_stds, 0)
    anomaly_score_z = np.max(np.abs(z_scores))
    
    variance = np.square(metric_stds)
    probability_density = np.exp(-np.square(x - metric_mean) / (2 * variance)) / (np.sqrt(2 * np.pi * variance))
    anomaly_score_prob = np.min(probability_density)
    
    cov_matrix = np.cov(np.vstack([metric_mean, x]), rowvar=False)
    inv_cov_matrix = np.linalg.pinv(cov_matrix)
    diff = x - metric_mean
    mahalanobis_distance = np.sqrt(np.dot(np.dot(diff, inv_cov_matrix), diff.T))

    anomaly_detected = (anomaly_score_z > 3) or (anomaly_score_prob < 0.01) or (mahalanobis_distance > 3)
    
    return {
        "z_score_anomaly": float(anomaly_score_z),
        "gaussian_probability": float(anomaly_score_prob),
        "mahalanobis_distance": float(mahalanobis_distance),
        "anomaly_detected": bool(anomaly_detected)
    }

def compute_fairness(predictions, actuals, sensitive_attribute):
    group_0 = [p == a for p, a, s in zip(predictions, actuals, sensitive_attribute) if s == 0]
    group_1 = [p == a for p, a, s in zip(predictions, actuals, sensitive_attribute) if s == 1]
    disparity = abs(sum(group_0) / len(group_0) - sum(group_1) / len(group_1)) if group_0 and group_1 else None
    return {"disparity": disparity}

def compute_explainability(feature_importances):
    return {"importance_rank": sorted(enumerate(feature_importances), key=lambda x: -x[1])}
