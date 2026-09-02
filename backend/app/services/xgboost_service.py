"""
CyberShield AI - XGBoost Inference Service

Loads the trained XGBoost model and provides
prediction functionality for the backend API.
"""

from pathlib import Path

import joblib
import numpy as np


# ------------------------------------------------------------------
# Model configuration
# ------------------------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "ai"
    / "models"
    / "saved"
    / "xgboost_baseline.joblib"
)


# Attack classes used by the trained model.
# These correspond to class IDs 0-14.

ATTACK_CLASSES = {
    0: "Benign",
    1: "Bot",
    2: "DDoS",
    3: "DoS GoldenEye",
    4: "DoS Hulk",
    5: "DoS Slowhttptest",
    6: "DoS slowloris",
    7: "FTP-Patator",
    8: "Heartbleed",
    9: "Infiltration",
    10: "PortScan",
    11: "SSH-Patator",
    12: "Web Attack - Brute Force",
    13: "Web Attack - Sql Injection",
    14: "Web Attack - XSS",
}
# ------------------------------------------------------------------
# XGBoost Service
# ------------------------------------------------------------------

class XGBoostService:

    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the trained XGBoost model."""

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"XGBoost model not found at: {MODEL_PATH}"
            )

        self.model = joblib.load(MODEL_PATH)

        print(
            f"XGBoost model loaded successfully "
            f"from: {MODEL_PATH}"
        )

    def predict(self, features):
        """
        Predict the attack class from 40 features.

        Parameters
        ----------
        features : list
            Exactly 40 numerical feature values.

        Returns
        -------
        dict
            Prediction result containing class,
            attack name and confidence.
        """

        if self.model is None:
            raise RuntimeError(
                "XGBoost model has not been loaded."
            )

        if len(features) != 40:
            raise ValueError(
                f"Expected 40 features, "
                f"but received {len(features)}."
            )

        # Convert input into model-compatible format.
        input_data = np.asarray(
            features,
            dtype=float
        ).reshape(1, -1)

        # Prediction.
        prediction = self.model.predict(input_data)

        predicted_class = int(prediction[0])

        # Confidence.
        probabilities = self.model.predict_proba(
            input_data
        )[0]

        confidence = float(
            np.max(probabilities)
        )

        attack_name = ATTACK_CLASSES.get(
            predicted_class,
            f"Unknown Attack ({predicted_class})"
        )

        return {
            "predicted_class": predicted_class,
            "attack_name": attack_name,
            "confidence": round(confidence, 4),
        }


# ------------------------------------------------------------------
# Shared service instance
# ------------------------------------------------------------------

xgboost_service = XGBoostService()