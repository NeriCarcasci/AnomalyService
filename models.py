from pydantic import BaseModel
from typing import List, Optional

class TrainingDataRequest(BaseModel):
    user_token: int
    run_id: Optional[str] = None
    training_data: List[List[float]]

class DataPoint(BaseModel):
    user_token: int
    run_id: str
    values: List[float]

class FairnessRequest(BaseModel):
    predictions: List[int]
    actuals: List[int]
    sensitive_attribute: List[int]

class ExplainabilityRequest(BaseModel):
    feature_importances: List[float]
