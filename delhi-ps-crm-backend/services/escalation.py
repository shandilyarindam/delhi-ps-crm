"""ML-based escalation prediction using a trained GradientBoostingClassifier."""

import logging
import os
from typing import Optional

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# Valid status values
VALID_STATUSES = {"open", "assigned", "resolved", "escalated"}
# Valid urgency values
VALID_URGENCIES = {"low", "medium", "high", "critical"}
# Maximum reasonable cluster count
MAX_CLUSTER_COUNT = 1000

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
    # Input validation
    if not isinstance(status, str) or not status.strip():
        raise ValueError("Status must be a non-empty string")
    if not isinstance(urgency, str) or not urgency.strip():
        raise ValueError("Urgency must be a non-empty string")
    if not isinstance(cluster_count, int) or cluster_count < 0:
        raise ValueError("Cluster count must be a non-negative integer")
    
    # Sanitize and validate inputs
    s = status.strip().lower()
    if s not in VALID_STATUSES:
        logger.warning("Invalid status '%s', using 'open' as fallback", status)
        s = "open"
    
    u = urgency.strip().lower()
    if u not in VALID_URGENCIES:
        logger.warning("Invalid urgency '%s', using 'medium' as fallback", urgency)
        u = "medium"
    
    # Cap cluster count to reasonable maximum
    cluster_count = min(cluster_count, MAX_CLUSTER_COUNT)
    
    # Encode features
    status_encoded = 0 if s == "assigned" else 1
    urgency_encoded = {"low": 0, "medium": 1, "high": 2, "critical": 3}[u]

    try:
        X = np.array([[status_encoded, urgency_encoded, cluster_count]], dtype=float)
        pred = _load_model().predict(X)
        result = int(pred[0])
        
        # Validate prediction result
        if result not in (0, 1):
            logger.warning("Invalid prediction result %d, using 0", result)
            result = 0
        
        return result
    except Exception as exc:
        logger.exception("ML model prediction failed: %s", exc)
        # Return safe default (no escalation) on model failure
        return 0
