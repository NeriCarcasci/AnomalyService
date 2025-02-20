"""
        Kolmogorov-Smirnov (KS) test [best for continuous data]
        - KS measures the maximum absolute difference between cumulative distributions.
        - If p < 0.05, the distributions are statistically different.

        Formula:
        KS = sup_x | F1(x) - F2(x) |

        Jensen-Shannon (JS) divergence [best for discrete data]
        - which measures similarity between two probability distributions.

        Formula:
        JS(P || Q) = 1/2 KL(P || M) + 1/2 KL(Q || M)
"""

from scipy.stats import ks_2samp
import numpy as np

class DriftMetric:
    def check(self, baseline, new_data):
        """Uses Kolmogorov-Smirnov test to detect data drift."""
        p_values = [ks_2samp(baseline[:, i], new_data[:, i]).pvalue for i in range(baseline.shape[1])]
        drift_detected = any(p < 0.05 for p in p_values)
        return {"p_values": p_values, "drift_detected": drift_detected}