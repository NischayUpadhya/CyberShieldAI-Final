"""
===============================================================================
File        : 09_xgboost.py
Project     : CyberShield AI
Description : Trains and evaluates an XGBoost baseline model for
              CICIDS2017 multi-class network intrusion detection.

Author      : Nischay Upadhya P
Version     : 1.0
===============================================================================
"""

import logging
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =============================================================================
# Configuration
# =============================================================================

RANDOM_STATE = 42

N_ESTIMATORS = 100
MAX_DEPTH = 8
LEARNING_RATE = 0.10

SUBSAMPLE = 0.8
COLSAMPLE_BYTREE = 0.8

N_JOBS = -1


# =============================================================================
# Main
# =============================================================================

def main():

    start_time = time.time()

    try:

        logging.info("Starting XGBoost training...")

        # =====================================================================
        # Paths
        # =====================================================================

        BASE_DIR = Path(__file__).resolve().parents[1]

        DATASET_DIR = BASE_DIR / "datasets" / "final"
        EVALUATION_DIR = BASE_DIR / "evaluation"
        MODEL_DIR = BASE_DIR / "models" / "saved"

        EVALUATION_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        MODEL_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        # =====================================================================
        # Dataset Paths
        # =====================================================================

        X_TRAIN_PATH = DATASET_DIR / "X_train.npy"
        Y_TRAIN_PATH = DATASET_DIR / "y_train.npy"

        X_VALIDATION_PATH = (
            DATASET_DIR / "X_validation.npy"
        )

        Y_VALIDATION_PATH = (
            DATASET_DIR / "y_validation.npy"
        )

        # =====================================================================
        # Load Training Data
        # =====================================================================

        logging.info("Loading training data...")

        X_train = np.load(
            X_TRAIN_PATH
        )

        y_train = np.load(
            Y_TRAIN_PATH
        )

        logging.info(
            f"Training data: {X_train.shape}"
        )

        # =====================================================================
        # Load Validation Data
        # =====================================================================

        logging.info("Loading validation data...")

        X_validation = np.load(
            X_VALIDATION_PATH
        )

        y_validation = np.load(
            Y_VALIDATION_PATH
        )

        logging.info(
            f"Validation data: {X_validation.shape}"
        )

        # =====================================================================
        # Create XGBoost Model
        # =====================================================================

        logging.info(
            "Creating XGBoost model..."
        )

        model = XGBClassifier(
            objective="multi:softprob",
            num_class=15,

            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            learning_rate=LEARNING_RATE,

            subsample=SUBSAMPLE,
            colsample_bytree=COLSAMPLE_BYTREE,

            tree_method="hist",

            eval_metric="mlogloss",

            random_state=RANDOM_STATE,
            n_jobs=N_JOBS,

            verbosity=1
        )

        # =====================================================================
        # Train
        # =====================================================================

        logging.info(
            "Training XGBoost..."
        )

        model.fit(
            X_train,
            y_train,

            eval_set=[
                (
                    X_validation,
                    y_validation
                )
            ],

            verbose=True
        )

        logging.info(
            "XGBoost training completed."
        )

        # =====================================================================
        # Validation Predictions
        # =====================================================================

        logging.info(
            "Generating validation predictions..."
        )

        y_pred = model.predict(
            X_validation
        )

        # =====================================================================
        # Metrics
        # =====================================================================

        accuracy = accuracy_score(
            y_validation,
            y_pred
        )

        macro_f1 = f1_score(
            y_validation,
            y_pred,
            average="macro",
            zero_division=0
        )

        weighted_f1 = f1_score(
            y_validation,
            y_pred,
            average="weighted",
            zero_division=0
        )

        report = classification_report(
            y_validation,
            y_pred,
            zero_division=0
        )

        # =====================================================================
        # Print Results
        # =====================================================================

        print("\n" + "=" * 80)
        print("XGBOOST VALIDATION RESULTS")
        print("=" * 80)

        print(
            f"Accuracy    : {accuracy:.4f}"
        )

        print(
            f"Macro F1    : {macro_f1:.4f}"
        )

        print(
            f"Weighted F1 : {weighted_f1:.4f}"
        )

        print("\nClassification Report")
        print("=" * 80)
        print(report)

        # =====================================================================
        # Save Model
        # =====================================================================

        model_path = (
            MODEL_DIR /
            "xgboost_baseline.joblib"
        )

        logging.info(
            "Saving XGBoost model..."
        )

        joblib.dump(
            model,
            model_path,
            compress=3
        )

        # =====================================================================
        # Save Metrics
        # =====================================================================

        metrics_path = (
            EVALUATION_DIR /
            "XGBoost_Metrics.txt"
        )

        with open(
            metrics_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("=" * 80 + "\n")
            f.write(
                "CYBERSHIELD AI - XGBOOST RESULTS\n"
            )
            f.write("=" * 80 + "\n\n")

            f.write(
                f"Training Samples : "
                f"{len(X_train):,}\n"
            )

            f.write(
                f"Validation Samples : "
                f"{len(X_validation):,}\n"
            )

            f.write(
                f"Features : "
                f"{X_train.shape[1]}\n"
            )

            f.write(
                f"Trees : "
                f"{N_ESTIMATORS}\n"
            )

            f.write(
                f"Max Depth : "
                f"{MAX_DEPTH}\n"
            )

            f.write(
                f"Learning Rate : "
                f"{LEARNING_RATE}\n\n"
            )

            f.write(
                f"Accuracy : "
                f"{accuracy:.6f}\n"
            )

            f.write(
                f"Macro F1 : "
                f"{macro_f1:.6f}\n"
            )

            f.write(
                f"Weighted F1 : "
                f"{weighted_f1:.6f}\n\n"
            )

            f.write(
                "Classification Report\n"
            )

            f.write(
                report
            )

        # =====================================================================
        # Execution Time
        # =====================================================================

        execution_time = (
            time.time() - start_time
        )

        print("\n" + "=" * 80)
        print("XGBOOST TRAINING COMPLETED")
        print("=" * 80)

        print(
            f"Accuracy    : "
            f"{accuracy:.4f}"
        )

        print(
            f"Macro F1    : "
            f"{macro_f1:.4f}"
        )

        print(
            f"Weighted F1 : "
            f"{weighted_f1:.4f}"
        )

        print(
            f"Execution Time : "
            f"{execution_time:.2f} seconds"
        )

        print("=" * 80)

        logging.info(
            f"Model saved to: {model_path}"
        )

    except Exception as e:

        logging.exception(
            f"Unexpected error: {e}"
        )


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()