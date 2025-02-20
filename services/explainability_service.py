from metrics.explainability.explainability import ExplainabilityMetric
from services.base_service import BaseService

class ExplainabilityService(BaseService):
    def __init__(self):
        super().__init__()
        self.metric = ExplainabilityMetric()

    def compute(self, feature_importances):
        """Computes explainability metrics."""
        return "in production"