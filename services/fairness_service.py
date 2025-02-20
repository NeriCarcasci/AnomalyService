from metrics.fairness.fairness import FairnessMetric
from services.base_service import BaseService

class FairnessService(BaseService):
    def __init__(self):
        super().__init__()
        self.metric = FairnessMetric()

    def compute(self, predictions, actuals, sensitive_attribute):
        """Computes fairness metrics."""
        return "in production"