"""Counterfactual recourse (proposal §5.11).

Two implementations, with graceful degradation:

  * ``diverse_counterfactuals`` — proper multi-feature **DiCE** (Mothilal et
    al., 2020) counterfactuals when the ``dice-ml`` package is installed. DiCE
    optimises for *diversity* and *proximity* simultaneously, so the lending
    officer sees several genuinely different routes to approval rather than one
    minimal nudge.

  * ``nearest_counterfactual`` — a dependency-free greedy 1-D search for the
    smallest single-feature change that flips the decision. This is the robust
    default the API serves (low latency, never crashes) and the fallback when
    DiCE is unavailable.

The proposal's interpretation (proposal §5.11 + Wachter et al., 2017): a
counterfactual under GDPR Art. 22 should be (a) actionable, (b) sparse,
(c) plausible. The actionable-feature list enforces (a); the greedy scan
enforces (b); DiCE's proximity term and the data-derived feature ranges
support (c).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Counterfactual:
    feature: str
    original_value: float
    new_value: float
    delta: float
    original_prediction: float
    new_prediction: float
    flipped: bool


def nearest_counterfactual(
    model,
    x_row: np.ndarray,
    feature_names: list[str],
    *,
    actionable_features: list[str],
    feature_ranges: dict[str, tuple[float, float]] | None = None,
    n_steps: int = 50,
    target_class: int = 1,
    threshold: float = 0.5,
    minority_label: int = 0,
) -> Counterfactual | None:
    """Search each actionable feature for the smallest 1-D change that flips
    the decision toward ``target_class``.

    Returns the best (smallest |Δ|) flip found, or ``None`` if no actionable
    feature can flip the prediction within its configured range.
    """
    x = np.asarray(x_row, dtype=float).reshape(1, -1).copy()
    name_to_idx = {n: i for i, n in enumerate(feature_names)}

    proba0 = model.predict_proba(x)
    classes = model.classes_ if hasattr(model, "classes_") else np.array([0, 1])
    target_idx = int(np.where(classes == target_class)[0][0]) if target_class in classes else 1
    p0 = float(proba0[0, target_idx])
    if (target_class == 1 and p0 >= threshold) or (target_class == 0 and p0 < threshold):
        # Already on the target side — no recourse needed
        return Counterfactual(
            feature="__none__",
            original_value=float("nan"),
            new_value=float("nan"),
            delta=0.0,
            original_prediction=p0,
            new_prediction=p0,
            flipped=True,
        )

    best: Counterfactual | None = None
    for f in actionable_features:
        if f not in name_to_idx:
            continue
        idx = name_to_idx[f]
        orig = float(x[0, idx])
        if feature_ranges and f in feature_ranges:
            lo, hi = feature_ranges[f]
        else:
            lo, hi = orig - 3.0, orig + 3.0  # standardised-scale default
        sweep = np.linspace(lo, hi, n_steps)
        for v in sweep:
            x[0, idx] = v
            p = float(model.predict_proba(x)[0, target_idx])
            flipped = (p >= threshold) if target_class == 1 else (p < threshold)
            if flipped:
                cand = Counterfactual(
                    feature=f,
                    original_value=orig,
                    new_value=float(v),
                    delta=float(v - orig),
                    original_prediction=p0,
                    new_prediction=p,
                    flipped=True,
                )
                if best is None or abs(cand.delta) < abs(best.delta):
                    best = cand
                break
        # Restore the feature for the next iteration
        x[0, idx] = orig
    return best


@dataclass
class DiverseCounterfactuals:
    """A set of DiCE-style counterfactuals for one applicant.

    ``changes`` is a list of dicts mapping ``{feature: (original, new)}`` — one
    dict per alternative recourse. ``method`` records whether the diverse DiCE
    engine or the greedy fallback produced them.
    """

    original_prediction: float
    changes: list[dict[str, tuple[float, float]]] = field(default_factory=list)
    method: str = "greedy-fallback"


def diverse_counterfactuals(
    model,
    X_background,
    x_row: np.ndarray,
    feature_names: list[str],
    *,
    actionable_features: list[str],
    total_cfs: int = 3,
    target_class: int = 1,
    random_state: int = 0,
) -> DiverseCounterfactuals:
    """Generate several diverse counterfactuals with DiCE; fall back to greedy.

    Operates in the post-preprocessing (all-numeric) feature space. ``X_background``
    is a representative sample of that space — DiCE uses it to learn per-feature
    ranges so the suggested changes stay plausible.

    If ``dice-ml`` is not installed (or DiCE fails for this instance), returns a
    single greedy 1-D counterfactual wrapped in the same structure, with
    ``method='greedy-fallback'`` so callers can be honest about provenance.
    """
    x = np.asarray(x_row, dtype=float).reshape(-1)
    classes = getattr(model, "classes_", np.array([0, 1]))
    pos_idx = int(np.where(classes == 1)[0][0]) if 1 in classes else 1
    p0 = float(model.predict_proba(x.reshape(1, -1))[0, pos_idx])

    try:
        import dice_ml
        import pandas as pd

        Xb = (
            X_background.to_numpy()
            if hasattr(X_background, "to_numpy")
            else np.asarray(X_background, dtype=float)
        )
        bg = pd.DataFrame(Xb, columns=feature_names)
        bg["__target__"] = (model.predict_proba(Xb)[:, pos_idx] >= 0.5).astype(int)

        data = dice_ml.Data(
            dataframe=bg,
            continuous_features=list(feature_names),
            outcome_name="__target__",
        )
        dmodel = dice_ml.Model(model=model, backend="sklearn", model_type="classifier")
        engine = dice_ml.Dice(data, dmodel, method="random")

        query = pd.DataFrame([dict(zip(feature_names, x))])
        result = engine.generate_counterfactuals(
            query,
            total_CFs=total_cfs,
            desired_class=int(target_class),
            features_to_vary=[f for f in actionable_features if f in feature_names] or "all",
            random_seed=random_state,
        )
        cf_df = result.cf_examples_list[0].final_cfs_df
        changes: list[dict[str, tuple[float, float]]] = []
        for _, cf in cf_df.iterrows():
            diff: dict[str, tuple[float, float]] = {}
            for j, name in enumerate(feature_names):
                new_v = float(cf[name])
                if abs(new_v - x[j]) > 1e-9:
                    diff[name] = (float(x[j]), new_v)
            if diff:
                changes.append(diff)
        if changes:
            return DiverseCounterfactuals(original_prediction=p0, changes=changes, method="dice")
    except Exception:
        pass  # fall through to greedy

    greedy = nearest_counterfactual(
        model,
        x,
        feature_names,
        actionable_features=actionable_features,
        target_class=target_class,
    )
    changes = []
    if greedy is not None and greedy.feature != "__none__":
        changes = [{greedy.feature: (greedy.original_value, greedy.new_value)}]
    return DiverseCounterfactuals(original_prediction=p0, changes=changes, method="greedy-fallback")
