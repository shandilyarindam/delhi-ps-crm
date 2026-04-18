"""ML-based escalation prediction using a trained GradientBoostingClassifier."""

import logging
import os
from typing import Optional

import joblib
import numpy as np

logger = logging.getLogger(__name__)

_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_MODEL_PATH = os.path.join(_BACKEND_ROOT, "models", "escalation_model.pkl")

_model: Optional[object] = None


def _load_model():
    """Load the escalation model from disk, caching it for subsequent calls."""
    global _model
    if _model is None:
        logger.info("Loading escalation model from %s", _MODEL_PATH)
        _model = joblib.load(_MODEL_PATH)
    return _model


def predict_escalation(status: str, urgency: str, cluster_count: int) -> int:
    """Predict whether a complaint should be escalated based on encoded features."""
    s = (status or "").strip().lower()
    status_encoded = 0 if s == "assigned" else 1

    u = (urgency or "").strip().lower()
    urgency_encoded = {"low": 0, "medium": 1, "high": 2, "critical": 3}.get(u, 1)

    X = np.array([[status_encoded, urgency_encoded, int(cluster_count)]], dtype=float)
    pred = _load_model().predict(X)
    return int(pred[0])
