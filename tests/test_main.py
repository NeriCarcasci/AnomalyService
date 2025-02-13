import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

USER_TOKEN = 1234
RUN_ID = "test_run"

@pytest.fixture
def setup_model():
    """Fixture to fit a model before each test requiring an existing model."""
    client.post("/fit", json={
        "user_token": USER_TOKEN,
        "run_id": RUN_ID,
        "training_data": [[10, 20, 30], [15, 25, 35], [12, 22, 32]]
    })


def test_fit_model_with_empty_data():
    response = client.post("/fit", json={"user_token": USER_TOKEN, "training_data": []})
    assert response.status_code == 400
    assert "Invalid training data format" in response.json()["detail"]









    

# -------- Reasonably useless tests

# --------[1]--------- Deleting data

def test_update_model_no_existing(setup_model):
    response = client.post("/update-model", json={
        "user_token": 9999,
        "run_id": "non_existent",
        "training_data": [[1, 2, 3]]
    })
    assert response.status_code == 404
    assert "No fitted model found" in response.json()["detail"]


# --------[2]--------- Deleting data

def test_delete_data_found(setup_model):
    response = client.delete(f"/delete-data/{USER_TOKEN}/{RUN_ID}")
    assert response.status_code == 200
    assert "Data successfully deleted." in response.json()["message"]

def test_delete_data_not_found():
    response = client.delete(f"/delete-data/{USER_TOKEN}/non_existent")
    assert response.status_code == 404
    assert "No stored data found" in response.json()["detail"]