import pytest
import requests

# Cloud API Base URL
BASE_URL = "https://anomaly-detection-anomaly-detection.apps.rosa.u4j8k6a7r8e1b0z.pkym.p3.openshiftapps.com"

USER_TOKEN = 1234
RUN_ID = "cloud_test"

@pytest.fixture
def setup_cloud_model():
    """Fixture to fit a model on the cloud before testing and clean up afterward."""
    # Setup our model
    response = requests.post(f"{BASE_URL}/fit", json={
        "user_token": USER_TOKEN,
        "run_id": RUN_ID,
        "training_data": [[10, 20, 30], [15, 25, 35], [12, 22, 32]]
    })
    assert response.status_code == 200, f"Model fit failed: {response.text}"

    yield  # this is when tests will be run

    # We need to clean up files after we run tests
    delete_response = requests.delete(f"{BASE_URL}/delete-data/{USER_TOKEN}/{RUN_ID}")
    assert delete_response.status_code == 200, f"Data deletion failed: {delete_response.text}"


def test_fit_model_with_empty_data():
    response = requests.post(f"{BASE_URL}/fit", json={"user_token": USER_TOKEN, "training_data": []})
    assert response.status_code == 400
    assert "Invalid training data format" in response.json()["detail"]


def test_detect_anomalies_valid(setup_cloud_model):
    response = requests.post(f"{BASE_URL}/detect-anomalies", json={
        "user_token": USER_TOKEN,
        "run_id": RUN_ID,
        "values": [11, 21, 31]
    })
    assert response.status_code == 200, f"Detect failed: {response.text}"
    data = response.json()
    assert "result" in data
    assert "anomaly_detected" in data["result"]


def test_detect_anomalies_obvious_anomaly(setup_cloud_model):
    response = requests.post(f"{BASE_URL}/detect-anomalies", json={
        "user_token": USER_TOKEN,
        "run_id": RUN_ID,
        "values": [500, 600, 700]
    })
    assert response.status_code == 200, f"Detect failed: {response.text}"
    data = response.json()
    assert "result" in data
    assert data["result"]["anomaly_detected"] == True  


# ------------ B ------------
def test_detect_anomalies_nonexistent_model():
    response = requests.post(f"{BASE_URL}/detect-anomalies", json={
        "user_token": 9999,
        "run_id": "non_existent",
        "values": [10, 20, 30]
    })
    assert response.status_code == 404
    assert "No fitted model found" in response.json()["detail"]

def test_delete_data_not_found():
    response = requests.delete(f"{BASE_URL}/delete-data/{USER_TOKEN}/non_existent")
    assert response.status_code == 404
    assert "No stored data found" in response.json()["detail"]