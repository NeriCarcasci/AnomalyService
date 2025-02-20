from metrics.explainability.explainability import AccuracyMetric
from services.base_service import BaseService

class AccuracyService(BaseService):
    def __init__(self):
        super().__init__()
        self.metric = AccuracyMetric()

    def compute(self, feature_importances):
        """Computes explainability metrics."""
        return "in production"