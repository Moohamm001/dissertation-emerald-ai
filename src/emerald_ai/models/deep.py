"""Tabular deep-learning models (proposal §5.8).

Two sklearn-compatible PyTorch classifiers so they drop straight into the
nested-CV harness alongside the GBDTs:

  * ``TorchMLP`` — a regularised multilayer perceptron (the standard deep
    tabular baseline).
  * ``FTTransformer`` — a compact Feature-Tokenizer Transformer
    (Gorishniy et al., 2021): each numeric feature is embedded into a token, a
    learnable [CLS] token is prepended, a Transformer encoder mixes them, and
    the [CLS] representation drives a linear head.

Both are gated on ``torch``: the factories raise a clear ImportError when it is
absent, so :func:`emerald_ai.models.available_models` simply skips them in a
minimal install. The preprocessing pipeline emits an all-numeric matrix, which
is exactly what the feature tokenizer expects.

Class imbalance (~0.36% defaults) is handled with a positive-class-weighted
BCE loss derived from the training split.

Reference: literature/papers/arik2021tabnet.md, gorishniy2021revisiting (FT-T).
"""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

from emerald_ai.config import MODEL


def _require_torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - exercised only without torch
        raise ImportError(
            "PyTorch is not installed. Install the deep-learning extra: "
            'pip install -e ".[dl]" (or `pip install torch`).'
        ) from exc
    import torch

    return torch


class _BaseTorchClassifier(ClassifierMixin, BaseEstimator):
    """Shared sklearn-compatible training loop for the torch tabular models.

    Subclasses implement ``_build_module(n_features)`` returning an nn.Module
    that maps (batch, n_features) -> (batch,) logits for P(Y=1).
    """

    def __init__(
        self,
        *,
        max_epochs: int = 60,
        batch_size: int = 256,
        lr: float = 1e-3,
        weight_decay: float = 1e-5,
        patience: int = 8,
        random_state: int = MODEL.random_seed,
    ) -> None:
        self.max_epochs = max_epochs
        self.batch_size = batch_size
        self.lr = lr
        self.weight_decay = weight_decay
        self.patience = patience
        self.random_state = random_state

    # -- subclass hook -----------------------------------------------------
    def _build_module(self, n_features: int):  # pragma: no cover - overridden
        raise NotImplementedError

    # -- sklearn API -------------------------------------------------------
    def fit(self, X, y):
        torch = _require_torch()
        rng = np.random.default_rng(self.random_state)
        torch.manual_seed(self.random_state)

        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y).astype(np.int64)
        self.classes_ = np.unique(y)
        self.n_features_in_ = X.shape[1]

        # Hold out a small validation slice for early stopping.
        n = len(X)
        idx = rng.permutation(n)
        n_val = max(1, int(0.15 * n))
        val_idx, tr_idx = idx[:n_val], idx[n_val:]
        Xt = torch.tensor(X[tr_idx])
        yt = torch.tensor(y[tr_idx], dtype=torch.float32)
        Xv = torch.tensor(X[val_idx])
        yv = torch.tensor(y[val_idx], dtype=torch.float32)

        pos = float((y[tr_idx] == 1).sum())
        neg = float((y[tr_idx] == 0).sum())
        pos_weight = torch.tensor([neg / max(pos, 1.0)], dtype=torch.float32)

        self.module_ = self._build_module(self.n_features_in_)
        opt = torch.optim.AdamW(
            self.module_.parameters(), lr=self.lr, weight_decay=self.weight_decay
        )
        loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

        best_val = float("inf")
        best_state = None
        bad = 0
        bs = self.batch_size
        for _epoch in range(self.max_epochs):
            self.module_.train()
            order = torch.randperm(len(Xt))
            for s in range(0, len(Xt), bs):
                b = order[s : s + bs]
                if len(b) < 2:  # BatchNorm needs >1 sample; skip a lone trailing row
                    continue
                opt.zero_grad()
                logits = self.module_(Xt[b]).reshape(-1)
                loss = loss_fn(logits, yt[b])
                loss.backward()
                opt.step()
            # validation
            self.module_.eval()
            with torch.no_grad():
                vlogits = self.module_(Xv).reshape(-1)
                vloss = float(loss_fn(vlogits, yv))
            if vloss < best_val - 1e-5:
                best_val = vloss
                best_state = {k: v.detach().clone() for k, v in self.module_.state_dict().items()}
                bad = 0
            else:
                bad += 1
                if bad >= self.patience:
                    break
        if best_state is not None:
            self.module_.load_state_dict(best_state)
        return self

    def predict_proba(self, X):
        torch = _require_torch()
        X = np.asarray(X, dtype=np.float32)
        self.module_.eval()
        with torch.no_grad():
            logits = self.module_(torch.tensor(X)).reshape(-1)
            p1 = torch.sigmoid(logits).numpy()
        return np.column_stack([1.0 - p1, p1])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


class TorchMLP(_BaseTorchClassifier):
    """A regularised MLP for tabular data."""

    def __init__(
        self,
        *,
        hidden: tuple[int, ...] = (256, 128),
        dropout: float = 0.2,
        max_epochs: int = 60,
        batch_size: int = 256,
        lr: float = 1e-3,
        weight_decay: float = 1e-5,
        patience: int = 8,
        random_state: int = MODEL.random_seed,
    ) -> None:
        super().__init__(
            max_epochs=max_epochs,
            batch_size=batch_size,
            lr=lr,
            weight_decay=weight_decay,
            patience=patience,
            random_state=random_state,
        )
        self.hidden = hidden
        self.dropout = dropout

    def _build_module(self, n_features: int):
        torch = _require_torch()
        import torch.nn as nn

        layers: list = []
        prev = n_features
        for h in self.hidden:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(self.dropout)]
            prev = h
        layers += [nn.Linear(prev, 1)]
        return nn.Sequential(*layers)


class FTTransformer(_BaseTorchClassifier):
    """Compact Feature-Tokenizer Transformer (Gorishniy et al., 2021)."""

    def __init__(
        self,
        *,
        d_token: int = 32,
        n_blocks: int = 3,
        n_heads: int = 4,
        dropout: float = 0.1,
        max_epochs: int = 60,
        batch_size: int = 256,
        lr: float = 1e-3,
        weight_decay: float = 1e-5,
        patience: int = 8,
        random_state: int = MODEL.random_seed,
    ) -> None:
        super().__init__(
            max_epochs=max_epochs,
            batch_size=batch_size,
            lr=lr,
            weight_decay=weight_decay,
            patience=patience,
            random_state=random_state,
        )
        self.d_token = d_token
        self.n_blocks = n_blocks
        self.n_heads = n_heads
        self.dropout = dropout

    def _build_module(self, n_features: int):
        torch = _require_torch()
        import torch.nn as nn

        d_token, n_heads, n_blocks, dropout = (
            self.d_token,
            self.n_heads,
            self.n_blocks,
            self.dropout,
        )

        class _FTT(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                # Per-feature numeric tokenizer: token = x_i * w_i + b_i
                self.weight = nn.Parameter(torch.empty(n_features, d_token))
                self.bias = nn.Parameter(torch.empty(n_features, d_token))
                self.cls = nn.Parameter(torch.empty(1, 1, d_token))
                nn.init.normal_(self.weight, std=0.02)
                nn.init.normal_(self.bias, std=0.02)
                nn.init.normal_(self.cls, std=0.02)
                enc = nn.TransformerEncoderLayer(
                    d_model=d_token,
                    nhead=n_heads,
                    dim_feedforward=d_token * 2,
                    dropout=dropout,
                    activation="gelu",
                    batch_first=True,
                )
                self.encoder = nn.TransformerEncoder(enc, num_layers=n_blocks)
                self.norm = nn.LayerNorm(d_token)
                self.head = nn.Linear(d_token, 1)

            def forward(self, x):  # x: (batch, n_features)
                tokens = x.unsqueeze(-1) * self.weight + self.bias  # (batch, n_features, d_token)
                cls = self.cls.expand(x.shape[0], -1, -1)  # (batch, 1, d_token)
                seq = torch.cat([cls, tokens], dim=1)
                out = self.encoder(seq)
                return self.head(self.norm(out[:, 0]))  # CLS representation

        return _FTT()


def make_mlp(*, random_state: int = MODEL.random_seed, **kwargs) -> TorchMLP:
    """Factory for the torch MLP (requires the [dl] extra)."""
    _require_torch()
    return TorchMLP(random_state=random_state, **kwargs)


def make_ft_transformer(*, random_state: int = MODEL.random_seed, **kwargs) -> FTTransformer:
    """Factory for the FT-Transformer (requires the [dl] extra)."""
    _require_torch()
    return FTTransformer(random_state=random_state, **kwargs)
