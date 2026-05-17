"""5×10 nested stratified cross-validation (proposal §5.9).

Outer 10-fold: estimates generalisation performance.
Inner  5-fold: drives hyperparameter optimisation.

Fold splits are seeded + persisted so all six model families train and evaluate
on identical splits — enabling paired statistical comparison (DeLong test for AUCs,
paired bootstrap for PR-AUC and calibration error).
"""
from __future__ import annotations
