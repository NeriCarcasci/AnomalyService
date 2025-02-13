# Anomaly Detection Service

This repository contains a FastAPI-based anomaly detection service designed to process numerical data, identify anomalies, and track results for different users and runs.
## Features

- **Fit Models**: Compute statistical parameters (mean, standard deviation, and covariance) from the provided dataset, they are stored for each individual dummy token and run id `{request.user_token}_{run_id}.json`
- **Update Models**: Extend existing models with additional training data dynamically - this updates the parameters stored and adds new data.
- **Detect Anomalies**: Compute multiple anomaly metrics, including:
  - Z-score anomaly detection
  - Gaussian probability estimation
  - Normalized probability
  - Mahalanobis Distance 🔜
- **Track & Retrieve Results**:Store anomaly results and retrieve them later using their token and run ID.
- **Delete Stored Data**: Remove stored models and data for specific runs, mainly for clean up.

## API Endpoints

### Model Training
- `POST /fit`: Train a new model using numerical data.

### Model Updating
- `POST /update-model`: Add new data to an existing model.

### Anomaly Detection
- `POST /detect-anomalies`: Analyze a new data point and compute anomaly metrics.

### Data Management
- `GET /get-tracked-anomalies/{user_token}/{run_id}`: Retrieve stored anomaly data.
- `DELETE /delete-data/{user_token}/{run_id}`: Delete stored model and data.

## Deployment walkthrough

### Local run
1. Clone the repository and install dependencies:
   ```bash
   git clone github.com/NeriCarcasci/AnomalyService
   cd AnomalyService
   pip install -r requirements.txt
   ```
2. Run the FastAPI service:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### OpenShift deployment
1. Build and push the container:
   ```bash
   podman build -t quay.io/<your-username>/anomaly-detection:latest .
   podman push quay.io/<your-username>/anomaly-detection:latest
   ```
2. Deploy the service in OpenShift: Apply the following in order `deployment.yaml`, `service.yaml`, and `route.yaml`. (change yaml to suit specific deployment - i.e. container image)
3. Access the service via the generated OpenShift route. `oc get routes -n anomaly-detection` or through --web

## Testing

To run local tests, use:
```bash
pytest tests/test_main.py -v
```

To run tests on the cloud deployment:
```bash
pytest tests/test_AnomalyDetection.py -v
```


if tests fail comment out testing functions, they are clearly the problem. 😎




`oc delete pod -l app=anomaly-detection -n anomaly-detection`
