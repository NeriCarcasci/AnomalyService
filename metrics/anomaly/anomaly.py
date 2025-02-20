"""
        Detects anomalies using three statistical methods:

        1. Z-score-based Anomaly Detection
           → Formula:
             Z = (x - μ) / σ
           - If |Z| > 3, the value is an anomaly.
        
        2. Gaussian Probability Density Function (PDF)
           → Formula:
             P(x) = (1 / sqrt(2πσ²)) * e^(-(x - μ)² / 2σ²)
           - If probability is very low, the point is an anomaly.

        3. Mahalanobis Distance (Multivariate Anomaly Detection)
           → Formula:
             D_M(x) = sqrt((x - μ)ᵀ S⁻¹ (x - μ))
           - Takes into account correlations between features.

        Why Use These Metrics?
        - Z-score is simple and fast for one-dimensional data.
        - Gaussian PDF provides statistical confidence.
        - Mahalanobis Distance is powerful in multivariate datasets.


         When to Use Euclidean Distance:
	•	Works well when all features are equally important.
	•	Suitable for low-dimensional, uncorrelated data.
	•	Fast to compute.

        Problems With Euclidean Distance in Anomaly Detection:
	•	Ignores feature correlations → If features are correlated, distances are misleading
	•	Doesn’t normalize feature scales → Features with larger ranges dominate the distance calculation.
        """
import numpy as np
from scipy.stats import norm

class AnomalyMetric:
    def fit(self, training_data):
        """Fits a simple Gaussian anomaly detection model."""
        data = np.array(training_data)
        return {
            "means": np.mean(data, axis=0).tolist(),
            "stds": np.std(data, axis=0, ddof=1).tolist(),
        }

    def detect(self, values, model_data):
        """Detects anomalies based on Gaussian probability."""
        metric_mean = np.array(model_data["means"])
        metric_stds = np.array(model_data["stds"])
        x = np.array(values)

        if len(x) != len(metric_mean):
            return "Dimension mismatch"

        # Compute Z-score anomaly detection
        z_scores = np.where(metric_stds > 0, (x - metric_mean) / metric_stds, 0)
        anomaly_score_z = np.max(np.abs(z_scores))

        # Gaussian probability
        variance = np.square(metric_stds)
        probability_density = np.exp(-np.square(x - metric_mean) / (2 * variance)) / (np.sqrt(2 * np.pi * variance))
        anomaly_score_prob = np.min(probability_density)

        # Mahalanobis distance
        cov_matrix = np.cov(np.vstack([metric_mean, x]), rowvar=False)
        inv_cov_matrix = np.linalg.pinv(cov_matrix)
        diff = x - metric_mean
        mahalanobis_distance = np.sqrt(np.dot(np.dot(diff, inv_cov_matrix), diff.T))

        # Define anomaly detection thresholds
        anomaly_detected = (anomaly_score_z > 3) or (anomaly_score_prob < 0.01) or (mahalanobis_distance > 3)

        return {
            "z_score_anomaly": float(anomaly_score_z),
            "gaussian_probability": float(anomaly_score_prob),
            "mahalanobis_distance": float(mahalanobis_distance),
            "anomaly_detected": bool(anomaly_detected)
        }