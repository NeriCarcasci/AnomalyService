from fastapi import APIRouter, HTTPException, Depends
from models import TrainingDataRequest, DataPoint, FairnessRequest, ExplainabilityRequest
from services.anomaly_service import AnomalyService
from services.fairness_service import FairnessService
from services.explainability_service import ExplainabilityService
from services.auth_service import AuthService
from services.drift_service import DriftService
from services.accuracy_service import AccuracyService

router = APIRouter()

anomaly_service = AnomalyService()
fairness_service = FairnessService()
explainability_service = ExplainabilityService()
drift_service = DriftService()
accuracy_service = AccuracyService()

# ---------------------------------[ FAIRNESS ]---------------------------------
@router.post("/metrics/fairness/compute", dependencies=[Depends(AuthService.authenticate)])
def compute_fairness(request: FairnessRequest):
    return fairness_service.compute(request.predictions, request.actuals, request.sensitive_attribute)
# -----------------------------[ -- ---------- -- ]-----------------------------


# ---------------------------------[ ANOMALY ]----------------------------------
@router.post("/metrics/anomaly/fit", dependencies=[Depends(AuthService.authenticate)])
def fit_model(request: TrainingDataRequest):
    if not request.training_data:
        raise HTTPException(status_code=400, detail="Invalid training data format.")
    run_id = anomaly_service.fit(request.user_token, request.run_id, request.training_data)
    return {"message": "Model fitted and saved.", "run_id": run_id}

@router.post("/metrics/anomaly/detect", dependencies=[Depends(AuthService.authenticate)])
def detect_anomalies(request: DataPoint):
    result = anomaly_service.detect(request.user_token, request.run_id, request.values)
    if result is None:
        raise HTTPException(status_code=403, detail="Unauthorized or model not found.")
    return {"result": result}
# -----------------------------[ -- ---------- -- ]-----------------------------


# ------------------------------[ EXPLAINABILITY ]------------------------------
@router.post("/metrics/explainability/compute", dependencies=[Depends(AuthService.authenticate)])
def compute_explainability(request: ExplainabilityRequest):
    return explainability_service.compute(request.feature_importances)
# -----------------------------[ -- ---------- -- ]-----------------------------


# -----------------------------[ Common Endpoints ]-----------------------------
@router.delete("/metrics/delete/{user_token}/{run_id}", dependencies=[Depends(AuthService.authenticate)])
def delete_data(user_token: int, run_id: str):
    if not anomaly_service.delete_model(user_token, run_id):
        raise HTTPException(status_code=403, detail="Unauthorized or model not found.")
    return {"message": "Data successfully deleted."}
# -----------------------------[ -- ---------- -- ]-----------------------------