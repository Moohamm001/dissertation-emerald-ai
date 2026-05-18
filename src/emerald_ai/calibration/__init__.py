"""Post-hoc probability calibration + split-conformal prediction (proposal §5.10).

Public entry points:
    calibrate         — Platt / isotonic / temperature scaling on a held-out fold.
    SplitConformal    — marginal-coverage conformal prediction at a target alpha.
    MondrianConformal — class-conditional conformal coverage (diagnostic).

v0.4.1 framing:
    - Marginal coverage   = HEADLINE result (finite-sample exact at any N).
    - Class-conditional   = DIAGNOSTIC with explicit small-sample bootstrap CIs.
    - Interval width      = NOT a primary metric (measurement-precision
                            artefact at ~10 minority observations).
"""
from __future__ import annotations

from emerald_ai.calibration.calibrators import (
    CalibrationResult,
    calibrate,
    expected_calibration_error,
)
from emerald_ai.calibration.conformal import (
    MondrianConformal,
    SplitConformal,
    bootstrap_class_conditional_coverage,
)

__all__ = [
    "CalibrationResult",
    "calibrate",
    "expected_calibration_error",
    "SplitConformal",
    "MondrianConformal",
    "bootstrap_class_conditional_coverage",
]
