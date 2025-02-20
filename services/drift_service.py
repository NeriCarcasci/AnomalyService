from metrics.explainability.explainability import DriftMetric
from services.base_service import BaseService

class DriftService(BaseService):
    def __init__(self):
        super().__init__()
        self.metric = DriftMetric()

    def compute(self, feature_importances):
        """Computes explainability metrics."""
        return "in production"