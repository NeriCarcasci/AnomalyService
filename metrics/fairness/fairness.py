# - Disparate Impact: Measures if the model disproportionately favors or disadvantages one group.
# - Equalized Odds: Ensures that different demographic groups have similar true positive and false positive rates.
# - [SOON] Demographic Parity: Ensures that predictions are independent of sensitive attributes.
# - [SOON] Predictive Parity: Ensures that positive predictions are equally reliable across different groups.
# - [SOON] Statistical Parity Difference: Measures the difference in positive outcome rates between groups.

class FairnessMetric:
    def disparate_impact(self, predictions, sensitive_attribute):
        """
        Computes Disparate Impact, a measure of fairness in classification models.

        A model is considered fair if the probability of a positive prediction is similar across different groups.
        The 80% Rule states that the positive rate for the disadvantaged group should be at least 80% of 
        the advantaged group.

        Formula:
            DI = P(Ŷ = 1 | S = 1) / P(Ŷ = 1 | S = 0)

        Where:
            - P(Ŷ = 1 | S = 1) is the probability of a positive prediction for Group 1.
            - P(Ŷ = 1 | S = 0) is the probability of a positive prediction for Group 0.
            - If DI < 0.8, the model may be biased.

        Returns:
            A dictionary containing the disparate impact ratio.
        """
        group_0_prob = sum(1 for p, s in zip(predictions, sensitive_attribute) if p == 1 and s == 0) / max(1, sum(1 for s in sensitive_attribute if s == 0))
        group_1_prob = sum(1 for p, s in zip(predictions, sensitive_attribute) if p == 1 and s == 1) / max(1, sum(1 for s in sensitive_attribute if s == 1))
        
        di = group_1_prob / group_0_prob if group_0_prob > 0 else None
        return {"disparate_impact": di}

    def equalized_odds(self, predictions, actuals, sensitive_attribute):
        """
        Computes Equalized Odds, ensuring that different groups have similar true positive and false positive rates.

        Formula:
            True Positive Rate (TPR) = TP / (TP + FN)
            False Positive Rate (FPR) = FP / (FP + TN)

        A fair model should have minimal differences in TPR and FPR across groups.

        Returns:
            A dictionary containing the TPR and FPR differences between the two groups.
        """
        tpr_0 = sum(1 for p, a, s in zip(predictions, actuals, sensitive_attribute) if p == 1 and a == 1 and s == 0) / max(1, sum(1 for a, s in zip(actuals, sensitive_attribute) if a == 1 and s == 0))
        tpr_1 = sum(1 for p, a, s in zip(predictions, actuals, sensitive_attribute) if p == 1 and a == 1 and s == 1) / max(1, sum(1 for a, s in zip(actuals, sensitive_attribute) if a == 1 and s == 1))

        fpr_0 = sum(1 for p, a, s in zip(predictions, actuals, sensitive_attribute) if p == 1 and a == 0 and s == 0) / max(1, sum(1 for a, s in zip(actuals, sensitive_attribute) if a == 0 and s == 0))
        fpr_1 = sum(1 for p, a, s in zip(predictions, actuals, sensitive_attribute) if p == 1 and a == 0 and s == 1) / max(1, sum(1 for a, s in zip(actuals, sensitive_attribute) if a == 0 and s == 1))

        return {"TPR_difference": abs(tpr_0 - tpr_1), "FPR_difference": abs(fpr_0 - fpr_1)}
