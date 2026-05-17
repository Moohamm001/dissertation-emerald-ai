#!/usr/bin/env bash
# scripts/reproduce.sh — re-run the full EMERALD-AI pipeline from raw data to scored test set.
#
# Target: ≤ 8 hours wall-clock on Google Colab Pro+ A100 + Warwick HPC CPU
# (proposal §5.16).
set -euo pipefail

cd "$(dirname "$0")/../.."

echo "▶ EMERALD-AI end-to-end reproduction pipeline"
echo "  ($(date --iso-8601=seconds))"

# 1. EDA + leakage audit
emerald eda
emerald preprocess

# 2. Train all model families (nested CV + Bayesian HPO)
emerald train --model all

# 3. Calibration + conformal intervals + metrics
emerald evaluate

# 4. Explainability stack + fidelity validation
emerald explain

# 5. Fairness + robustness + drift audit
emerald audit --axis all

echo "✓ Reproduction complete."
