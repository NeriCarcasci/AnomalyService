""" 
        1. Accuracy: Measures the proportion of correctly classified instances.
           - Formula: 
             Accuracy = (TP + TN) / (TP + TN + FP + FN)
           - Why Accuracy?
             - Simple and effective when class distributions are balanced.
             - Can be misleading for imbalanced datasets.

        2. Precision: Measures how many predicted positives were actually positive.
           - Formula: 
             Precision = TP / (TP + FP)
           - Why Precision?
             - Important when false positives are costly (e.g., spam filters, medical tests).

        3. Recall (Sensitivity): Measures how many actual positives were correctly identified.
           - Formula: 
             Recall = TP / (TP + FN)
           - Why Recall?
             - Crucial when false negatives are costly (e.g., medical field: cancer diagnosis).

        4. F1-score: Harmonic mean of precision and recall.
           - Formula: 
             F1 = 2 * (Precision * Recall) / (Precision + Recall)
           - Why F1-score?
             - Helps in imbalanced datasets to avoid favoring one class.
 """


from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class AccuracyMetric:
    def calculate(self, y_true, y_pred):
        """Computes accuracy, precision, recall, and F1-score."""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="weighted"),
            "recall": recall_score(y_true, y_pred, average="weighted"),
            "f1_score": f1_score(y_true, y_pred, average="weighted"),
        }
