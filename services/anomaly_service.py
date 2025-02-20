from metrics.anomaly.anomaly import AnomalyDetector
from services.base_service import BaseService

class AnomalyService(BaseService):
    def __init__(self):
        super().__init__()
        self.detector = AnomalyDetector()

    def fit(self, user_token, run_id, training_data):
        """Fits an anomaly detection model and saves it."""
        model_data = self.detector.fit(training_data)
        run_id = run_id if run_id else self.generate_run_id()
        self.save_model(user_token, run_id, model_data)
        return run_id

    def detect(self, user_token, run_id, values):
        """Loads the model and performs anomaly detection."""
        model_data = self.authenticate_user(user_token, run_id)
        if model_data is None:
            return None

        return self.detector.detect(values, model_data)